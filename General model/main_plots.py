from car import Car
from F_propulsion import Propulsion
from F_drag import Drag
from F_bearing import Bearing
from F_wheel import Wheel

from matplotlib import pyplot as plt
import numpy as np
import os

if __name__ == "__main__":

    # Define the inertia matrix (I) for the car
    I = np.array([[53276.082, -0.001, 0.015], 
                  [-0.001, 53139.733, -3645.297], 
                  [0.015, -3645.297, 3090.801]])
    I = I * 1e-9

    car = Car(I=I, dt=0.001, m=0.05)
    propulsion = Propulsion(os.path.join(os.path.dirname(__file__), '../Propulsion theory/F_prop1.csv'))
    #  drag = Drag(F1=np.array([-0.45788, 0, 0.10328]),  Fake
    #                 F2=np.array([-1.6443, 0, 0.3873]), 
    #                 T1=np.array([0,0,0]), 
    #                 T2=np.array([0,0,0]), v1=10, v2=20)
    # drag = Drag(F1=np.array([-0.050876, 0, 0.011476]),  Real CFD
    #             F2=np.array([-0.182705, 0, 0.043031]), 
    #             T1=np.array([0,0,0]), 
    #             T2=np.array([0,0,0]), v1=10, v2=20)
    drag = Drag(F1=np.array([-.0051, 0, 0]),  # Real tunnel
                    F2=np.array([-.312, 0, 0]), 
                    T1=np.array([0,0,0]), 
                    T2=np.array([0,0,0]), v1=10, v2=22)
    # bearing = Bearing(mu=0.1)
    # wheel = Wheel(0.1, 0.015, 0.0001, 0.001)
    
    i = 1
    while car.x[0] < 20:
        car.apply_forces([propulsion.get_force(dict(car), car.t), drag.get_force(dict(car), car.t)])#, bearing.get_force(dict(car), car.t), wheel.get_force(dict(car), car.t)])
        car.update()
        i += 1


    # plots = [(car.x_list, 0, "X position (m)"), (car.x_list, 1, "Y position (m)"), (car.x_list, 2, "Z position (m)"),
    #          (car.v_list, 0, "X velocity (m)"), (car.v_list, 1, "Y velocity (m)"), (car.v_list, 2, "Z velocity (m)"),
    #         (car.N_list, -1, "Normal Force (N)"), (car.a_list, 0, "X acceleration (m/s^2)")]
    plots = [(car.x_list, 0, "Position [$m$]"), (car.v_list, 0, "Velocity [$m/s$]"), (car.a_list, 0, "Acceleration [$m/s^2$]")]#, (wheel.F_list, 0, "Wheel friction (N)")]
    for plot in plots:
        if plot[1] == -1:
            y= plot[0]
        else:
            y = [cord[plot[1]] for cord in plot[0]]

        plt.figure(figsize=(10, 6), facecolor='black')
        plt.gca().set_facecolor('black')
        plt.gca().tick_params(colors='white')
        plt.gca().spines['bottom'].set_color('white')
        plt.gca().spines['left'].set_color('white')
        plt.gca().spines['top'].set_color('white')
        plt.gca().spines['right'].set_color('white')
        plt.plot(car.t_list, y, color='orange', linewidth=2)
        plt.xlabel('Time [$s$]', fontname="Arial", fontsize=15, fontweight='bold', color='white')
        plt.ylabel(plot[2], fontname="Arial", fontsize=15, fontweight='bold', color='white')
        plt.title(f'{plot[2]} Over Time', fontname="Arial", fontsize=17, fontweight='bold', color='white')
        plt.grid(True, linestyle='--', alpha=0.6)
    
    print(car.t)
    # plt.scatter(car.t_list, x)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Position (m)')
    # plt.title('Position of the Car Over Time')
    # plt.grid(True)
    plt.show()