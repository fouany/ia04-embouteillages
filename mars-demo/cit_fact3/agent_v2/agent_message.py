# -*- coding: utf-8 -*-

import calendar
import datetime
import json


class AgentMessage:
    """
    エージェントメッセージ構成クラス
    """
    def __init__(self, json_text=None):
        self.Name = ""
        self.Type = "INFORM"
        self.Date = 0
        self.From = ""
        self.To = ""
        self.Action = ""
        self.Args = {}
        self.Contents = None
        self.ContentLanguage = ""
        self.ErrorContents = ""
        self.Timeout = ""
        self.TimeLimit = ""
        self.Ack = ""
        self.Protocol = ""
        self.Strategy = ""
        self.ButFor = ""
        self.TaskID = ""
        self.ReplyTo = ""
        self.ReplyWith = ""
        self.RepeatCount = ""
        self.TaskTimeout = ""
        self.SenderIP = ""
        self.SenderSite = ""
        self.Thru = ""

        if json_text is not None:
            self.parse(json_text)



    def to_json(self):
        self.Date = self.generate_unix_time()
        
        # Output Filter
        f = ['Type', 'Date', 'From', 'To', 'TaskID', 'Action', 'Args', 'Contents','ReplyWith']
        d = {k : v for k, v in filter(lambda t: t[0] in f, self.__dict__.items())} # [TODO]
        return json.dumps(d)
    
    
    def validate(self):
        pass

    def generate_unix_time(self):
        now = datetime.datetime.utcnow()
        ut = calendar.timegm(now.utctimetuple())
        # print("Unix time : {0}".format(ut))
        return ut


    def parse(self, json_text):
        j = json.loads(json_text)
        for k, v in j.items():
            self.__dict__[k] = v

    def addReceiver(self,agentName):
        self.To.append(agentName)
        
    def getContent(self):
        return  self.Args["SENTENCE"]
    def setContent(self, content):
        self.Args["SENTENCE"] = content

# Prepare a message to be sent       
def requestBaseMessage(agent, task, replyWith, content, to):
    msg = AgentMessage()
    msg.Type = "REQUEST"
    msg.From = agent
    msg.To = to
    msg.Action = task
    msg.setContent(content)
    msg.ReplyWith = replyWith
    return msg

# prepare a message for answering       
def answerMessage(agent, input_message):
    msg = AgentMessage()
    msg.Type = "INFORM"
    msg.From = agent
    msg.To = input_message.From
    msg.Action = input_message.ReplyWith
    msg.TaskID = input_message.TaskID
    return msg     
if __name__ == "__main__":
    # for debug
    msg = AgentMessage()
    msg.addReceiver('agt1')
    msg.addReceiver('agt2')
    print(msg.to_json())

    json_sample = '{"Type": "", "Date": 1499368977, "From": "", "To": "", "Action": "", "Args": {"test-1": null}, "Contents": null}'
    t = msg.parse(json_sample)
    print(msg.__dict__)
    
