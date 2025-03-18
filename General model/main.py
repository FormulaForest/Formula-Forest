from force import Force
from car import Car
from wheel import Wheel
from F_propulsion import Propulsion
from matplotlib import pyplot as plt

if __name__ == "__main__":
    car = Car()
    propulsion = Propulsion(r'.\Propulsion theory\F_prop.csv', 0.001, 1)

    S_list = []
    t_list = []
    t = 0
    
    while 

    # for i in range(int(1/0.001)):
    #     time = i/1000
    #     car.apply_forces([propulsion.get_force(dict(car), time)])
    #     print(time, car.forces)
    #     car.update()
    #     x.append(dict(car)["x"][0])
    #     t.append(time)



    plt.scatter(t, x)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Position of the Car Over Time')
    plt.grid(True)
    plt.show()