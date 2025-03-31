from car import Car
# from wheel import Wheel
from F_propulsion import Propulsion
from F_drag import Drag
from F_bearing import Bearing

from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":
    I = np.array([[53276.082, -0.001, 0.015], 
                  [-0.001, 53139.733, -3645.297], 
                  [0.015, -3645.297, 3090.801]])
    I = I * 1e-9

    car = Car(I=I, dt=0.001, m=0.05)
    propulsion = Propulsion(r'./Propulsion theory/F_prop1.csv', y_r=0.001)
    drag = Drag(F1=np.array([-0.050876, 0, 0.011476]), 
                F2=np.array([-0.182705, 0, 0.043031]), 
                T1=np.array([0,0,0]), 
                T2=np.array([0,0,0]), v1=10, v2=20)
    bearing = Bearing(mu=0.02)
    
    i = 1
    while car.x[0] < 20 and i < 1000:
        car.apply_forces([propulsion.get_force(dict(car), car.t), drag.get_force(dict(car), car.t), bearing.get_force(dict(car), car.t)])
        car.update()
        i += 1


    plots = [(car.x_list, 0, "X position (m)"), (car.x_list, 1, "Y position (m)"), (car.x_list, 2, "Z position (m)"),
             (car.v_list, 0, "X velocity (m)"), (car.v_list, 1, "Y velocity (m)"), (car.v_list, 2, "Z velocity (m)"),
            (car.N_list, -1, "Normal Force (N)"), (car.a_list, 0, "X acceleration (m/s^2)"),]
    for plot in plots:
        if plot[1] == -1:
            y= plot[0]
        else:
            y = [cord[plot[1]] for cord in plot[0]]

        plt.figure()
        plt.plot(car.t_list, y)
        plt.xlabel('Time (s)')
        plt.ylabel(plot[2])
        plt.title(f'{plot[2]} Over Time')
    
    print(car.t)
    # plt.scatter(car.t_list, x)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Position (m)')
    # plt.title('Position of the Car Over Time')
    # plt.grid(True)
    plt.show()