from flask import Flask
from .views.scraping import GetArticleData
from .views.translate import papagoAPI
from .views.image_caption import imgTotxt
from flask import request
from datetime import datetime
import os
import boto3
import json
import sys
import torch
from .views.repository import Repository
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from flask import make_response

app=Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def insertArticleData():
    repo = Repository()
    articles = GetArticleData()
    article = articles.getArticle
    repo.insertArticles(json.dumps(article, ensure_ascii=False))

sched=BackgroundScheduler(demon=True)
sched.add_job(insertArticleData, 'cron', minute='0')#매정각마다 실행
sched.start()

#==============================================================================
'''s3 = boto3.client(
	's3',
	aws_access_key_id=os.environ.get("ACCESS_KEY_ID"),
	aws_secret_access_key=os.environ.get("SECRET_KEY"),
)

def download(s3_bucket, s3_object_key, local_file_name):
    meta_data = s3.head_object(Bucket=s3_bucket, Key=s3_object_key)
    total_length = int(meta_data.get('ContentLength', 0))
    downloaded = 0
    def progress(chunk):
        nonlocal downloaded
        downloaded += chunk
        done = int(50 * downloaded / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
        sys.stdout.flush()

    print(f'Downloading {s3_object_key}')
    with open(local_file_name, 'wb') as f:
        s3.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)
    print()

flicker = './main/model/Flickr8k_dataset/captions.txt'
testData = './main/model/resized_test/captions.txt'
trainData = './main/model/resized_train/captions.txt'
valData = './main/model/resized_val/captions.txt'
encoderFile = './main/model/encoder-7.ckpt'
decoderFile = './main/model/decoder-7.ckpt'
bucket="seear"

if not os.path.isfile(flicker):
    download(bucket, 'Flickr8k_dataset/captions.txt', flicker)
if not os.path.isfile(testData):
    s3.download_file(bucket, 'resized_test/captions.txt', testData)
if not os.path.isfile(trainData):
    s3.download_file(bucket, 'resized_train/captions.txt', trainData)
if not os.path.isfile(valData):
    s3.download_file(bucket, 'resized_val/captions.txt', valData)
if not os.path.isfile(encoderFile):
    s3.download_file(bucket, 'encoder-7.ckpt', encoderFile)
if not os.path.isfile(decoderFile):
    s3.download_file(bucket, 'decoder-7.ckpt', decoderFile)
#==============================================================================
'''
@app.route("/translate")
def doTranslate():
    trans=papagoAPI("my name is seear")
    return trans.eNtokR()

@app.route("/health-check")
def healthCheck():
    return app.response_class(
        response={"Hello"},
        status=200,
        mimetype='application/json'
    )

@app.route("/api/articles")
def main():
    repo=Repository()
    contents=repo.getArticles()
    res = app.response_class(
        response=contents,
        status=200,
        mimetype='application/json;charset=utf-8'
    )
    return res


@app.route("/api/test")
def apiTest():
    model=imgTotxt('d')
    print(model.ModelStart())

    res = app.response_class(
        response=json.dumps("{asdf:asdf}",ensure_ascii=False, indent=4),
        status=200,
        mimetype='application/json;charset=utf-8'
    )
    return res