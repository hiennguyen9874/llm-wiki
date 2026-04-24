import json
import os
import re
from collections import defaultdict

from random import randint, shuffle
from random import random as rand

import torch
import copy
from PIL import Image
from PIL import ImageFile
from torch.utils.data import Dataset
from transformers import XLMRobertaTokenizer

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None


class ps_train_dataset(Dataset):
    def __init__(self, config, transform, split, max_words=30):
        self.config = config
        ann_root = config.anno_dir
        image_root = config.image_dir

        ann_file_sl = os.path.join(ann_root, split + '_reid_' + self.config.data.source_language + '.json')
        ann_file_tl = os.path.join(ann_root, split + '_reid_' + self.config.data.target_language + '.json')
        with open(ann_file_sl) as f:
            anns_sl = json.load(f)
        with open(ann_file_tl) as f:
            anns_tl = json.load(f)
        self.transform = transform
        self.person2text = defaultdict(list)
        person_id2idx = {}
        n = 0
        self.pairs = []

        # for MLM
        self.tokenizer = build_tokenizer(config['text_encoder'])
        self.add_eos = True  # always add eos

        self.cls_token = self.tokenizer.cls_token
        self.eos_token = self.tokenizer.sep_token
        self.pad_token_id = self.tokenizer.pad_token_id
        self.mask_token_id = self.tokenizer.mask_token_id

        self.mask_generator = TextMaskingGenerator(self.tokenizer, config.mlm.mask_prob,
                                                   config.mlm.max_masks, config.mlm.skipgram_prb,
                                                   config.mlm.skipgram_size, mask_whole_word=False)
        self.max_tokens = config.experiment.text_length
        self.max_masks = config.mlm.max_masks
        self.PAD_mask = -100  # loss will ignore this

        for index in range(len(anns_sl)):
            ann = anns_sl[index]
            image_path = os.path.join(image_root, ann['file_path'])
            person_id = ann['id']
            if person_id not in person_id2idx.keys():
                person_id2idx[person_id] = n
                n += 1
            person_idx = person_id2idx[person_id]

            ann_tl = anns_tl[index]
            for caption, caption_tl in zip(ann['captions'], ann_tl['captions']):
                caption = pre_caption(caption, max_words)
                caption_tl = pre_caption(caption_tl, max_words)
                self.pairs.append((image_path, caption, caption_tl, person_idx))
                self.person2text[person_idx].append(caption)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, caption, caption_tl, person = self.pairs[index]

        image_pil = Image.open(image_path)
        image = self.transform(image_pil.convert('RGB'))
        if self.config.mlm.is_mlm:
            text_ids, text_atts, text_ids_masked, masked_pos, masked_ids = self.preprocess(caption, True)
            text_ids_tl, text_atts_tl, text_ids_masked_tl, masked_pos_tl, masked_ids_tl = self.preprocess(
                caption_tl, True)
            return (image, text_ids, text_atts, text_ids_masked, masked_pos, masked_ids, text_ids_tl, text_atts_tl,
                    text_ids_masked_tl, masked_pos_tl, masked_ids_tl, person)
        else:
            text_ids, text_atts = self.preprocess(caption, False)
            text_ids_tl, text_atts_tl = self.preprocess(caption_tl, False)
            return image, text_ids, text_atts, text_ids_tl, text_atts_tl, person

    def preprocess(self, text, is_mlm):
        tokens = self.tokenizer.tokenize(text)

        tokens = [self.cls_token] + tokens[:self.max_tokens - 1]

        if self.add_eos:
            tokens = tokens[:self.max_tokens - 1]
            tokens += [self.eos_token]

        n_tokens = len(tokens)
        assert n_tokens >= 2, "len(word tokens) < 2"

        text_ids = self.tokenizer.convert_tokens_to_ids(tokens)  # list of int

        tokens_masked, masked_pos = self.mask_generator(copy.deepcopy(tokens))
        text_ids_masked = self.tokenizer.convert_tokens_to_ids(tokens_masked)  # list of int
        masked_ids = [text_ids[p] for p in masked_pos]

        # pad
        n_pad = self.max_tokens - n_tokens
        text_ids = text_ids + [self.pad_token_id] * n_pad
        text_atts = [1] * n_tokens + [0] * n_pad
        if not is_mlm:
            return text_ids, text_atts

        text_ids_masked = text_ids_masked + [self.pad_token_id] * n_pad
        n_pad = self.max_masks - len(masked_ids)
        masked_pos = masked_pos + [0] * n_pad
        masked_ids = masked_ids + [self.PAD_mask] * n_pad

        return text_ids, text_atts, text_ids_masked, masked_pos, masked_ids

    def collate_fn(self, batch):
        batch_tensors = []
        for x in zip(*batch):
            if x[0] is None:
                batch_tensors.append(None)
            elif isinstance(x[0], torch.Tensor):
                batch_tensors.append(torch.stack(x))
            else:
                batch_tensors.append(torch.tensor(x, dtype=torch.long))

        return batch_tensors


