import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


n = 4
t = np.linspace(0, 2 * np.pi, 160)
x = np.cos(t)
y = np.sin(t)

# Création de la figure et de l'axe
fig, ax = plt.subplots()

# Création de la ligne qui sera mise à jour au fur et à mesure
line, = ax.plot(np.multiply(x, 0.93), np.multiply(y, 0.93), color='black')
line2, = ax.plot(np.multiply(x, 1.07), np.multiply(y, 1.07), color='black')
point, = ax.plot([], [], color="green",ls="none", marker="o")
point2, = ax.plot([], [], color="red",ls="none", marker="o")
point3, = ax.plot([], [], color="blue",ls="none", marker="o")

#Gestion des limites de la fenêtre
ax.set_xlim([1.1*np.min(x), 1.1*np.max(x)])
ax.set_ylim([1.1*np.min(y), 1.1*np.max(y)])


# Création de la function qui sera appelée à "chaque nouvelle image"
def animate(k):
    i = min(k, x.size)
    point.set_data(x[i], y[i])
    point2.set_data(x[i - 5], y[i - 5])
    return line, line2, point, point2

# Génération de l'animation, frames précise les arguments numérique reçus par func (ici animate), 
# interval est la durée d'une image en ms, blit gère la mise à jour
ani = animation.FuncAnimation(fig=fig, func=animate, frames=range(x.size), interval=50, blit=True, repeat=True)
plt.show()
