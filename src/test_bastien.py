from agent_v2.edge_agent import EdgeBaseAgent
from agent_v2.agent_message import AgentMessage

import time
import random
from threading import Timer
import matplotlib.pyplot as plt

autoroute_name = "autoroute"
autoroute_length = 300
simulation_name = 'simulation'
car_positions = {}
vmax = 36


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
        car_positions[name] = []

    def update(self):
        t = time.time()
        dt = t - self.last_update
        self.last_update = t
        self.vitesse = self.a*dt + self.vitesse
        if self.vitesse < 0:
            self.vitesse = 0
        if self.vitesse > vmax:
            self.vitesse = vmax
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

    def brake_lights(self):
        msg = AgentMessage()
        msg.addReceiver(autoroute_name)
        msg.Type = "Request"
        msg.setContent(f"brake_lights {self.name}")
        self.send_message(msg)

    def handleChoc(self):
        self.a = 0
        self.vitesse = 0


    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "accelerate":
            self.accelerate(int(split_content[1]))
        elif split_content[0] == "decelerate":
            self.accelerate(int(split_content[1]))
            self.last_update += int(split_content[2])
        elif split_content[0] == "update":
            self.update()
        elif split_content[0] == "ask_position":
            self.send_position_car(split_content[1])
        elif split_content[0] == "choc":
            pass

    