class ps_eval_dataset(Dataset):
    def __init__(self, config, transform, split, max_words=30, is_sl=True):
        if is_sl:
            self.language = config.data.source_language
        else:
            self.language = config.data.target_language
        ann_root = config.anno_dir
        image_root = config.image_dir
        ann_file = os.path.join(ann_root, split + '_reid_' + self.language + '.json')
        anns = json.load(open(ann_file, 'r'))
        self.transform = transform

        self.text = []
        self.image = []
        self.txt2person = []
        self.img2person = []

        for ann in anns:
            image_path = os.path.join(image_root, ann['file_path'])
            self.image.append(image_path)

            person_id = ann['id']
            self.img2person.append(person_id)

            caption_lst = ann['captions']
            for caption in caption_lst:
                self.text.append(pre_caption(caption, max_words))
                self.txt2person.append(person_id)

        self.txt2person = torch.tensor(self.txt2person, dtype=torch.long)
        self.img2person = torch.tensor(self.img2person, dtype=torch.long)

    def __len__(self):
        return len(self.image)

    def __getitem__(self, index):
        image_path = self.image[index]
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image)

        return image


def pre_caption(caption, max_words=50):
    caption = re.sub(
        r"([.!\"()*#:;~])",
        ' ',
        caption.lower(),
    )
    caption = re.sub(
        r"\s{2,}",
        ' ',
        caption,
    )
    caption = caption.rstrip('\n')
    caption = caption.strip(' ')

    # truncate caption
    caption_words = caption.split(' ')
    if len(caption_words) > max_words:
        caption = ' '.join(caption_words[:max_words])

    return caption


class TextMaskingGenerator:
    def __init__(self, tokenizer, mask_prob, mask_max, skipgram_prb=0.2, skipgram_size=3, mask_whole_word=True, use_roberta=False):
        self.id2token = {i: w for w, i in tokenizer.get_vocab().items()}

        self.use_roberta = use_roberta

        for i in range(len(self.id2token)):
            assert i in self.id2token.keys()  # check

        self.cls_token = tokenizer.cls_token
        self.mask_token = tokenizer.mask_token

        self.mask_max = mask_max
        self.mask_prob = mask_prob

        self.skipgram_prb = skipgram_prb
        self.skipgram_size = skipgram_size
        self.mask_whole_word = mask_whole_word

    def get_random_word(self):
        i = randint(0, len(self.id2token) - 1)
        return self.id2token[i]

    def __call__(self, tokens: list):  # tokens: [CLS] + ...
        n_pred = min(self.mask_max, max(
            1, int(round(len(tokens) * self.mask_prob))))

        # candidate positions of masked tokens
        assert tokens[0] == self.cls_token
        special_pos = {0}  # will not be masked
        cand_pos = list(range(1, len(tokens)))

        shuffle(cand_pos)
        masked_pos = set()
        max_cand_pos = max(cand_pos)
        for pos in cand_pos:
            if len(masked_pos) >= n_pred:
                break
            if pos in masked_pos:
                continue

            def _expand_whole_word(st, end):
                new_st, new_end = st, end

                if self.use_roberta:
                    while (new_st > 1) and (tokens[new_st][0] != 'Ġ'):
                        new_st -= 1
                    while (new_end < len(tokens)) and (tokens[new_end][0] != 'Ġ'):
                        new_end += 1
                else:
                    # bert, WordPiece
                    while (new_st >= 0) and tokens[new_st].startswith('##'):
                        new_st -= 1
                    while (new_end < len(tokens)) and tokens[new_end].startswith('##'):
                        new_end += 1

                return new_st, new_end

            if (self.skipgram_prb > 0) and (self.skipgram_size >= 2) and (rand() < self.skipgram_prb):
                # ngram
                cur_skipgram_size = randint(2, self.skipgram_size)
                if self.mask_whole_word:
                    st_pos, end_pos = _expand_whole_word(
                        pos, pos + cur_skipgram_size)
                else:
                    st_pos, end_pos = pos, pos + cur_skipgram_size
            else:
                if self.mask_whole_word:
                    st_pos, end_pos = _expand_whole_word(pos, pos + 1)
                else:
                    st_pos, end_pos = pos, pos + 1

            for mp in range(st_pos, end_pos):
                if (0 < mp <= max_cand_pos) and (mp not in special_pos):
                    masked_pos.add(mp)
                else:
                    break

        masked_pos = list(masked_pos)
        n_real_pred = len(masked_pos)
        if n_real_pred > n_pred:
            shuffle(masked_pos)
            masked_pos = masked_pos[:n_pred]

        for pos in masked_pos:
            if rand() < 0.8:  # 80%
                tokens[pos] = self.mask_token
            elif rand() < 0.5:  # 10%
                tokens[pos] = self.get_random_word()

        return tokens, masked_pos


