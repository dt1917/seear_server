from flask import Flask
from .views.Scraping import GetArticleData
from .views.Translate import Translate
from .views.ImageCaptioning import ImageCaptioning
from .views.GetModeltoS3 import GetModeltoS3
import json
from .views.Repository import Repository
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app=Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

GetModeltoS3().downloadModel()

def insertArticleData():
    repo = Repository()
    articles = GetArticleData()
    article = articles.getArticle
    repo.insertArticles(json.dumps(article, ensure_ascii=False))

sched=BackgroundScheduler(demon=True)
sched.add_job(insertArticleData, 'cron', minute='0')#매정각마다 실행
sched.start()

@app.route("/articles")
def main():
    repo = Repository()
    contents = repo.getArticles()
    res = app.response_class(
        response=contents,
        status=200,
        mimetype='application/json;charset=utf-8'
    )
    return res

@app.route("/pressses")
def getPress():
    repository = Repository()
    repository.insertPress()
    responseData = app.response_class(
        response="Complete",
        status=200,
        mimetype='application/json;charset=utf-8'
    )
    return responseData