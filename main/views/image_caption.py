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

num_train_images = 6000
num_val_images = 1000

nltk.download('punkt')
caption_path = "../model/Flickr8k_dataset/captions.txt"
vocab_path = "../model/vocab.pkl"
word_threshold = 4
train_caption_path = "../model/resized_train/captions.txt"
val_caption_path = "../model/resized_val/captions.txt"
test_caption_path = "../model/resized_test/captions.txt"

class EncoderCNN(nn.Module):
    def __init__(self, embed_size):
        #Resnet-101
        super(EncoderCNN, self).__init__()
        resnet = models.resnet101(pretrained=True)
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.linear = nn.Linear(resnet.fc.in_features, embed_size) #output => input
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
        #captions
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
            hiddens, states = self.lstm(inputs, states) # hiddens: (batch_size, 1, hidden_size)
            outputs = self.linear(hiddens.squeeze(1)) # outputs: (batch_size, vocab_size)
            _, predicted = outputs.max(1) # predicted: (batch_size)
            sampled_indexes.append(predicted)
            inputs = self.embed(predicted) # inputs: (batch_size, embed_size)
            inputs = inputs.unsqueeze(1) # inputs: (batch_size, 1, embed_size)
        sampled_indexes = torch.stack(sampled_indexes, 1) # sampled_indexes: (batch_size, max_seq_length)
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

counter = Counter()

with open(caption_path, "r") as f:
    lines = sorted(f.readlines()[1:])
    for i in range(len(lines)):
        line = lines[i]
        if (i + 1) <= num_train_images * 5:
            output_caption = train_caption_path
        elif (i + 1) <= (num_train_images + num_val_images) * 5:
            output_caption = val_caption_path
        else:
            output_caption = test_caption_path
        index = line.find(",")
        caption = line[index + 1:]
        tokens = nltk.tokenize.word_tokenize(caption.lower())
        counter.update(tokens)
        with open(output_caption, "a") as output_caption_f:
            output_caption_f.write(line)

words = [word for word, cnt in counter.items() if cnt >= word_threshold]

vocab = Vocabulary()
vocab.add_word('<pad>')
vocab.add_word('<start>')
vocab.add_word('<end>')
vocab.add_word('<unk>')

for word in words:
    vocab.add_word(word)

with open(vocab_path, 'wb') as f:
    pickle.dump(vocab, f)


#------------------------------------------


def load_image(image_path, transform=None):
    res = request.urlopen(image_path).read()
    image = Image.open(BytesIO(res)).convert('RGB')
    image = image.resize([224, 224], Image.LANCZOS)

    if transform is not None:
        image = transform(image).unsqueeze(0)

    return image

image_path = "https://imgnews.pstatic.net/image/001/2022/04/28/PYH2022042817560001300_P4_20220428195711761.jpg?type=w647"#"../model/image.jpg"
encoder_path = "../model/encoder-7.ckpt"  # path for trained encoder
decoder_path = "../model/decoder-7.ckpt"  # path for trained decoder"
vocab_path = "../model/vocab.pkl"  # path for vocabulary wrappers

embed_size = 256  # dimension of word embedding vectors
hidden_size = 512  # dimension of lstm hidden states
num_layers = 1  # number of layers in lstm
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# image preprocessing
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])

# # Load vocabulary wrapper
with open(vocab_path, 'rb') as f:
    vocab = pickle.load(f)

# Build models
encoder = EncoderCNN(embed_size).eval()  # eval mode (batchnorm uses moving mean/variance)
decoder = DecoderRNN(embed_size, hidden_size, len(vocab), num_layers)
encoder = encoder.to(device)
decoder = decoder.to(device)

# Load trained model parameters
encoder.load_state_dict(torch.load(encoder_path, map_location=torch.device('cpu')))
decoder.load_state_dict(torch.load(decoder_path, map_location=torch.device('cpu')))

# Prepare image
image = load_image(image_path, transform)
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
print(sentence)




