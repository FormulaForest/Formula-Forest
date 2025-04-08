from car import Car
from F_propulsion import Propulsion
from F_drag import Drag
from F_bearing import Bearing
from F_wheel import Wheel

from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":

    # Define the inertia matrix (I) for the car
    I = np.array([[53276.082, -0.001, 0.015], 
                  [-0.001, 53139.733, -3645.297], 
                  [0.015, -3645.297, 3090.801]])
    I = I * 1e-9

    def get_time(m):
        car = Car(I=I, dt=0.001, m=m/1000)
        propulsion = Propulsion(r'./Propulsion theory/F_prop1.csv')
        drag = Drag(F1=np.array([-0.45788, 0, 0.10328]), 
                    F2=np.array([-1.6443, 0, 0.3873]), 
                    T1=np.array([0,0,0]), 
                    T2=np.array([0,0,0]), v1=10, v2=20)
        bearing = Bearing(mu=0.1)
        wheel = Wheel(0.1, 0.015, 0.0001, 0.001)
        
        i = 1
        while car.x[0] < 20:
            if i > 10000:
                return 0

            car.apply_forces([propulsion.get_force(dict(car), car.t), drag.get_force(dict(car), car.t), bearing.get_force(dict(car), car.t), wheel.get_force(dict(car), car.t)])
            car.update()
            i += 1

        return car.t
    
    masses = []
    times = []
    
    for i in range(40, 81):
        masses.append(i)
        times.append(get_time(float(i)))

    plt.figure(figsize=(10, 6), facecolor='black')
    plt.plot(masses, times, marker='o', color='orange', linewidth=2)
    plt.xlabel('Mass [$g$]', fontname="Arial", fontsize=15, fontweight='bold', color='white')
    plt.ylabel('Time [$s$]', fontname="Arial", fontsize=15, fontweight='bold', color='white')
    plt.title('Race time vs Mass', fontname="Arial", fontsize=17, fontweight='bold', color='white')
    plt.grid(True, linestyle='--', alpha=0.6, color='white')
    plt.gca().set_facecolor('black')
    plt.gca().tick_params(colors='white')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().spines['top'].set_color('white')
    plt.gca().spines['right'].set_color('white')
    plt.show()