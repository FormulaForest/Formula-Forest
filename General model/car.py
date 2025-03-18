import sympy as ap
import numpy as np
import matplotlib.pyplot as plt

class Car:

    def __init__(self, dt = 1e-4, m = 0.05):
        self.x = np.zeros(3)
        self.v = np.zeros(3)
        self.a = np.zeros(3)
        # sets pos, vel, acc
        self.r = np.mat([[1], [0], [0]])
        self.omega = np.zeros(3)
        self.alpha = np.zeros(3)
        # sets angular pos, vel, acc
        self.t = 0
        self.dt = dt
        self.m = m
        self.forces = []

        self.t_list = [self.t]
        self.x_list = [self.x]
        self.v_list = [self.v]
        self.a_list = [self.a]
        self.r_list = [self.r]
        self.omega_list = [self.omega]
        self.alpha_list = [self.alpha]

    def apply_forces(self, F:tuple):
        for f in F:
            self.forces.append(f)
        # adds forces to the car

    def __iter__(self):
        dict = {"t": self.t, "x": self.x, "v": self.v, "a": self.a, "r": self.r, "omega": self.omega, "alpha": self.alpha}
        return iter(dict.items())

    def update(self):

        self.t_list.append(self.t)
        

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
        
        Sigma = np.mat([[0, -self.omega[2], self.omega[1]],
            [self.omega[2], 0, -self.omega[0]],
            [-self.omega[1], self.omega[0], 0]])
        R = np.identity(3) + Sigma * self.dt
        self.r = R * self.r
            # directional vector is rotated using the matrix R
        
        #self.theta += self.omega * self.dt
            # angular position is the sum of all angular velocities

        self.forces = []

        self.t_list.append(self.t)
        self.x_list.append(self.x)
        self.v_list.append(self.v)
        self.a_list.append(self.a)
        self.r_list.append(self.r)
        self.omega_list.append(self.omega)
        self.alpha_list.append(self.alpha)


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