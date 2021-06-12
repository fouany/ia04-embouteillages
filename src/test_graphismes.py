from typing import Tuple
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation


n = 4
t = np.linspace(0, 2 * np.pi, 160)
x = np.cos(t)
y = np.sin(t)

# Création de la figure et de l'axe
fig, ax = plt.subplots()

# Création de la route
# line, = ax.plot(np.multiply(x, 0.93), np.multiply(y, 0.93), color='black')
# line2, = ax.plot(np.multiply(x, 1.07), np.multiply(y, 1.07), color='black')
# point, = ax.plot([], [], color="green",ls="none", marker="o")
# point2, = ax.plot([], [], color="red",ls="none", marker="o")
# point3, = ax.plot([], [], color="blue",ls="none", marker="o")



#Gestion des limites de la fenêtre
ax.set_xlim([1.1*np.min(x), 1.1*np.max(x)])
ax.set_ylim([1.1*np.min(y), 1.1*np.max(y)])

line, = ax.plot(np.multiply(x, 0.93), np.multiply(y, 0.93), color='black')
line2, = ax.plot(np.multiply(x, 1.07), np.multiply(y, 1.07), color='black')
f = open('car_positions.json',)
car_positions = json.load(f)
list_len = [len(pl) for pl in car_positions.values()]
min_len = min(list_len)
pi = math.pi
d = len(car_positions)*50
print(d)
points = []
for car_name in car_positions:
    p, = ax.plot([], [],ls="none", marker="o")
    points.append(p)
print(points)

# def init():
#     line, = ax.plot(np.multiply(x, 0.93), np.multiply(y, 0.93), color='black')
#     line2, = ax.plot(np.multiply(x, 1.07), np.multiply(y, 1.07), color='black')
#     return line, line2

# Création de la function qui sera appelée à "chaque nouvelle image"
def animate(j):
    for i in range(len(points)):
        point = points[i]
        point.set_data(math.cos((car_positions[str(i)][j]*pi)/d), math.sin((car_positions[str(i)][j]*pi)/d))
    return tuple(points)

# Génération de l'animation, frames précise les arguments numérique reçus par func (ici animate), 
# interval est la durée d'une image en ms, blit gère la mise à jour
ani = animation.FuncAnimation(fig=fig, func=animate, frames=range(min_len), interval=100, blit=True, repeat=True)
plt.show()
