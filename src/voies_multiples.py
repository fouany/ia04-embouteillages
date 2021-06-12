from typing import List
from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage

import time
import random
from threading import Timer, active_count
import matplotlib.pyplot as plt

autoroute_name = "autoroute"
autoroute_length = 300
simulation_name = 'simulation'
car_positions = {}


class CarAgent(EdgeBaseAgent):
    """ Agent voiture

    Args:
        EdgeBaseAgent
    """
    def __init__(self, name, vitesse, acceleration, deceleration, x, driver):
        super().__init__(name)
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.a = 0
        self.vitesse = vitesse
        self.x = x
        self.last_update = time.time()
        self.driver = driver
        car_positions[name] = []

    def update(self):
        t = time.time()
        dt = t - self.last_update
        self.last_update = t
        self.vitesse = self.a*dt + self.vitesse
        if self.vitesse < 0:
            self.vitesse = 0
        if self.vitesse > 36:
            self.vitesse = 36
        self.x = (self.vitesse*dt + self.x) % autoroute_length
        self.send_xv_driver()
        self.send_position_car(simulation_name)
        #printing = [self.name, self.a, self.vitesse, self.x]
        car_positions[self.name].append(round(self.x, 2))
        #print(printing)

    def send_xv_driver(self):
        msg = AgentMessage()
        msg.addReceiver(self.driver)
        msg.Type = "Inform"
        msg.setContent(f"driver_xv {self.x} {self.vitesse}")
        self.send_message(msg)

    def send_position_car(self, receiver_name):
        msg = AgentMessage()
        msg.addReceiver(receiver_name)
        msg.Type = "Inform"
        msg.setContent(f"car_position {self.x} {self.name} {time.time()}")
        self.send_message(msg)

    def accelerate(self, value):
        self.a = value

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "accelerate":
            self.accelerate(int(self.acceleration))
        elif split_content[0] == "break":
            self.accelerate(int(self.deceleration))
        elif split_content[0] == "update":
            self.update()
        elif split_content[0] == "ask_position":
            self.send_position_car(split_content[1])

    


class DriverAgent(EdgeBaseAgent):
    """ Agent conducteur

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, reaction_time, car_name, position, vitesse, security_distance, longAutoroute):
        super().__init__(name)
        self.reaction_time = reaction_time
        self.car_name = car_name
        self.position = position
        self.vitesse = vitesse
        self.security_distance = security_distance
        self.longAutoroute = longAutoroute

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            Timer(self.reaction_time, self.accelerate(int(split_content[1])))
        elif split_content[0] == "driver_xv":
            self.position = float(split_content[1])
            self.vitesse = float(split_content[2])
        elif split_content[0] == "front_car":
            self.ask_position(split_content[1])
        elif split_content[0] == "car_position":
            self.handle_distance(float(split_content[1]) - float(self.position))
        elif split_content[0] == "update":
            self.ask_front_car()


    def accelerate(self, value):
        if value > 0:
            content = "accelerate"
        else:
            content = "break"
        msg = AgentMessage()
        msg.addReceiver(self.car_name)
        msg.Type = "Request"
        msg.setContent(f"{content}")
        self.send_message(msg)

    def ask_front_car(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"ask_front_car {self.car_name} {self.name}")
        self.send_message(msg)

    def ask_position(self, car_name):
        msg = AgentMessage()
        msg.addReceiver(car_name)
        msg.Type = "Request"
        msg.setContent(f"ask_position {self.name}")
        self.send_message(msg)
    
    def handle_distance(self, distance):
        if distance < 0:
            real_distance = self.longAutoroute + distance
        else:
            real_distance = distance
        self.send_distance_simulation(real_distance)
        if real_distance > self.security_distance:
            timer = Timer(self.reaction_time, self.accelerate, [1])
            timer.start()
        elif real_distance < self.security_distance/2:
            self.overtake()
        else:
            timer = Timer(self.reaction_time, self.accelerate, [-1])
            timer.start()  
              
    def send_distance_simulation(self, distance):
        msg = AgentMessage()
        msg.addReceiver(simulation_name)
        msg.Type = "Inform"
        msg.setContent(f"car_distance {distance} {self.car_name} {time.time()}")
        self.send_message(msg)

    def overtake(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"overtake {self.name} {self.vitesse}")
        self.send_message(msg)


class Autoroute(EdgeBaseAgent):
    """ Agent autoroute (unique)

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, car_list, global_list, longueur):
        super().__init__(name)
        self.car_list = car_list
        self.autoroute_length = longueur
        self.nb_lanes = len(car_list)
        self.dict_lanes = {}
        for i in range(self.nb_lanes):
            for car_name in car_list[i]:
                self.dict_lanes[car_name] = i


    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "ask_front_car":
            msg = AgentMessage()
            msg.addReceiver(split_content[2])
            msg.Type = "Inform"
            car_name = split_content[1]
            front_car_name = self.car_list[self.dict_lanes[car_name]][(self.car_list.index(car_name) + 1) % len(self.car_list)]
            msg.setContent(f"front_car {front_car_name}")
            self.send_message(msg)
        elif split_content[0] == 'overtake':
            if self.dict_lanes[self.]
            msg = AgentMessage()
            msg.addReceiver(split_content[2])
            msg.Type = "Request"
            msg.setContent(f"front_car {front_car_name}")
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
    def __init__(self, name, dt):
        super().__init__(name)
        self.dt = dt
        self.rt = RepeatedTimer(dt, self.send_update)

    def send_update(self):
        msg = AgentMessage()
        msg.Type = "Request"
        msg.addReceiver("ALL")
        msg.setContent("update")
        self.send_message(msg)
    
    def stop(self):
        self.rt.stop()
        msg = AgentMessage()
        msg.Type = "Request"
        msg.addReceiver(simulation_name)
        msg.setContent("print_simulation")
        self.send_message(msg)

