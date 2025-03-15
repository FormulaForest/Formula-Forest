import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Propulsion():
    def __init__(self, file_name, dt, t_end, z_r=0, y_r=0):
        self.z_r = z_r
        self.y_r = y_r
        self.df = pd.read_csv(file_name)
        self.dt = dt
        self.t_end = t_end

        self.interpolate()

    def get_force(self, S:dict, t):
        # change the direction of the force by accounting for theta
        return Force(r=(0, self.y_r, self.z_r), F=(0, self.df[self.df['T'] == t]['F'].values[0], 0))
        
    def interpolate(self):
        # interpolates the force at a given time
        times = np.linspace(0, self.t_end, int(self.t_end/self.dt) + 1)
        for t in times:
            if t in self.df['T']:
                continue
            self.df = pd.concat([pd.DataFrame([[t, np.nan]], columns=self.df.columns), self.df], ignore_index=True)
        # self.df = pd.concat([pd.DataFrame([[0, 0]], columns=self.df.columns), self.df], ignore_index=True)
        
        self.df = self.df.sort_values(by='T').reset_index(drop=True).interpolate(method='linear')


if __name__ == '__main__':
    # test the interpolation
    prop = Propulsion(r'.\Propulsion theory\F_prop.csv', 0.001, 1)
    print(prop.df)
    prop.df.plot(x='T', y='F', kind="scatter")
    plt.show()