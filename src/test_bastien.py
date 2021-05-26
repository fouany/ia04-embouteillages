from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage

import time
from threading import Timer

autoroute_name = "autoroute"


class CarAgent(EdgeBaseAgent):
    """ Agent voiture

    Args:
        EdgeBaseAgent
    """
    def __init__(self, name, vitesse, hp, x, driver):
        super().__init__(name)
        self.hp = hp
        self.a = 0
        self.vitesse = vitesse
        self.x = x
        self.last_update = time.time()
        self.driver = driver

    def update(self):
        t = time.time()
        dt = t - self.last_update
        self.last_update = t
        self.vitesse = self.a*dt + self.vitesse
        if self.vitesse < 0:
            self.vitesse = 0
        if self.vitesse > 36:
            self.vitesse = 36
        self.x = self.vitesse*dt + self.x
        self.send_position_driver()
        printing = [self.name, self.a, self.vitesse, self. x]
        print(printing)

    def send_position_driver(self):
        msg = AgentMessage()
        msg.addReceiver(self.driver)
        msg.Type = "Inform"
        msg.setContent(f"driver_position {self.x}")
        self.send_message(msg)

    def send_position_car(self, receiver_name):
        msg = AgentMessage()
        msg.addReceiver(self.driver)
        msg.Type = "Inform"
        msg.setContent(f"car_position {self.x}")
        self.send_message(msg)

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
        elif split_content[0] == "ask_position":
            self.send_position_car(msg.From)

    
            



class DriverAgent(EdgeBaseAgent):
    """ Agent conducteur

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, reaction_time, car_name, position):
        super().__init__(name)
        self.reaction_time = reaction_time
        self.car_name = car_name

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            self.accelerate(int(split_content[1]))
        elif split_content[0] == "driver_position":
            self.position = split_content[1]
        elif split_content[0] == "front_car":
            self.ask_position()
        elif split_content[0] == "car_position":
            self.handle_distance(split_content[1] - self.x)
        elif split_content[0] == "update":
            self.ask_front_car()


    def accelerate(self, value):
        time.sleep(self.reaction_time)
        msg = AgentMessage()
        msg.addReceiver(self.car_name)
        msg.Type = "Request"
        msg.setContent(f"accelerate {value}")
        self.send_message(msg)

    def ask_front_car(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"front_car")
        self.send_message(msg)

    def ask_position(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"ask_position")
        self.send_message(msg)
    
    def handle_distance(self, distance):
        if distance > self.vitesse*2.16:
            self.accelerate(15)
        else:
            self.accelerate(-15)


class Autoroute(EdgeBaseAgent):
    """ Agent autoroute (unique)

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, car_list):
        super().__init__(name)
        self.car_list = car_list

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            receiver_name = "d" + \
                self.car_list[self.car_list.index(split_content[1]) - 1]
            self.transfert(receiver_name)
        elif split_content[0] == "ask_front_car":
            msg = AgentMessage()
            msg.addReceiver(msg.From)
            msg.Type = "Inform"
            front_car_name = self.car_list[(self.car_list.index(split_content[1]) + 1) % len(self.car_list)]
            msg.setContent(f"front_car {front_car_name}")
            self.send_message(msg)



    def transfert(self, receiver_name):
        msg = AgentMessage()
        msg.addReceiver(receiver_name)
        msg.Type = "Request"
        msg.setContent("brake_lights -5")
        self.send_message(msg)
    
    def send_distance(self, receiver_name, value):
        msg = AgentMessage()
        msg.addReceiver(receiver_name)
        msg.Type = "Inform"
        msg.setContent(f"distance {value}")
        self.send_message(msg)


# Classe utilitaire pour la gestion des timers
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
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


# Idem
class TimeAgent(EdgeBaseAgent):
    def __init__(self, name, dt, car_n_agent_list):
        super().__init__(name)
        self.dt = dt
        self.car_n_agent_list = car_n_agent_list
        self.rt = RepeatedTimer(dt, self.send_update)

    def send_update(self):
        for (car_name, agent_name) in self.car_n_agent_list:
            msg = AgentMessage()
            msg.Type = "Request"
            msg.addReceiver(car_name)
            msg.setContent("update")
            self.send_message(msg)
            msg2 = AgentMessage()
            msg2.Type = "Request"
            msg2.addReceiver(agent_name)
            msg2.setContent("update")
            self.send_message(msg2)


if __name__ == "__main__":
    # Construction des voitures
    Car1 = CarAgent("1", 20, 50, 0, "d1")  # Nom, vitesse, horsepower, position
    Car2 = CarAgent("2", 20, 50, 100, "d2")
    Car3 = CarAgent("3", 20, 50, 200, "d3")

    # Construction des conducteurs
    Driver1 = DriverAgent("d1", 1, Car1.name, 0) # Nom, temps reaction, nom voiture
    Driver2 = DriverAgent("d2", 1, Car2.name, 100)
    Driver3 = DriverAgent("d3", 1, Car3.name, 200)

    liste_voitures = [Car1.name, Car2.name, Car3.name]
    car_n_agent_list = [(Car1.name, Driver1.name), (Car2.name, Driver2.name), (Car3.name, Driver3.name)]

    # Instanciation autoroute
    auto = Autoroute(autoroute_name, liste_voitures)
    ta = TimeAgent("ta", 0.5, car_n_agent_list)
    Car2.brake_lights()
