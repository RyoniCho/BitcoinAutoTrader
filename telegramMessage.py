import requests
import json
import time

class message:
    
    def __init__(self):
        self.token="==Telegram Bot Token=="
        self.my_chat_id="==Telegram Bot ChatID=="
        self.SetInfo()
        self.msgSet=set()
        self.exitPlag=False
        
        self.currentState=1
        self.exit=2
        self.exitYes=3
        self.bestKUpdate=4
        

    def SetInfo(self):
        if self.token=="==Telegram Bot Token==" or self.my_chat_id=="==Telegram Bot ChatID==":
            with open("./telegramKey.txt") as f:
                lines = f.readlines()
                self.token = lines[0].strip()
                self.my_chat_id=lines[1].strip()

        self.URL="https://api.telegram.org/bot{}/".format(self.token)

    def send_message(self,text):
        url = self.URL + "sendMessage?text={}&chat_id={}".format(text, self.my_chat_id)
        self.RequestTelegramBot(url)

    def RequestTelegramBot(self,url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        #print("Request Telegram: "+content)
        return content

    def GetUpdates(self):
        url = self.URL + "getUpdates"
        js = self.GetJsonResultFromRequest(url)
        return js

    def GetJsonResultFromRequest(self,url):
        content = self.RequestTelegramBot(url)
        js = json.loads(content)
        return js

    def get_last_chat_id_and_text(self,updates):
        num_updates = len(updates["result"])
        if num_updates<=0:
            return "null","0","0"

        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        message_id=updates["result"][last_update]["message"]["message_id"]
        return (text, chat_id,message_id)

    def CheckMessageInLoop(self):
        time.sleep(1)
        text, chat_id,msg_id = self.get_last_chat_id_and_text(self.GetUpdates())
        
        if msg_id in self.msgSet:
            return 0

        
        if text !="null":
            if "현재상태" in text:
                self.msgSet.add(msg_id)
                return self.currentState
            if "종료" in text:
                self.msgSet.add(msg_id)
                self.exitPlag=True
                return self.exit
            if "네" in text and self.exitPlag==True:
                self.msgSet.add(msg_id)
                return self.exitYes
            if "아니오" in text and self.exitPlag==True:
                self.msgSet.add(msg_id)
                self.exitPlag=False
                return 0
            if "K갱신" in text:
                self.msgSet.add(msg_id)
                return self.bestKUpdate
        return 0

            
