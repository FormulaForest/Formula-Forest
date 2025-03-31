import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Drag():
    def __init__(self, F1, F2, T1, T2, v1, v2):
        '''Does the approximation and sets up the coefficients for the drag force'''
        np.set_printoptions(precision=10, suppress=False)

        M = np.array([[v1**3, v1**2], [v2**3, v2**2]])
        self.f_coeff = np.zeros((3, 2))
        self.t_coeff = np.zeros((3, 2))

        for i in range(3):
            b = np.array([[F1[i]], [F2[i]]])
            x = np.linalg.solve(M, b)
            self.f_coeff[i, :] = x.flatten()

            b = np.array([[T1[i]], [T2[i]]])
            x = np.linalg.solve(M, b)
            self.t_coeff[i, :] = x.flatten()

        print(self.f_coeff)

    def get_force(self, S: dict, t):
        '''Returns the drag force at time t'''
        v = S['v'][0]
        F = self.f_coeff @ np.array([v**3, v**2])
        T = self.t_coeff @ np.array([v**3, v**2])

        # print("Computed force:\n", F)
        # print("Computed torque:\n", T)

        force = Force(T=T, F=F)
        force.convert_coords(S)
        return force


if __name__ == '__main__':
    drag = Drag(F1=np.array([0.137, 0.01, 0.01]), 
                F2=np.array([0.677, 0.03, 0.02]), 
                T1=[0.137, 0.01, 0.01], T2=[0.17, 0.021, 0.0311], v1=8, v2=18)
    
    drag.get_force({'v': [10, 0, 0]}, 0)
