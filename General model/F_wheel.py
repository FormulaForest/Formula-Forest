import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Wheel():
    def __init__(self, mu, r, I, dt):
        self.mu = mu
        self.omega = 0.0
        self.r = r
        self.I = I
        self.dt = dt

        self.F_list = []

    def get_force(self, S: dict, t):
        '''Returns the drag force at time t'''

        if  self.omega * self.r >= S['v'][0]:
            F = np.array([-1 * S['a'][0] * self.I / (self.r ** 2), 0, 0])
        else:
            F = F = np.array([-1 * self.mu * S['N'], 0, 0])
            self.update(F[0])
        T = np.zeros(3)

        force = Force(T=T, F=F)
        force.convert_coords(S)
        self.F_list.append(F)
        return force
    
    def update(self, F):
        self.omega += F * self.r / self.I * self.dt


if __name__ == '__main__':
    pass
