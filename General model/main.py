from car import Car
# from wheel import Wheel
from F_propulsion import Propulsion
from F_drag import Drag

from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":
    I = np.array([[53276.082, -0.001, 0.015], 
                  [-0.001, 53139.733, -3645.297], 
                  [0.015, -3645.297, 3090.801]])
    I = I * 1e-9

    car = Car(I=I, dt=0.001, m=0.05)
    propulsion = Propulsion(r'./Propulsion theory/F_prop.csv')
    drag = Drag(F1=np.array([0.137, 0.01, 0.01]), 
                F2=np.array([0.677, 0.03, 0.02]), 
                T1=np.array([0.137, 0.01, 0.01]), 
                T2=np.array([0.17, 0.021, 0.0311]), v1=8, v2=18)
    
    i = 1
    while car.x[0] < 20 and i < 1000:
        car.apply_forces([propulsion.get_force(dict(car), car.t), drag.get_force(dict(car), car.t)])
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