def build_tokenizer(text_encoder: str):
    tokenizer = XLMRobertaTokenizer.from_pretrained(text_encoder)
    tokenizer.add_special_tokens({'bos_token': tokenizer.cls_token, 'eos_token': tokenizer.sep_token})
    return tokenizer


def pre_caption(caption, max_words=50):
    caption = re.sub(
        r"([.!\"()*#:;~])",
        ' ',
        caption.lower(),
    )
    caption = re.sub(
        r"\s{2,}",
        ' ',
        caption,
    )
    caption = caption.rstrip('\n')
    caption = caption.strip(' ')

    # truncate caption
    caption_words = caption.split(' ')
    if len(caption_words) > max_words:
        caption = ' '.join(caption_words[:max_words])

    return caption


class tsne_dataset(Dataset):
    def __init__(self, config, transform, split, max_words=30):
        self.config = config
        ann_root = config.anno_dir
        image_root = config.image_dir

        ann_file_sl = os.path.join(ann_root, split + '_reid_' + self.config.data.source_language + '.json')
        with open(ann_file_sl) as f:
            anns_sl = json.load(f)
        ann_file_tl = os.path.join(ann_root, split + '_reid_' + self.config.data.target_language + '.json')
        with open(ann_file_tl) as f:
            anns_tl = json.load(f)
        self.transform = transform
        self.person2text = defaultdict(list)
        person_id2idx = {}
        n = 0
        self.pairs = []

        # for MLM
        self.tokenizer = build_tokenizer(config['text_encoder'])
        self.add_eos = True  # always add eos

        self.cls_token = self.tokenizer.cls_token
        self.eos_token = self.tokenizer.sep_token
        self.pad_token_id = self.tokenizer.pad_token_id
        self.mask_token_id = self.tokenizer.mask_token_id
        self.max_tokens = config.experiment.text_length
        self.max_masks = config.mlm.max_masks
        self.PAD_mask = -100  # loss will ignore this

        for index in range(len(anns_sl)):
            ann = anns_sl[index]
            image_path = os.path.join(image_root, ann['file_path'])
            person_id = ann['id']
            if person_id not in person_id2idx.keys():
                person_id2idx[person_id] = n
                n += 1
            person_idx = person_id2idx[person_id]
            ann_tl = anns_tl[index]
            self.res = []
            for caption, caption_tl in zip(ann['captions'], ann_tl['captions']):
                caption = pre_caption(caption, max_words)
                caption_tl = pre_caption(caption_tl, max_words)
                self.pairs.append((image_path, caption, caption_tl, person_idx))
                self.person2text[person_idx].append(caption)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, caption, caption_tl, person = self.pairs[index]
        image_pil = Image.open(image_path)
        image = self.transform(image_pil.convert('RGB'))
        text_ids, text_atts = self.preprocess(caption, False)
        text_ids_tl, text_atts_tl = self.preprocess(caption_tl, False)
        return image, text_ids, text_atts, text_ids_tl, text_atts_tl, person

    def preprocess(self, text, is_mlm):
        tokens = self.tokenizer.tokenize(text)

        tokens = [self.cls_token] + tokens[:self.max_tokens - 1]

        if self.add_eos:
            tokens = tokens[:self.max_tokens - 1]
            tokens += [self.eos_token]

        n_tokens = len(tokens)
        assert n_tokens >= 2, "len(word tokens) < 2"

        text_ids = self.tokenizer.convert_tokens_to_ids(tokens)  # list of int
        # pad
        n_pad = self.max_tokens - n_tokens
        text_ids = text_ids + [self.pad_token_id] * n_pad
        text_atts = [1] * n_tokens + [0] * n_pad
        return text_ids, text_atts


    def collate_fn(self, batch):
        batch_tensors = []
        for x in zip(*batch):
            if x[0] is None:
                batch_tensors.append(None)
            elif isinstance(x[0], torch.Tensor):
                batch_tensors.append(torch.stack(x))
            else:
                batch_tensors.append(torch.tensor(x, dtype=torch.long))

        return batch_tensors