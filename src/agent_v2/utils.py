'''
Created on 4 déc. 2019

@author: cmoulin
'''
import json
from builtins import staticmethod
############ Publishers ##########################"
class Publisher:
    def __init__(self):
        self.subscribers = set()
        self.value = ''
        
    def register(self, who):
        self.subscribers.add(who)
    def unregister(self, who):
        self.subscribers.discard(who)
# Call the subscriber function 
    def dispatch(self, message):
        for subscriber in self.subscribers:
            subscriber(message)
    def setValue(self,value):
        self.value = value
        self.dispatch(self.value)
    def getValue(self):
        return self.value
'''
a ListPublisher encapsulates a list
subscriber functions may be registered and react when an event occurred in the list
for now only an add event is available produced when an element is added to the list 
'''    
class ListPublisher:
    def __init__(self):
        self.addingSubscribers = set()
        self.listValue = []
# register a subsriber
    def addingRegister(self, who):
        self.addingSubscribers.add(who)
# dispatch the message to all the addingSubscribers 
    def addDispatch(self, message):
        for subscriber in self.addingSubscribers:
            subscriber(message)
# add a value to the list and addDispatch it
    def addValue(self,value):
        self.listValue.append(value)
        self.addDispatch(value) 
    def getListValue(self):
        return self.listValue
    
################## JSON ############################        
class JsonUtil:
    @staticmethod
    def readFile(fileName):
        data = open(fileName,'r',encoding="utf-8").read() 
        return json.loads(data)
    @staticmethod
    def writeFile(fileName,structure):
        with open(fileName, 'w') as outfile:
            json.dump(structure, outfile)
    @staticmethod
    def toJson(structure):
        return json.dumps(structure)
    @staticmethod
    def toStructure(str_structure):
        return json.loads(str_structure)