class Simulation(EdgeBaseAgent):
    def __init__(self, name, car_list, dt):
        super().__init__(name)
        self.car_list = car_list
        self.X = {}
        self.D = {}
        self.TX = {}
        self.TD = {}
        self.creation_time = time.time()
        for car_name in car_list:
            self.X[car_name] = []
            self.D[car_name] = []
            self.TX[car_name] = []
            self.TD[car_name] = []
        self.dt = dt

    def sync(self):
        X_sync = {}
        for car_name, position_list in self.X.items():
            time_list = self.TX[car_name]
            X_sync[car_name] = []
            dti = self.dt
            previous_x = position_list[0]
            previous_t = time_list[0]
            for i in range(1, len(position_list)):
                x = position_list[i]
                t = time_list[i]
                if x > dti:
                    v = (x - previous_x) / (t - previous_t)
                    x_sync = previous_x + v*(t - previous_t)
                    X_sync[car_name].append(x_sync)
                previous_x = x
                previous_t = t
                dti = dti + self.dt
        return X_sync

                
    
    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == 'car_position':
            self.X[split_content[2]].append(float(split_content[1]))
            self.TX[split_content[2]].append(float(split_content[3]) - self.creation_time)
        elif split_content[0] == 'car_distance':
            self.D[split_content[2]].append(float(split_content[1]))
            self.TD[split_content[2]].append(float(split_content[3]) - self.creation_time)
        elif split_content[0] == 'print_simulation':
            for car_name in self.car_list:
                plt.plot(self.TD[car_name], self.D[car_name])
            plt.xlabel("Temps")
            plt.ylabel("Distance relative")
            plt.show()
            import json
            with open('car_positions.json', 'w') as fp:
                json.dump(self.sync(), fp, ensure_ascii=False)

def initialisation(nbVoiture=3, vitesse=20, acceleration=3, deceleration=-8, longAutoroute=300, var_position=0,
             var_vitesse=0, var_acceleration=0, var_deceleration=0, dt=0.01, reaction_time=0.5, var_rt=0, simulation_time=15):
    liste_voitures, liste_Objets_Voitures, liste_drivers = [], [], []
    security_distance = longAutoroute/nbVoiture
    for i in range(nbVoiture):
        position_temp = random.gauss(i*security_distance, var_position)
        acceleration_temp = random.gauss(acceleration, var_acceleration)
        deceleration_temp = random.gauss(deceleration, var_deceleration)
        reaction_time_temp = random.gauss(reaction_time, var_rt)
        vitesse_temp = random.gauss(vitesse, var_vitesse)
        Car = CarAgent(str(i), vitesse_temp, acceleration_temp, deceleration_temp, position_temp, "d" + str(i))
        Driver = DriverAgent("d" + str(i), reaction_time, Car.name, position_temp, acceleration_temp, security_distance, longAutoroute)
                
        liste_voitures.append(Car.name)
        liste_Objets_Voitures.append(Car)
        liste_drivers.append(Driver.name)

    sa = Simulation(simulation_name, liste_voitures, dt*10)
    autoroute = Autoroute(autoroute_name, liste_voitures, longAutoroute)
    ta = TimeAgent("ta", dt)
    liste_Objets_Voitures[0].accelerate(-1)
    print(">>> La simulation est lancée ...")
    time.sleep(simulation_time)
    ta.stop()
    print(car_positions)


if __name__ == "__main__":
    initialisation(simulation_time=5)

    # Laisser les commentaires comme référence

    # # Construction des voitures
    # Car1 = CarAgent("1", 20, 50, 0, "d1")  # Nom, vitesse, horsepower, position
    # Car2 = CarAgent("2", 20, 50, 100, "d2")
    # Car3 = CarAgent("3", 20, 50, 200, "d3")

    # # Construction des conducteurs
    # Driver1 = DriverAgent("d1", 2, Car1.name, 0, 20) # Nom, temps reaction, nom voiture
    # Driver2 = DriverAgent("d2", 2, Car2.name, 100, 20)
    # Driver3 = DriverAgent("d3", 2, Car3.name, 200, 20)

    # liste_voitures = [Car1.name, Car2.name, Car3.name]
    # car_n_agent_list = [(Car1.name, Driver1.name), (Car2.name, Driver2.name), (Car3.name, Driver3.name)]
    # sa = Simulation(simulation_name, liste_voitures, 0.01)

    # # Instanciation autoroute
    # auto = Autoroute(autoroute_name, liste_voitures)
    # ta = TimeAgent("ta", 0.01)
    # Car2.brake_lights()
    # print(">>> La simulation est lancée ...")
    # time.sleep(15)
    # ta.stop()
    # print(car_positions)