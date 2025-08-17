import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from scipy.spatial.transform import Rotation
import time
import matplotlib.animation as animation

class Car:

    def __init__(self):
        self.v = np.array([1,2,3])
        self.coords = np.eye(3)
        self.omega = np.array([0,0,0])
        self.dt = 0.01

        self.iHat, self.jHat, self.kHat = self.coords
        self.v1 = self.coords.T @ self.v

    def update(self):
        rot = Rotation.from_rotvec(self.omega * self.dt)
        self.coords = rot.apply(self.coords)
        self.v1 = self.coords.T @ self.v
        self.iHat, self.jHat, self.kHat = self.coords


car = Car()

# Plot orientation.
fig  = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_aspect("equal")
plt.subplots_adjust(top=0.95, bottom=0.15)
lim = 0.5
ax.set_xlim((-lim, lim))
ax.set_ylim((-lim, lim))
ax.set_zlim((-lim, lim))

def plotCoordSystem(ax, iHat, jHat, kHat, x0=np.zeros(3), ds=0.45, ls="-", omega=None, v=None):
    x1 = x0 + iHat*ds
    x2 = x0 + jHat*ds
    x3 = x0 + kHat*ds
    lns = ax.plot([x0[0], x1[0]], [x0[1], x1[1]], [x0[2], x1[2]], "r", ls=ls, lw=2)
    lns += ax.plot([x0[0], x2[0]], [x0[1], x2[1]], [x0[2], x2[2]], "g", ls=ls, lw=2)
    lns += ax.plot([x0[0], x3[0]], [x0[1], x3[1]], [x0[2], x3[2]], "b", ls=ls, lw=2)
    lns += ax.plot([x0[0], omega[0]*ds], [x0[1], omega[1]*ds], [x0[2], omega[2]*ds], "grey", ls=ls, lw=2)
    lns += ax.plot([x0[0], v[0]*ds], [x0[1], v[1]*ds], [x0[2], v[2]*ds], "black", ls=ls, lw=2)
    return lns

# Plot twice - one plot will be updated, the other one will stay as reference.
plotCoordSystem(ax, car.iHat, car.jHat, car.kHat, ls="--", omega=car.omega, v=car.v1)
lns = plotCoordSystem(ax, car.iHat, car.jHat, car.kHat, omega=car.omega, v=car.v1)

sldr_ax1 = fig.add_axes([0.15, 0.01, 0.7, 0.025])
sldr_ax2 = fig.add_axes([0.15, 0.05, 0.7, 0.025])
sldr_ax3 = fig.add_axes([0.15, 0.09, 0.7, 0.025])
sldrLim = 10
sldr1 = Slider(sldr_ax1, '$\omega_x$', -sldrLim, sldrLim, valinit=0, valfmt="%.1f rad/s")
sldr2 = Slider(sldr_ax2, '$\omega_y$', -sldrLim, sldrLim, valinit=0, valfmt="%.1f rad/s")
sldr3 = Slider(sldr_ax3, '$\omega_z$', -sldrLim, sldrLim, valinit=0, valfmt="%.1f rad/s")

def onChanged(val):
    global car
    car.omega = np.array([sldr1.val, sldr2.val, sldr3.val])

sldr1.on_changed(onChanged)
sldr2.on_changed(onChanged)
sldr3.on_changed(onChanged)

# Add a text box to display car coordinates
coord_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes)

def update_coord_text():
    coord_str = (
        f"iHat: [{car.iHat[0]:.2f}, {car.iHat[1]:.2f}, {car.iHat[2]:.2f}]\n"
        f"jHat: [{car.jHat[0]:.2f}, {car.jHat[1]:.2f}, {car.jHat[2]:.2f}]\n"
        f"kHat: [{car.kHat[0]:.2f}, {car.kHat[1]:.2f}, {car.kHat[2]:.2f}]"
    )
    coord_text.set_text(coord_str)

    # Add self.coords matrix and omega vector to the text box
    coords_str = "coords:\n" + "\n".join(
        [f"[{row[0]:.2f}, {row[1]:.2f}, {row[2]:.2f}]" for row in car.coords]
    )
    omega_str = f"omega: [{car.omega[0]:.2f}, {car.omega[1]:.2f}, {car.omega[2]:.2f}]"
    coord_text.set_text(coord_str + "\n" + coords_str + "\n" + omega_str)


def loop(frame):
    global car, lns
    update_coord_text()
    car.update()
    for l in lns:
        l.remove()
    lns = plotCoordSystem(ax, car.iHat, car.jHat, car.kHat, omega=car.omega, v=car.v1)
    return lns

anim = animation.FuncAnimation(fig, loop, interval=car.dt)

plt.show()