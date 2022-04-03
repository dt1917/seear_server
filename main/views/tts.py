from gtts import gTTS
from config import config

class TTS:
    newsIdt=0
    newsTxt=""
    def __init__(self,newsIdt,newsTxt):
        self.newsIdt=newsIdt
        self.newsTxt=newsTxt

    def speak(self):
        try:
            tts = gTTS(text=self.newsTxt, lang='ko')
            filename = str(self.newsIdt)+'.mp3'
            tts.save(config.staticSound+filename)
            return config.staticSound+filename
        except:
            return 0;

