from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage

from time import sleep
import time
from threading import Timer

autoroute_name = "autoroute"

class CarAgent(EdgeBaseAgent):
    def __init__(self, name, v, hp, x):
        super().__init__(name)
        self.hp = hp
        self.a = 0
        self.v = v
        self.x = x
        self.last_update = time.time()

    def update(self):
        t = time.time()
        dt = t - self.last_update
        self.v = self.a*dt + self.v
        self.x = self.v*dt + self.x
        printing = [self.name, self.a, self.v, self. x]
        print(printing)

    def accelerate(self, value):
        self.a = self.a + value

    def brake_lights(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"brake_lights {self.name}")
        self.send_message(msg)
    
    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "accelerate":
            self.accelerate(int(split_content[1]))
        elif split_content[0] == "update":
            self.update()
    

class DriverAgent(EdgeBaseAgent):
    def __init__(self, name, reaction_time, car_name):
        super().__init__(name)
        self.reaction_time = reaction_time
        self.car_name = car_name

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            self.accelerate(int(split_content[1]))

    def accelerate(self, value):
        time.sleep(self.reaction_time)
        msg = AgentMessage()
        msg.addReceiver(self.car_name)
        msg.Type = "Request"
        msg.setContent(f"accelerate {value}")
        self.send_message(msg)

    

class Autoroute(EdgeBaseAgent):
    def __init__(self, name, car_list):
        super().__init__(name)
        self.car_list = car_list

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            receiver_name = "d" + self.car_list[self.car_list.index(split_content[1]) - 1]
            self.transfert(receiver_name)

    def transfert(self, receiver_name):
        msg = AgentMessage()
        msg.addReceiver(receiver_name)
        msg.Type = "Request"
        msg.setContent("brake_lights -30")
        self.send_message(msg)




class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class TimeAgent(EdgeBaseAgent):
    def __init__(self, name, dt, car_list):
        super().__init__(name)
        self.dt = dt
        self.car_list = car_list
        self.rt = RepeatedTimer(dt, self.send_update)
    
    def send_update(self):
        for car_name in self.car_list:
            msg = AgentMessage()
            msg.Type = "Request"
            msg.addReceiver(car_name)
            msg.setContent("update")
            self.send_message(msg)
        


if __name__ == "__main__":
    Car1 = CarAgent("1", 50, 50, 0)
    Car2 = CarAgent("2", 50, 50, 10)
    Driver1 = DriverAgent("d1", 1, "1")
    Driver2 = DriverAgent("d2", 1, "2")
    auto = Autoroute(autoroute_name, ["1", "2"])
    ta = TimeAgent("ta", 2, ["1", "2"])
    Car1.brake_lights()
