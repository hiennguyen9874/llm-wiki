import os
import random
import time
from pathlib import Path

import torch
import json
from misc.build import load_checkpoint, cosine_scheduler, build_optimizer
from misc.data import build_pedes_data
from misc.eval import cclm_test, metric_eval
from misc.utils import parse_config, init_distributed_mode, set_seed, is_master, is_using_distributed, \
    AverageMeter
# from model.tbps_model import clip_vitb
from transformers import XLMRobertaTokenizer
from misc.cclm_utils import get_rank


def convert_models_to_fp32(model):
    for p in model.parameters():
        p.data = p.data.float()
        if p.grad:
            p.grad.data = p.grad.data.float()


def build_tokenizer(text_encoder: str):
    tokenizer = XLMRobertaTokenizer.from_pretrained(text_encoder)
    tokenizer.add_special_tokens({'bos_token': tokenizer.cls_token, 'eos_token': tokenizer.sep_token})
    return tokenizer


def run(config):
    print(config)

    # data
    dataloader = build_pedes_data(config)
    train_loader = dataloader['train_loader']
    num_classes = len(train_loader.dataset.person2text)

    meters = {
        "loss": AverageMeter(),
        "loss_itc": AverageMeter(),
        "loss_sdm": AverageMeter(),
        "loss_itm": AverageMeter(),
        "loss_mlm": AverageMeter(),
        "loss_mim": AverageMeter(),
        "loss_id": AverageMeter(),
        "precision": AverageMeter(),
    }
    sl = config.data.source_language
    tl = config.data.target_language
    best_rank_1 = 0.0
    best_epoch = 0
    best_rank_1_tl = 0.0
    best_epoch_tl = 0

    from models.model_retrieval import Bi_IRRA
    model = Bi_IRRA(config=config, num_classes=num_classes)
    model.load_pretrained(config)
    model = model.to(config.device)
    tokenizer = build_tokenizer(config['text_encoder'])

    if is_using_distributed():
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[config.device],
                                                          find_unused_parameters=False)

    # schedule
    config.schedule.niter_per_ep = len(train_loader)
    lr_schedule = cosine_scheduler(config)

    # optimizer
    optimizer = build_optimizer(config, model)

    # train
    it = 0
    scaler = torch.cuda.amp.GradScaler()
    for epoch in range(config.schedule.epoch):

        if is_using_distributed():
            dataloader['train_sampler'].set_epoch(epoch)

        start_time = time.time()
        for meter in meters.values():
            meter.reset()
        model.train()

        for i, batch in enumerate(train_loader):
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_schedule[it] * param_group['ratio']

            with torch.autocast(device_type='cuda'):
                (image, text_ids, text_atts, text_ids_masked, masked_pos, masked_ids, text_ids_tl, text_atts_tl,
                 text_ids_masked_tl, masked_pos_tl, masked_ids_tl, idx) = None, None, None, None, None, None, None, None, None, None, None, None

                if config.mlm.is_mlm:
                    (image, text_ids, text_atts, text_ids_masked, masked_pos, masked_ids, text_ids_tl, text_atts_tl,
                        text_ids_masked_tl, masked_pos_tl, masked_ids_tl, idx) = batch
                else:
                    image, text_ids, text_atts, text_ids_tl, text_atts_tl, idx = batch
                ret = model(image, text_ids, text_atts, text_ids_tl, text_atts_tl,
                            text_ids_masked_sl=text_ids_masked, masked_pos_sl=masked_pos, masked_ids_sl=masked_ids,
                            text_ids_masked_tl=text_ids_masked_tl, masked_pos_tl=masked_pos_tl,
                            masked_ids_tl=masked_ids_tl, idx=idx)

                loss = sum([v for k, v in ret.items() if "loss" in k])

            batch_size = image.shape[0]
            meters['loss'].update(loss.item(), batch_size)
            meters['loss_itc'].update(ret.get('loss_itc', 0), batch_size)
            meters['loss_sdm'].update(ret.get('loss_sdm', 0), batch_size)
            meters['loss_itm'].update(ret.get('loss_itm', 0), batch_size)
            meters['loss_mlm'].update(ret.get('loss_mlm', 0), batch_size)
            meters['loss_mim'].update(ret.get('loss_mim', 0), batch_size)
            meters['loss_id'].update(ret.get('loss_id', 0), batch_size)
            meters['precision'].update(ret.get('precision', 0), batch_size)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            model.zero_grad()
            optimizer.zero_grad()
            it += 1

            if (i + 1) % config.log.print_period == 0:
                info_str = f"Epoch[{epoch + 1}] Iteration[{i + 1}/{len(train_loader)}]"
                # log loss
                for k, v in meters.items():
                    if v.val != 0:
                        info_str += f", {k}: {v.val:.4f}"
                info_str += f", Base Lr: {param_group['lr']:.2e}"
                print(info_str)

        i = 1
        end_time = time.time()
        time_per_batch = (end_time - start_time) / (i + 1)
        print("Epoch {} done. Time per batch: {:.3f}[s] Speed: {:.1f}[samples/s]"
              .format(epoch + 1, time_per_batch, train_loader.batch_size / time_per_batch))

        score_matrix_t2i = cclm_test(model.module, dataloader['test_loader'], tokenizer, config)
        score_matrix_t2i_tl = cclm_test(model.module, dataloader['test_loader_tl'], tokenizer, config, is_tl=True)
        if is_master():
            dataset = dataloader['test_loader'].dataset
            eval_result = metric_eval(score_matrix_t2i, dataset.img2person, dataset.txt2person, config)
            rank_1, rank_5, rank_10, map = eval_result['r1'], eval_result['r5'], eval_result['r10'], eval_result['mAP']
            print('{sl}: Acc@1 {top1:.5f} Acc@5 {top5:.5f} Acc@10 {top10:.5f} mAP {mAP:.5f}'
                  .format(sl=config.data.source_language, top1=rank_1, top5=rank_5, top10=rank_10, mAP=map))
            if best_rank_1 < rank_1:
                best_rank_1 = rank_1
                best_epoch = epoch

                save_obj = {
                    'state_dict': model.module.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'config': config,
                }
                torch.save(save_obj, os.path.join(config.model.saved_path, 'checkpoint_best_' + str(sl) + '.pth'))

            if score_matrix_t2i_tl is not None:
                dataset = dataloader['test_loader_tl'].dataset
                eval_result_tl = metric_eval(score_matrix_t2i_tl, dataset.img2person, dataset.txt2person, config)
                rank_1_tl, rank_5_tl, rank_10_tl, map_tl = (eval_result_tl['r1'], eval_result_tl['r5'],
                                                            eval_result_tl['r10'], eval_result_tl['mAP'])
                print('{tl}: Acc@1 {top1:.5f} Acc@5 {top5:.5f} Acc@10 {top10:.5f} mAP {mAP:.5f}'
                      .format(tl=config.data.target_language, top1=rank_1_tl, top5=rank_5_tl, top10=rank_10_tl,
                              mAP=map_tl))
                if best_rank_1_tl < rank_1_tl:
                    best_rank_1_tl = rank_1_tl
                    best_epoch_tl = epoch

                    save_obj = {
                        'state_dict': model.module.state_dict(),
                        'optimizer': optimizer.state_dict(),
                        'config': config,
                    }
                    torch.save(save_obj, os.path.join(config.model.saved_path, 'checkpoint_best_' + str(tl) + '.pth'))

            torch.cuda.empty_cache()

    print(f"{sl} best Acc@1: {best_rank_1} at epoch {best_epoch + 1}")
    print(f"{tl} best Acc@1: {best_rank_1_tl} at epoch {best_epoch_tl + 1}")


if __name__ == '__main__':
    config_path = 'config/config.yaml'
    config = parse_config(config_path)

    Path(config.model.saved_path).mkdir(parents=True, exist_ok=True)

    init_distributed_mode(config)

    set_seed(config)

    run(config)
