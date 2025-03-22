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
    print(car.x, car.x_list[0])
    
    while car.x[0] < 20:
        car.apply_forces([propulsion.get_force(dict(car), car.t)])
        car.update()
        # print(car.x_list[-1])

    # for i in range(int(1/0.001)):
    #     time = i/1000
    #     car.apply_forces([propulsion.get_force(dict(car), time)])
    #     print(time, car.forces)
    #     car.update()
    #     x.append(dict(car)["x"][0])
    #     t.append(time)

    print(car.t)
    car.x = [-1, 0, 0]
    # print(car.x_list[-1])
    x = [cord[0] for cord in car.x_list]
    plt.scatter(car.t_list, x)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Position of the Car Over Time')
    plt.grid(True)
    plt.show()