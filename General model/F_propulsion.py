import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from force import Force

class Propulsion():
    def __init__(self, file_name, dt=0.05, t_end=1, z_r=0, y_r=0):
        self.z_r = z_r
        self.y_r = y_r
        self.df = pd.read_csv(file_name)
        self.dt = dt
        self.t_end = t_end

        self.interpolate(dt, t_end)

    def get_force(self, S:dict, t):
        # change the direction of the force by accounting for theta
        print(self.df[self.df['T'] == t]['F'])
        return Force(r=(0, self.y_r, self.z_r), F=(self.df[self.df['T'] == t]['F'], 0, 0))
        
    def interpolate(self, dt, t_end):
        # # interpolates the force at a given time
        # times = np.linspace(0, self.t_end, int(self.t_end/self.dt) + 1)
        # for t in times:
        #     if t in self.df['T']:
        #         continue
        #     self.df = pd.concat([pd.DataFrame([[t, np.nan]], columns=self.df.columns), self.df], ignore_index=True)
        # # self.df = pd.concat([pd.DataFrame([[0, 0]], columns=self.df.columns), self.df], ignore_index=True)
        
        # self.df = self.df.sort_values(by='T').reset_index(drop=True).interpolate(method='linear')

        # Set time as index
        self.df.set_index('T', inplace=True)

        # Interpolate linearly
        df_interpolated = self.df.reindex(np.arange(0, t_end, dt)).interpolate(method='linear')

        # Reset index to keep time column
        df_interpolated.reset_index(inplace=True)

        self.df = df_interpolated


if __name__ == '__main__':
    # test the interpolation
    prop = Propulsion(r'.\Propulsion theory\F_prop.csv', 0.001, 1)
    print(prop.df)
    prop.get_force({'x': 0, 'v': 0, 'a': 0, 'r': 0, 'omega': 0, 'alpha': 0}, 0.0035)
    prop.df.plot(x='T', y='F', kind="scatter")
    plt.show()