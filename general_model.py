import sympy as ap
import numpy as np
import matplotlib.pyplot as plt

class Force:

    def __init__(self, r:tuple, F:tuple):
        # two three component vectors: 
        #   one for the #D position of the vector, 
        #   one for the magnitude and direction of the force
        self.r = np.array(r)
        self.F = np.array(F)

    def get_torque(self):
        d = self.r + ((np.dot(self.r, self.F) / np.dot(self.F, self.F)) * self.F)
            # finds the lever arm by which the force is applied to create the torque

        T = np.cross(d, self.F)
            # cross products the lever arm with the force

        return T

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