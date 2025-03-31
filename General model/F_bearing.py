import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Bearing():
    def __init__(self, mu):
        self.mu = mu

    def get_force(self, S: dict, t):
        '''Returns the drag force at time t'''
        N = S['N']
        F = np.array([-1 * self.mu * N, 0, 0])
        T = np.zeros(3)

        # print("Computed force:\n", F)
        # print("Computed torque:\n", T)

        force = Force(T=T, F=F)
        force.convert_coords(S)
        return force


if __name__ == '__main__':
    pass