class DriverAgent(EdgeBaseAgent):
    """ Agent conducteur

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, reaction_time, car_name, position, vitesse):
        super().__init__(name)
        self.reaction_time = reaction_time
        self.car_name = car_name
        self.position = position
        self.vitesse = vitesse
        self.front_car = -1
        self.alertDistance = False

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            Timer(self.reaction_time, self.accelerate(int(split_content[1])))
        elif split_content[0] == "driver_xv":
            self.position = float(split_content[1])
            self.vitesse = float(split_content[2])
        elif split_content[0] == "front_car":
            self.front_car = split_content[1]
            self.ask_position(split_content[1])
        elif split_content[0] == "car_position":
            self.handle_distance(float(split_content[1]) - float(self.position))
        elif split_content[0] == "update":
            self.ask_front_car()
        elif split_content[0] == "front_car_position":
            if split_content[1] == self.front_car :
                #print("Current :", self.car_name, self.position, "front voiture: ", self.front_car, "position ", split_content[2])
                self.handle_security_distance(float(split_content[2]))



    def accelerate(self, value):
        if not self.alertDistance :
            msg = AgentMessage()
            msg.addReceiver(self.car_name)
            msg.Type = "Request"
            msg.setContent(f"accelerate {value}")
            self.send_message(msg)

    def decelerate(self, value):
        if not self.alertDistance :
            msg = AgentMessage()
            msg.addReceiver(self.car_name)
            msg.Type = "Request"
            msg.setContent(f"decelerate {value} {self.reaction_time}")
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
            real_distance = autoroute_length + distance
        else:
            real_distance = distance
        self.send_distance_simulation(real_distance)
        # 
        # if real_distance > 100:
        #     timer = Timer(self.reaction_time, self.accelerate, [3])
        #     timer.start()
        # else:
        #     timer = Timer(self.reaction_time, self.accelerate, [-8])
        #     timer.start()  
              
    def send_distance_simulation(self, distance):
        msg = AgentMessage()
        msg.addReceiver(simulation_name)
        msg.Type = "Inform"
        msg.setContent(f"car_distance {distance} {self.car_name} {time.time()}")
        self.send_message(msg)

    def sendChoc(self):
        msg = AgentMessage()
        msg.addReceiver(self.car_name)
        msg.Type = "Inform"
        msg.setContent("chock")
        self.send_message(msg)
    
    def handle_security_distance(self, position):
        dx = position - self.position
        if dx < 0:
            self.sendChoc()
        elif dx < self.vitesse * 2.78 * 6:
            self.alertDistance = True
            self.decelerate(-8)
        else :
            self.alertDistance = True


class Autoroute(EdgeBaseAgent):
    """ Agent autoroute (unique)

    Args:
        EdgeBaseAgent ([type]): [description]
    """
    def __init__(self, name, car_list, longueur):
        super().__init__(name)
        self.car_list = car_list
        autoroute_length = longueur
        autoroute_name = "autoroute"

    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == "brake_lights":
            receiver_name = "d" + \
                self.car_list[self.car_list.index(split_content[1]) - 1]
            self.transfert(receiver_name)
        elif split_content[0] == "ask_front_car":
            msg = AgentMessage()
            msg.addReceiver(split_content[2])
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
    def __init__(self, name, car_list, driver_list, dt):
        super().__init__(name)
        self.car_list = car_list
        self.driver_list = driver_list
        self.X = []
        self.D = []
        self.TX = []
        self.TD = []
        self.creation_time = time.time()
        [self.X.append([]) for _ in self.car_list]
        [self.D.append([]) for _ in self.car_list]
        [self.TX.append([]) for _ in self.car_list]
        [self.TD.append([]) for _ in self.car_list]
        self.dt = dt
    
    def receive_message(self, msg: AgentMessage):
        split_content = msg.getContent().split(" ")
        if split_content[0] == 'car_position':
            self.brodcastPosition(int(split_content[2])-1, split_content[1])
            self.X[int(split_content[2])-1].append(float(split_content[1]))
            self.TX[int(split_content[2])-1].append(float(split_content[3]) - self.creation_time)
        elif split_content[0] == 'car_distance':
            self.D[int(split_content[2])-1].append(float(split_content[1]))
            self.TD[int(split_content[2])-1].append(float(split_content[3]) - self.creation_time)
        elif split_content[0] == 'print_simulation':
            list_length = [len(d) for d in self.D]
            min_length = min(list_length)
            for i in range(len(self.D)):
                plt.plot(self.TD[i], self.D[i])
            plt.xlabel("Temps")
            plt.ylabel("Distance relative")
            plt.show()

    def brodcastPosition(self, car_name, car_position):
        for driver in self.driver_list :
            msg = AgentMessage()
            msg.addReceiver(driver)
            msg.Type = "Inform"
            msg.setContent(f"front_car_position {car_name} {car_position}")
            self.send_message(msg)

def gaussian(mu, sigma):
    nums = [] 
    m = mu
    sig = sigma
    for i in range(10000): 
        temp = random.gauss(mu, sigma) 
        nums.append(temp)        
    # Plotting pour afficher un graphe
    #plt.hist(nums, bins = 100) 
    #plt.show()
    #Retourne valeur aléatoire dans la gaussienne
    return random.choice(nums)

def initialisation(nbVoiture, vitesse, horsePower, position, longAutoroute, name_Autoroute, vm):
    liste_voitures, liste_Objets_Voitures, liste_drivers = [], [], []
    
    for i in range(nbVoiture):
        position_temp = gaussian(position[i], 25)
        horsePower_temp = gaussian(horsePower, 5)
        Car1 = CarAgent(str(i), gaussian(vitesse, 5), horsePower_temp, position_temp, "d" + str(i))
        Driver1 = DriverAgent("d" + str(i), 0.5, Car1.name, position_temp, horsePower_temp)
                
        liste_voitures.append(Car1.name)
        liste_Objets_Voitures.append(Car1)
        liste_drivers.append(Driver1.name)

    sa = Simulation(simulation_name, liste_voitures, liste_drivers, 0.01)
    autoroute = Autoroute(name_Autoroute, liste_voitures, longAutoroute)
    vmax = vm
    ta = TimeAgent("ta", 0.01)
    liste_Objets_Voitures[2].brake_lights()
    print(">>> La simulation est lancée ...")
    time.sleep(15)
    ta.stop()
    #print(car_positions)


if __name__ == "__main__":
    initialisation(3, 20, 50, [0, 100, 200], 300, "autoroute", 36)

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

    #recuperer position voiture en face
    #a chaque update, verifier si la distance de securite est respecte (distance > % 2.78 * 6)
    #si la distance de securite n'est pas respecté, il faut (decelerer / envoyer message de deceleration)
    