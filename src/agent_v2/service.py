'''
Created on 5 déc. 2019

@author: cmoulin
'''
import configparser
import redis
from agent_v2.utils import JsonUtil

class Service:
    def __init__(self, service_type, service_name, agent_className):
        self.service_type = service_type
        self.service_name = service_name
        self.agent_className = agent_className
        self.args = {}
    def serviceTopic(self):
        return "{}-{}".format(self.service_type,self.service_name)
    
    def addArgument(self,arg_key,arg_value):
        self.args[arg_key] = arg_value
        
class ServiceManager:
    redis_port = 6379
    def __init__(self):
        self.load_settings()
        self.connect()
        
    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('edge_settings.ini')
        self.host = config['SETTINGS']['BrokerIP']
    
    def connect(self):
        self.redisClient = redis.StrictRedis(host=self.host, port=ServiceManager.redis_port, db=1,decode_responses=True )
     
    # --- services
            
    # --- Instance methods    
    def submitService(self,agentName, service:Service):
        act_list = Tasks.ACTIONS[service.agent_className]
        ll_actions = [{'act_name' : action.get('act_name'), 'action_strategy' : action.get('action_strategy')} for action in act_list]
        topic = service.serviceTopic()
        print('topic:',topic)
        service.addArgument('name',agentName)
        service.addArgument('actions', ll_actions)
        agentArgs = JsonUtil.toJson(service.args)    
        if not self.exist(topic):
            print('new key:',topic)
            self.redisClient.rpush(topic,agentArgs)
            print('agent',agentName,'added in:',topic)
        else: 
            if not self.lookup(topic, agentName):
                self.redisClient.rpush(topic,agentArgs)
                print('agent',agentName,'added in:',topic)
            else:
                print('agent',agentName,'already in:',topic)
                 
        self.printService(topic)
# look for a topic being registered
    def exist(self,topic):
        return len(self.redisClient.keys(pattern = topic)) != 0
# look for an agent being in the topic agent list
    def lookup(self,topic, agentName): 
        if not self.exist(topic):
            return False
        llt = self.getTopicAgentList(topic)
        return list(filter(lambda args: args.get('name') == agentName,llt))
# lookup for agents fulfilling a topic given by type and name 
    def lookupAgents(self,stype,sname):
        topic = "{}-{}".format(stype,sname)
        return self.getTopicAgentList(topic)
# list of agents fulfilling a service (topic)        
    def getTopicAgentList(self,topic):   
        return [JsonUtil.toStructure(self.redisClient.lindex(topic, n)) for n in range(0,self.redisClient.llen(topic))]

# print the list of agents fulfilling a service (topic)    
    def printService(self,topic):
        print('Printing:',topic)
        llt = self.getTopicAgentList(topic)
        for agt in llt:
            print(agt)                                                    
# Empty the Redis topic agent list -> cancel the topic
    def cancelService(self,stype,sname):
        topic = "{}-{}".format(stype,sname)
        self.cancelTopic(topic)
        
    def cancelTopic(self,topic):
        for i in range(0, self.redisClient.llen(topic)):
            self.redisClient.lpop(topic)
# Cancel all services
    def cancelAll(self):
        ll = self.redisClient.keys()
        print('canceling all services:', ll)
        for topic in ll:
            self.cancelTopic(topic)

    def printAllServices(self):   
        ll = self.redisClient.keys() 
        for topic in ll:
            print('Topic:', topic)
            for n in range(0, self.redisClient.llen(topic)):
                print(self.redisClient.lindex(topic, n)) 
                
serviceManager=ServiceManager() 