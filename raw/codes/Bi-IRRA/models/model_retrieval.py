import torch
import random
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
from models.xvlm import XVLMBase, XVLMPlusBase
from models.xvlm import QuickGELU, LayerNorm

class Bi_IRRA(XVLMBase):
    def __init__(self, config, num_classes=None):
        # Initialize the base XVLM model for parallel data
        super().__init__(config, num_classes=num_classes, load_vision_params=False, load_text_params=False,
                         use_contrastive_loss=True, use_matching_loss=True, use_mlm_loss=config.mlm.is_mlm,
                         use_bbox_loss=False)
        self.itm_weight = config.itm.weight
        self.mim_weight = config.mim.weight
        self.num_attention_heads = self.text_encoder.config.num_attention_heads
        self.init_params = []

    def forward(self, image, text_ids_sl, text_atts_sl, text_ids_tl, text_atts_tl, text_ids_masked_sl=None, masked_pos_sl=None,
                masked_ids_sl=None, text_ids_masked_tl=None, masked_pos_tl=None, masked_ids_tl=None, idx=None):
        ret = dict()
        # Get image and source language text embeddings
        image_embeds, image_atts = self.get_vision_embeds(image)
        text_embeds_sl = self.get_text_embeds(text_ids_sl, text_atts_sl)
        image_feat, text_feat_sl = self.get_features(image_embeds, text_embeds_sl)

        # Calculate contrastive and matching losses for source language
        loss_itc_sl = self.get_contrastive_loss(image_feat, text_feat_sl, idx=idx)
        loss_itm_sl = self.get_matching_loss(image_embeds, image_atts, image_feat, text_embeds_sl, text_atts_sl, text_feat_sl,
                                          idx=idx)

        # If using MIM or ITM mask, get masked image features
        if self.use_mim or self.itm_mask:
            image_embeds_mask, image_atts_mask = self.get_vision_embeds(image, is_mask=True)
            image_feat_mask = self.get_features(image_embeds_mask)

        # Get target language text embeddings and features
        text_embeds_tl = self.get_text_embeds(text_ids_tl, text_atts_tl)
        text_feat_tl = self.get_features(text_embeds=text_embeds_tl, is_tl=True)
        loss_itc_tl = self.get_contrastive_loss(image_feat, text_feat_tl, idx=idx)

        # Calculate matching loss for target language, using masked or unmasked image features
        if self.itm_mask:
            loss_itm_tl = self.get_matching_loss(image_embeds_mask, image_atts_mask, image_feat_mask, text_embeds_tl,
                                                 text_atts_tl, text_feat_tl, idx=idx)
        else:
            loss_itm_tl = self.get_matching_loss(image_embeds, image_atts, image_feat, text_embeds_tl,
                                                 text_atts_tl, text_feat_tl, idx=idx)
        # If using masked image modeling, calculate MIM loss
        if self.use_mim:
            with torch.no_grad():
                cross_embeds_sl = self.get_cross_embeds(text_embeds_sl, text_atts_sl, text_embeds=image_embeds,
                                                        text_atts=image_atts)
            cross_embeds_tl = self.get_cross_embeds(text_embeds_tl, text_atts_tl, text_embeds=image_embeds_mask,
                                                    text_atts=image_atts_mask)
            loss_d_mim = self.get_d_mim_loss(cross_embeds_sl, cross_embeds_tl)
            ret['loss_mim'] = loss_d_mim * self.mim_weight

        # If using masked language modeling, calculate MLM loss for both languages
        if self.use_mlm:
            loss_mlm_sl = self.get_mlm_loss(text_ids_masked_sl, text_atts_sl, image_embeds, image_atts, masked_pos_sl, masked_ids_sl)
            loss_mlm_tl = self.get_mlm_loss(text_ids_masked_tl, text_atts_tl, image_embeds, image_atts, masked_pos_tl,
                                            masked_ids_tl)
            ret['loss_mlm'] = loss_mlm_sl + loss_mlm_tl
        # Average the contrastive and matching losses from both languages
        ret['loss_itc'] = (loss_itc_sl + loss_itc_tl) * 0.5
        ret['loss_itm'] = (loss_itm_sl + loss_itm_tl) * 0.5 * self.itm_weight
        return ret
