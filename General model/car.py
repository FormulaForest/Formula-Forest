import sympy as ap
import numpy as np
import matplotlib.pyplot as plt

class Car:

    def __init__(self):
        self.x = np.zeros(3)
        self.v = np.zeros(3)
        self.a = np.zeros(3)
        # sets pos, vel, acc
        self.theta = np.zeros(3)
        self.omega = np.zeros(3)
        self.alpha = np.zeros(3)
        # sets angular pos, vel, acc
        self.t = 0
        self.dt = 1e-4
        self.m = 0.05
        self.forces = []

    def apply_forces(self, F:tuple):
        for f in F:
            self.forces.append(f)
        # adds forces to the car

    def __iter__(self):
        dict = {"t": self.t, "x": self.x, "v": self.v, "a": self.a, "theta": self.theta, "omega": self.omega, "alpha": self.alpha}
        return iter(dict.items())

    def update(self):
        self.t += self.dt

        for f in self.forces:
            self.a += f.F / self.m
                # acceleration is the sum of all forces divided by mass

        self.v += self.a * self.dt
            # linear motion
        self.x += self.v * self.dt
            # angular motion

        for f in self.forces:
            self.alpha += f.get_torque() / self.m
                # angular acceleration is the sum of all torques divided by mass

        self.omega += self.alpha * self.dt
            # angular velocity is the sum of all angular accelerations
        self.theta += self.omega * self.dt
            # angular position is the sum of all angular velocities

        self.forces = []


if __name__ == "__main__":
    car = Car()
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])
    # car.apply_forces([Force(r=(0, 0, 0), F=(0, 0, 0))])

    # for _ in range(1000):
    #     car.update()

    # for k, v in car:
    #     print(k, v)

    # plt.plot(car.x[0], car.x[1])
    # plt.show()

    print(dict(car))