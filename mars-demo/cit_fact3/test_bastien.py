from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage, requestBaseMessage, answerMessage
from agent_v2.utils import Publisher
from operation.task_module import Tasks
from agent_v2.service import serviceManager

from time import sleep
from concurrent import  futures
import random
from agent_v2.service import Service, serviceManager
import time


class CarAgent(EdgeBaseAgent):
    def __init__(self, name, v, hp, x):
        super().__init__(name)
        self.hp = hp
        self.a = 0
        self.v = v
        self.x = x
        last_update = time.time()
    def update(self):
        t = time.time()
        dt = t - self.last_update
        self.v = self.a*dt + self.v
        self.x = self.v*dt + self.x
    

class Autoroute(EdgeBaseAgent):
    def __init__(self, name):
        super().__init__(name)