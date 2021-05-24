'''
Created on 27 nov. 2019

@author: cmoulin
Classes for the factorial demo
ConsoleAgent -> receives the user input and display the result
FactAgent -> knows how to iterate for calculating n!
MultAgent -> knows calculating a * b
StoreAgt -> stores the values of n! for avoiding twice the same calculus
'''
from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage, requestBaseMessage, answerMessage
from agent_v2.utils import Publisher
from operation.task_module import Tasks
from agent_v2.service import serviceManager

from time import sleep
from concurrent import  futures
import random
from agent_v2.service import Service, serviceManager

class BaseAgent(EdgeBaseAgent):
    def __init__(self, name):
        EdgeBaseAgent.__init__(self, name)
        self.className = self.__class__.__name__
        
    def receive_message(self, msg: AgentMessage):
        action_list = Tasks.ACTIONS[self.className]
        filter_list = list(filter(lambda action: action['act_name'] == msg.Action, action_list))
        if filter_list:
            method_name = filter_list[0].get('act_method')
            try:
                method = getattr(self, method_name)
            except AttributeError:
                print("[ERROR method]",  method_name, "is nothing.")
            method(msg)

    def publishService(self,service_type, service_name, args):
        service = Service(service_type, service_name,self.className)
        if args != None:
            for key, value in args.items():
                service.addArgument(key,value)
        serviceManager.submitService(self.name,service)
    # gives the name of action corresponding to a strategy
    def filter_strategy(self,actions,strategy):
        f = lambda action: action.get('action_strategy') == strategy
        lstrategy = list(filter(f,actions))
        return lstrategy[0].get('act_name')
    
    def filter_args(self,service_type,service_name,arg_predicate):
        ll = serviceManager.lookupAgents(service_type,service_name)
        return list(filter(arg_predicate,ll))

       
class FactAgent(BaseAgent):

    def __init__(self, name, args = None):
        BaseAgent.__init__(self, name)
# for preparing the answers to the agent requesting the n! (console agent)
# dataSet is a dictionary with keys: 'waitingAnswerMessages', fact, current
        self.dataSet = {}
# id for messages (useful when several calculi could be asked in parallel)
        self.messageID = 0
        self.storeAgentName = None
# receive a message from mult. Verify if the calculus n! is finished
# else send a message for another product    
    def act_prod(self, msg:AgentMessage):
        taskID = msg.TaskID
        content = msg.getContent()
        print("\n",self.name,'receive >>>', content)
        current = self.dataSet[taskID]['current']
        current -= 1
        self.dataSet[taskID]['current'] = current
        if current > 1:
            self.select_mult_agent([int(content), current], taskID)
        else:
# send back the result and ask the result to be stored
            self.sendBackResult(taskID,content)
            number = self.dataSet[taskID]['fact']
            if self.storeAgentName != None:
                msg2Store = requestBaseMessage(self.name, "STORE", '', [number, content],self.storeAgentName)
                self.send_message(msg2Store)
# send back the result    
    def sendBackResult(self,tid,result):
        number = self.dataSet[tid]['fact']
        answerContent = '{}! = {}'.format(number, result)
        print("\n",self.name,':-->', answerContent)
        self.answer2Sender(tid,answerContent)

# ask the prepared answer complete it and send the result
    def answer2Sender(self, msgID, content): 
        msg = self.dataSet.get(msgID).get('waitingAnswerMessages')
        msg.setContent(content)
        self.send_message(msg)   
# receive a request for n!
# verify if it is possible or trivial        
    def act_fact(self, msg:AgentMessage):
        received = msg.getContent()
        print("\n",self.name,'receive >>>', received, '! to do')
        self.messageID += 1
        answer = answerMessage(self.name,msg)
        self.dataSet[self.messageID] = {}
        self.dataSet[self.messageID]['waitingAnswerMessages'] = answer       
        fact = int(received)
        if fact < 0:
            answerContent = "Nb must be >=0"
            self.answer2Sender(self.messageID,answerContent)
        else:
            if fact == 0 or fact == 1:
                answerContent = '{}! = {}'.format(self.fact, 1)
                self.answer2Sender(self.messageID,answerContent)
            else:
# ask to the store agent if the calculus has already been made
                if self.storeAgentName == None:
                    ll = serviceManager.lookupAgents('persistence', 'factorial')
                    if ll:
                        self.storeAgentName = ll[0].get('name')
                self.dataSet[self.messageID]['fact'] = fact
                if self.storeAgentName != None:    
                    storeMsg = requestBaseMessage(self.name,'IS_STORED','STORE',fact,self.storeAgentName)
                    storeMsg.TaskID = self.messageID
                    self.send_message(storeMsg)
                else:
                    self.ask_for_product(self.messageID)
                    
