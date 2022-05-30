from flask import Flask
from .views.scrapping import Scheduler
from .views.tts import TTS
from .views.translate import papagoAPI
from .views.image_caption import imgTotxt
from flask import request
from datetime import datetime
import os
import boto3
import json
import sys

app=Flask(__name__)

#스케줄링 시작
schedul=Scheduler()
#schedul.startScheduler()


#==============================================================================
s3 = boto3.client(
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


@app.route("/")
def home():
    data='''
    {
      "newsTitle": "힘들겠다",
      "newsURL": "www.naver.com"
    }
    '''
    res=app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return res

@app.route("/voice")
def doTTS():
    tmpTTS=TTS(1234,"안녕하세요")
    return tmpTTS.speak()

@app.route("/health-check")
def health_check():
    return "success"

@app.route("/translate")
def doTranslate():
    trans=papagoAPI("my name is seear")
    return trans.eNtokR()

@app.route("/gettxt", methods=['POST'])
def doCaption():
    print(request.data)
    params = json.loads(request.data, encoding='utf-8')
    if len(params) == 0:
        return 'No parameter'

    clscaption = imgTotxt()
    clscaption.setting_word()

    result=''
    for key in params.keys():
        trans = papagoAPI(clscaption.img_txt(params[key])).eNtokR()
        result += '{},{}<br>'.format(params[key], trans)

    return app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )

@app.route("/health-check")
def healthCheck():
    current_time = datetime.now()
    return  app.response_class(
        response={current_time},
        status=200,
        mimetype='application/json'
    )

#/health-check