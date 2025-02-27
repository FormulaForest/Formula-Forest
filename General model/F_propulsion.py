import pandas as pd
from force import Force

class Propulsion(Force):

    def __init__(self, file_name, dt, t_end):
        self.df = pd.read_csv(file_name)
        self.dt = dt
        self.t_end = t_end

        self.interpolate()
        
    def interpolate(self):
        # interpolates the force at a given time
        for t in range(0, self.t_end, self.dt):
            if t in self.df['time']:
                continue
            self.df = pd.concat([pd.DataFrame([[t,pd.NA]], columns=self.df.columns), self.df], ignore_index=True)


if __name__ == '__main__':
    # test the interpolation
    prop = Propulsion('F_prop.csv', 0.001, 5)
    print(prop.df)