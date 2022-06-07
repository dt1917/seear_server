import torch
import torch.nn.functional as F
import numpy as np
import json
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import skimage.transform
import argparse
# from scipy.misc import imresize
import cv2
import urllib
from imageio import imread
import requests
from PIL import Image
from io import BytesIO
from skimage import io
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class imgTotxt:
    def __init__(self,img):
        self.caption = ""
        self.img = img
        self.model = os.path.join(os.getcwd(), 'BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar')
        self.word_map = os.path.join(os.getcwd(), 'WORDMAP_coco_5_cap_per_img_5_min_word_freq.json')
        self.ModelStart()

    def ModelStart(self):
        checkpoint = torch.load(self.model, map_location=str(device))
        decoder = checkpoint['decoder']
        decoder = decoder.to(device)
        decoder.eval()
        encoder = checkpoint['encoder']
        encoder = encoder.to(device)
        encoder.eval()

        with open(self.word_map, 'r') as j:
            word_map = json.load(j)
        rev_word_map = {v: k for k, v in word_map.items()}

        seq, alphas = self.caption_image_beam_search(encoder, decoder, self.img, word_map, 5)
        alphas = torch.FloatTensor(alphas)

        for i in seq:
            self.caption += rev_word_map[i] + " "

        startIndex = self.caption.find("<start>") + 8
        endIndex = self.caption.find("<end>")

        return self.caption[startIndex:endIndex]

    def caption_image_beam_search(self, encoder, decoder, image_path, word_map, beam_size=3):
        k = beam_size
        vocab_size = len(word_map)
        img = io.imread(image_path)
        if len(img.shape) == 2:
            img = img[:, :, np.newaxis]
            img = np.concatenate([img, img, img], axis=2)
        img = cv2.resize(src=img, dsize=(256,256))
        img = img.transpose(2, 0, 1)
        img = img / 255.
        img = torch.FloatTensor(img).to(device)
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                        std=[0.229, 0.224, 0.225])
        transform = transforms.Compose([normalize])
        image = transform(img)
        image = image.unsqueeze(0)
        encoder_out = encoder(image)
        enc_image_size = encoder_out.size(1)
        encoder_dim = encoder_out.size(3)
        encoder_out = encoder_out.view(1, -1, encoder_dim)
        num_pixels = encoder_out.size(1)
        encoder_out = encoder_out.expand(k, num_pixels, encoder_dim)
        k_prev_words = torch.LongTensor([[word_map['<start>']]] * k).to(device)
        seqs = k_prev_words
        top_k_scores = torch.zeros(k, 1).to(device)
        seqs_alpha = torch.ones(k, 1, enc_image_size, enc_image_size).to(device)
        complete_seqs = list()
        complete_seqs_alpha = list()
        complete_seqs_scores = list()

        step = 1
        h, c = decoder.init_hidden_state(encoder_out)

        while True:
            embeddings = decoder.embedding(k_prev_words).squeeze(1)
            awe, alpha = decoder.attention(encoder_out, h)
            alpha = alpha.view(-1, enc_image_size, enc_image_size)
            gate = decoder.sigmoid(decoder.f_beta(h))
            awe = gate * awe
            h, c = decoder.decode_step(torch.cat([embeddings, awe], dim=1), (h, c))
            scores = decoder.fc(h)
            scores = F.log_softmax(scores, dim=1)
            scores = top_k_scores.expand_as(scores) + scores
            if step == 1:
                top_k_scores, top_k_words = scores[0].topk(k, 0, True, True)
            else:
                top_k_scores, top_k_words = scores.view(-1).topk(k, 0, True, True)
            prev_word_inds = top_k_words / vocab_size
            next_word_inds = top_k_words % vocab_size
            seqs = torch.cat([seqs[prev_word_inds.long()], next_word_inds.unsqueeze(1)], dim=1)
            seqs_alpha = torch.cat([seqs_alpha[prev_word_inds.long()], alpha[prev_word_inds.long()].unsqueeze(1)],
                                dim=1)

            incomplete_inds = [ind for ind, next_word in enumerate(next_word_inds) if
                            next_word != word_map['<end>']]
            complete_inds = list(set(range(len(next_word_inds))) - set(incomplete_inds))

            if len(complete_inds) > 0:
                complete_seqs.extend(seqs[complete_inds].tolist())
                complete_seqs_alpha.extend(seqs_alpha[complete_inds].tolist())
                complete_seqs_scores.extend(top_k_scores[complete_inds])
            k -= len(complete_inds)
            if k == 0:
                break
            seqs = seqs[incomplete_inds]
            seqs_alpha = seqs_alpha[incomplete_inds]
            h = h[prev_word_inds[incomplete_inds].long()]
            c = c[prev_word_inds[incomplete_inds].long()]
            encoder_out = encoder_out[prev_word_inds[incomplete_inds].long()]
            top_k_scores = top_k_scores[incomplete_inds].unsqueeze(1)
            k_prev_words = next_word_inds[incomplete_inds].unsqueeze(1)
            if step > 50:
                break
            step += 1

        i = complete_seqs_scores.index(max(complete_seqs_scores))
        seq = complete_seqs[i]
        alphas = complete_seqs_alpha[i]

        return seq, alphas