# send a message for a product               
    def ask_for_product(self, taskID):
        fact = self.dataSet[taskID]['fact']
        current = fact - 1
        self.dataSet[taskID]['current'] = current
        self.select_mult_agent([fact, current], taskID)
            
# choose a mult agent and send a message
    def select_mult_agent(self, content, taskID):
        p = lambda dictm: dictm['max'] >= content[0] and dictm['max'] >= content[1]
        llfilter = self.filter_args('operation', 'multiplication',p)
        nbMult = len(llfilter)
        if nbMult == 0:
            self.sendBackResult(taskID,'no answer possible')
            return
        else:
            row = 0
            if nbMult >= 2:
                row = random.randint(0, nbMult - 1)
        print('-----------', llfilter, row)
        name = llfilter[row].get('name')
        actions = llfilter[row].get('actions')
        actionName = self.filter_strategy(actions,'product')
        callBack = 'PRODUCT'
        msg2Send = requestBaseMessage(self.name, actionName, callBack, content, name)
        msg2Send.TaskID = taskID
        self.send_message(msg2Send)
# receives a message from the store agent. Detect if the calculus is necessary        
    def act_store(self, msg:AgentMessage):
        received = msg.getContent()
        taskID = msg.TaskID
        print("\n",self.name,'receive >>>', received)
        if received[1] == 0:
            self.ask_for_product(taskID) 
        else:
            self.sendBackResult(msg.TaskID,received[1])
            
    
        
class MultAgent(BaseAgent):
    def __init__(self, name, args = None):
        BaseAgent.__init__(self, name)
        self.executor = futures.ThreadPoolExecutor(2)        
        self.publishService('operation', 'multiplication', args)
        
#     ACTIONS = {
#         'MULTIPLICATION' :     'act_mult'
#     }

# answer the product of two numbers               
    def act_mult(self, msg:AgentMessage):
        delay = random.randint(1, 50) / 10
        self.waker(msg, delay)
        
    def waker(self, msg:AgentMessage, delay):
        content = msg.getContent()
        print("\n",self.name,'receive >>>', content, 'Task:',msg.TaskID)
        total = int(content[0]) * int(content[1])
        print("\n",self.name,'result >>>', total)
        answer = answerMessage(self.name, msg)
        answer.setContent(total)
        print('{} sends result after {} sec delay'.format(self.name,delay))
        def task(n):
            sleep(n)
            self.send_message(answer)
        self.executor.submit(task, (delay))

class ConsoleAgent(BaseAgent):
    def __init__(self, name, args = None):
        #EdgeBaseAgent.__init__(self, name)
        BaseAgent.__init__(self, name)
        self.publishService('output', 'console', args)
        self.resultPublisher = Publisher()
    # useful for link with gui
    # the agent set the value in this publisher and 
    # external subscribers (example gui controller) will be
    # activated
        
#     ACTIONS = {
#         'CONSOLE' :     'act_console'
#     }
    
# set the parameter (n for n!) and send the request      
    def sendToMainAgent(self,content,to,action):
        description = "{} --> ask to {}: {}".format(self.name, to, content)
        print("\n",description)
        msg = requestBaseMessage(self.name, action, 'CONSOLE', content, to)
        self.send_message(msg)
        
# receive the result of a n! request, print it and put it in its publisher
# external suscribers of this publisher (GUI controller) will react       
    def act_console(self,msg:AgentMessage):
        content = msg.getContent()
        self.resultPublisher.setValue(content)
        print("\n",self.name,':-->', content)

# Store a n et n! value in a dictionary        
class StoreAgent(BaseAgent):
    def __init__(self, name, args = None):
        BaseAgent.__init__(self, name)
        self.publishService('persistence', 'factorial',args)
        self.storeDictionnary = {}
    
# receive a message for asking if a n! has already been calculated
# return the answer: a 0 value means no previous request for this number      
    def act_is_stored(self,msg:AgentMessage):
        ansMsg = answerMessage(self.name, msg)
        content = msg.getContent()
        print("\n",self.name,'--> asked for:', content)
        if content in self.storeDictionnary:
            result = self.storeDictionnary[content]
        else:
            result = 0
        ansMsg.setContent([content, result])
        self.send_message(ansMsg)
# receive a message asking to store a n and n! values     
    def act_store(self, msg:AgentMessage):
        content = msg.getContent() 
        print("\n",self.name,': asked to store -->', content)
        self.storeDictionnary[content[0]] = content[1] 
        print(self.storeDictionnary)     
        