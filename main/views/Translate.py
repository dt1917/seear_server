import json
import urllib.request
import os

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

class Translate:
    target=""
    def __init__(self,target):
        self.target=target

    def setTarget(self,target):
        self.target=target

    def englishTokorean(self):
        try:
            encText = urllib.parse.quote(self.target)
            data = "source=en&target=ko&text=" + encText
            url = "https://openapi.naver.com/v1/papago/n2mt"
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id",client_id)
            request.add_header("X-Naver-Client-Secret",client_secret)
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
            responseCode = response.getcode()

            if(responseCode==200):
                response_body = json.loads(response.read().decode('utf-8'))
                return response_body['message']['result']['translatedText']
            else:
                raise responseCode
        except Exception as e:
            return e