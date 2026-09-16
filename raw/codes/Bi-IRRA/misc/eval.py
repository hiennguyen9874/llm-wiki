import torch
import torch.nn.functional as F

from typing import Union, List
from misc.cclm_utils import MetricLogger, get_world_size, get_rank
import torch.distributed as dist
from misc.utils import is_master

@torch.no_grad()
def cclm_test(model, data_loader, tokenizer, config, is_tl=False):
    device = config.device
    model.eval()

    metric_logger = MetricLogger(delimiter="  ")
    header = 'Evaluation:'

    print('Computing features for evaluation...')

    texts = data_loader.dataset.text
    num_text = len(texts)
    text_bs = config.data.test_batch_size  # 256
    text_feats = []
    text_embeds = []
    text_atts = []
    for i in range(0, num_text, text_bs):
        text = texts[i: min(num_text, i + text_bs)]
        text_input = tokenizer(text, padding='max_length', truncation=True, max_length=config.experiment.text_length,
                               return_tensors="pt").to(device)

        text_feat = model.get_text_embeds(text_input.input_ids, text_input.attention_mask)
        text_embed = model.get_features(text_embeds=text_feat, is_tl=is_tl)

        text_embeds.append(text_embed)
        text_feats.append(text_feat)
        text_atts.append(text_input.attention_mask)

    text_embeds = torch.cat(text_embeds, dim=0)
    text_feats = torch.cat(text_feats, dim=0)
    text_atts = torch.cat(text_atts, dim=0)

    image_feats = []
    image_embeds = []
    for image in data_loader:
        image = image.to(device)

        image_feat, _ = model.get_vision_embeds(image)
        image_embed = model.get_features(image_embeds=image_feat)

        image_feats.append(image_feat)
        image_embeds.append(image_embed)

    image_feats = torch.cat(image_feats, dim=0)
    image_embeds = torch.cat(image_embeds, dim=0)

    sims_matrix = image_embeds @ text_embeds.t()

    num_tasks = get_world_size()
    rank = get_rank()

    sims_matrix = sims_matrix.t()
    score_matrix_t2i = torch.full((len(texts), len(data_loader.dataset.image)), -100.0).to(device)

    step = sims_matrix.size(0)//num_tasks + 1
    start = rank*step
    end = min(sims_matrix.size(0), start + step)

    for i, sims in enumerate(metric_logger.log_every(sims_matrix[start:end], 1000, header)):
        topk_sim, topk_idx = sims.topk(k=config.model.k_test, dim=0)
        encoder_output = image_feats[topk_idx]
        encoder_att = torch.ones(encoder_output.size()[:-1], dtype=torch.long).to(device)

        output = model.get_cross_embeds(image_embeds=encoder_output, image_atts=encoder_att,
                                        text_embeds=text_feats[start + i].repeat(config.model.k_test, 1, 1),
                                        text_atts=text_atts[start + i].repeat(config.model.k_test, 1))
        score = model.itm_head(output[:, 0, :])[:, 1]

        score_matrix_t2i[start + i, topk_idx] = score
    dist.barrier()
    torch.distributed.all_reduce(score_matrix_t2i, op=torch.distributed.ReduceOp.SUM)

    score_matrix_t2i = score_matrix_t2i.cpu().numpy()
    return score_matrix_t2i


@torch.no_grad()
def metric_eval(scores_t2i, img2person, txt2person, config):
    device = config.device
    scores_t2i = torch.Tensor(scores_t2i).to(device)
    img2person = img2person.to(device)
    txt2person = txt2person.to(device)

    index = torch.argsort(scores_t2i, dim=-1, descending=True)
    pred_person = img2person[index]
    matches = (txt2person.view(-1, 1).eq(pred_person)).long()

    def acc_k(matches, k=1):
        matches_k = matches[:, :k].sum(dim=-1)
        matches_k = torch.sum((matches_k > 0))
        return 100.0 * matches_k / matches.size(0)

    # Compute metrics
    ir1 = acc_k(matches, k=1).item()
    ir5 = acc_k(matches, k=5).item()
    ir10 = acc_k(matches, k=10).item()
    ir_mean = (ir1 + ir5 + ir10) / 3

    real_num = matches.sum(dim=-1)
    tmp_cmc = matches.cumsum(dim=-1).float()
    order = torch.arange(start=1, end=matches.size(1) + 1, dtype=torch.long).to(device)
    tmp_cmc /= order
    tmp_cmc *= matches
    AP = tmp_cmc.sum(dim=-1) / real_num
    mAP = AP.mean() * 100.0

    eval_result = {'r1': ir1,
                   'r5': ir5,
                   'r10': ir10,
                   'r_mean': ir_mean,
                   'mAP': mAP.item()
                   }

    return eval_result
