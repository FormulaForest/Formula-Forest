import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Propulsion():
    def __init__(self, file_name, z_r=0, y_r=0):
        self.z_r = z_r
        self.y_r = y_r
        self.df = pd.read_csv(file_name)
        self.t_end = self.df['T'].max()


    def get_force(self, S:dict, t):
        # change the direction of the force by accounting for theta
        if t > self.t_end:
            force_value = 0
        else:
            force_value = np.interp(t, self.df['T'], self.df['F'])  # Linearly interpolate force
        F = tuple(F * S['r'])
        r = 
        return Force(r=(0, self.y_r, self.z_r), F=(force_value, 0, 0))
        
    # def interpolate(self):
    #     # Set time as index
    #     self.df.set_index('T', inplace=True)
    #     self.t_end = self.df.index[-1]

    #     # Interpolate linearly
    #     df_interpolated = self.df.reindex(np.arange(0, self.t_end, dt)).interpolate(method='linear')

    #     # Reset index to keep time column
    #     df_interpolated.reset_index(inplace=True)

    #     self.df = df_interpolated


if __name__ == '__main__':
    # test the interpolation
    prop = Propulsion(r'.\Propulsion theory\F_prop.csv', 0.001, 1)
    print(prop.df)
    prop.get_force({'x': 0, 'v': 0, 'a': 0, 'r': 0, 'omega': 0, 'alpha': 0}, 0.0035)
    t = np.linspace(0, 0.7, 1000)
    F = [prop.get_force({'x': 0, 'v': 0, 'a': 0, 'r': 0, 'omega': 0, 'alpha': 0}, i).F[0] for i in t]
    plt.scatter(t, F)
    plt.show()