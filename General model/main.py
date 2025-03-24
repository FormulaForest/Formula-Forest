# from force import Force
from car import Car
# from wheel import Wheel
from F_propulsion import Propulsion

from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":
    I = np.array([[53276.082, -0.001, 0.015], 
                  [-0.001, 53139.733, -3645.297], 
                  [0.015, -3645.297, 3090.801]])
    I = I * 1e-9

    car = Car(I=I, dt=0.001, m=0.05)
    propulsion = Propulsion(r'.\Propulsion theory\F_prop.csv')
    
    i = 1
    while car.x[0] < 20:
        print(i)
        print(car.q.shape)
        car.apply_forces([propulsion.get_force(dict(car), car.t)])
        car.update()
        i += 1


    # print(car.x_list[-1])
    x = [cord[0] for cord in car.x_list]
    plt.scatter(car.t_list, x)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Position of the Car Over Time')
    plt.grid(True)
    plt.show()