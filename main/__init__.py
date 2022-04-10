from flask import Flask
from .views.scrapping import Scheduler
from .views.tts import TTS
from .views.translate import papagoAPI
import json

app=Flask(__name__)

#스케줄링 시작
schedul=Scheduler()
#schedul.startScheduler()

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

@app.route("/translate")
def doTranslate():
    trans=papagoAPI("my name is seear")
    return trans.eNtokR()
