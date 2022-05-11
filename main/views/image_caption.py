import os.path
from io import BytesIO

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
import torchvision.models as models
from torch.nn.utils.rnn import pack_padded_sequence
import pickle
import nltk
from collections import Counter
from urllib import request
import config

nltk.download('punkt')

class EncoderCNN(nn.Module):
    def __init__(self, embed_size):
        # Resnet-101
        super(EncoderCNN, self).__init__()
        resnet = models.resnet101(pretrained=True)
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.linear = nn.Linear(resnet.fc.in_features, embed_size)  # output => input
        self.bn = nn.BatchNorm1d(embed_size, momentum=0.01)

    def forward(self, images):
        # feature vectors
        with torch.no_grad():
            features = self.resnet(images)
        features = features.reshape(features.size(0), -1)
        features = self.bn(self.linear(features))
        return features


class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers, max_seq_length=20):
        super(DecoderRNN, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)
        self.max_seg_length = max_seq_length

    def forward(self, features, captions, lengths):
        # captions
        embeddings = self.embed(captions)
        embeddings = torch.cat((features.unsqueeze(1), embeddings), 1)
        packed = pack_padded_sequence(embeddings, lengths, batch_first=True)
        hiddens, _ = self.lstm(packed)
        outputs = self.linear(hiddens[0])
        return outputs

    def sample(self, features, states=None):
        sampled_indexes = []
        inputs = features.unsqueeze(1)
        for i in range(self.max_seg_length):
            hiddens, states = self.lstm(inputs, states)  # hiddens: (batch_size, 1, hidden_size)
            outputs = self.linear(hiddens.squeeze(1))  # outputs: (batch_size, vocab_size)
            _, predicted = outputs.max(1)  # predicted: (batch_size)
            sampled_indexes.append(predicted)
            inputs = self.embed(predicted)  # inputs: (batch_size, embed_size)
            inputs = inputs.unsqueeze(1)  # inputs: (batch_size, 1, embed_size)
        sampled_indexes = torch.stack(sampled_indexes, 1)  # sampled_indexes: (batch_size, max_seq_length)
        return sampled_indexes


class Vocabulary(object):
    """Simple vocabulary wrapper."""

    def __init__(self):
        self.word2idx = {}
        self.idx2word = {}
        self.idx = 0

    def add_word(self, word):
        if not word in self.word2idx:
            self.word2idx[word] = self.idx
            self.idx2word[self.idx] = word
            self.idx += 1

    def __call__(self, word):
        if not word in self.word2idx:
            return self.word2idx['<unk>']
        return self.word2idx[word]

    def __len__(self):
        return len(self.word2idx)


class imgTotxt:
    adr = config.config.Model_DIR
    num_train_images = 6000
    num_val_images = 1000
    word_threshold = 4
    caption_path = os.path.join(adr, "Flickr8k_dataset/captions.txt")
    vocab_path = os.path.join(adr, "vocab.pkl")
    train_caption_path = os.path.join(adr, "resized_train/captions.txt")
    val_caption_path = os.path.join(adr, "resized_val/captions.txt")
    test_caption_path = os.path.join(adr, "resized_test/captions.txt")

    image_path = "https://static01.nyt.com/images/2022/05/09/world/09ukraine-putin-vid-cover-sub/09ukraine-putin-vid-cover-sub-videoLarge.jpg"  # "../model/image.jpg"
    encoder_path = os.path.join(adr, "encoder-7.ckpt")  # path for trained encoder
    decoder_path = os.path.join(adr, "decoder-7.ckpt")  # path for trained decoder"

    def __int__(self,adr,num_train_images,num_val_images,word_threshold,caption_path,vocab_path,train_caption_path,val_caption_path,test_caption_path,image_path,encoder_path,decoder_path):
        self.adr=adr
        self.num_train_images=num_train_images
        self.num_val_images=num_val_images
        self.word_threshold=word_threshold
        self.caption_path=caption_path
        self.vocab_path=vocab_path
        self.train_caption_path=train_caption_path
        self.val_caption_path=val_caption_path
        self.test_caption_path=test_caption_path
        self.image_path=image_path
        self.encoder_path=encoder_path
        self.decoder_path=decoder_path

    def setting_word(self):
        counter = Counter()

        with open(self.caption_path, "r") as f:
            lines = sorted(f.readlines()[1:])
            for i in range(len(lines)):
                line = lines[i]
                if (i + 1) <= self.num_train_images * 5:
                    output_caption = self.train_caption_path
                elif (i + 1) <= (self.num_train_images + self.num_val_images) * 5:
                    output_caption = self.val_caption_path
                else:
                    output_caption = self.test_caption_path
                index = line.find(",")
                caption = line[index + 1:]
                tokens = nltk.tokenize.word_tokenize(caption.lower())
                counter.update(tokens)
                with open(output_caption, "a") as output_caption_f:
                    output_caption_f.write(line)

        words = [word for word, cnt in counter.items() if cnt >= self.word_threshold]

        vocab = Vocabulary()
        vocab.add_word('<pad>')
        vocab.add_word('<start>')
        vocab.add_word('<end>')
        vocab.add_word('<unk>')

        for word in words:
            vocab.add_word(word)

        with open(self.vocab_path, 'wb') as f:
            pickle.dump(vocab, f)

    def load_image(self, image_path, transform=None):
        res = request.urlopen(image_path).read()
        image = Image.open(BytesIO(res)).convert('RGB')
        image = image.resize([224, 224], Image.LANCZOS)

        if transform is not None:
            image = transform(image).unsqueeze(0)

        return image

    def img_txt(self):
        embed_size = 256  # dimension of word embedding vectors
        hidden_size = 512  # dimension of lstm hidden states
        num_layers = 1  # number of layers in lstm
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # image preprocessing
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])

        with open(self.vocab_path, 'rb') as f:
            vocab = pickle.load(f)

        # Build models
        encoder = EncoderCNN(embed_size).eval()  # eval mode (batchnorm uses moving mean/variance)
        decoder = DecoderRNN(embed_size, hidden_size, len(vocab), num_layers)
        encoder = encoder.to(device)
        decoder = decoder.to(device)

        # Load trained model parameters
        encoder.load_state_dict(torch.load(self.encoder_path, map_location=torch.device('cpu')))
        decoder.load_state_dict(torch.load(self.decoder_path, map_location=torch.device('cpu')))

        # Prepare image
        image = self.load_image(self.image_path, transform)
        image_tensor = image.to(device)
        # Generate caption
        feature = encoder(image_tensor)
        sampled_ids = decoder.sample(feature)
        sampled_ids = sampled_ids[0].cpu().numpy()  # (1, max_seq_length) -> (max_seq_length)

        # Convert word_ids to words
        sampled_caption = []
        for word_id in sampled_ids:  # words_idx
            word = vocab.idx2word[word_id]  # words_idx to word
            sampled_caption.append(word)
            if word == '<end>':
                break
        sentence = ' '.join(sampled_caption)
        sentence=sentence.replace('<pad>','')
        sentence=sentence.replace('<start>','')
        sentence=sentence.replace('<end>','')
        sentence=sentence.replace('<unk>','')
        return sentence
