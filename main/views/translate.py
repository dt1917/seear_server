import os
import sys
import json
import urllib.request
#config ----------------------
with open('.env') as json_file:
    env_data = json.load(json_file)

client_id = env_data['client_id']
client_secret = env_data['client_secret']

class papagoAPI:
    target=""
    def __init__(self,target):
        self.target=target
    
    def setTarget(self,target):
        self.target=target
        
    def eNtokR(self):
        try:
            encText = urllib.parse.quote(self.target)
            data = "source=en&target=ko&text=" + encText
            url = "https://openapi.naver.com/v1/papago/n2mt"
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id",client_id)
            request.add_header("X-Naver-Client-Secret",client_secret)
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
            rescode = response.getcode()

            if(rescode==200):
                response_body = json.loads(response.read().decode('utf-8'))
                return response_body['message']['result']['translatedText']
            else:
                raise rescode
        except Exception as e:
            return e