import numpy as np
import matplotlib.pyplot as plt


"""
mass=0.05
MuRotational=0.01
CdA=0.01
"""

Time=[]
Mass=[]
CdAt=[]

def Fapplied(time):
    if(time < 0.025):
        return (9/0.025)*(time)
    elif(time < 0.06):
        return 9
    elif(time < 0.4):
        return 9-(8/0.34)*(time-0.06)
    elif(time < 0.5):
        return 9-(8/0.34)*(0.4-0.06)-(1/0.1)*(time-0.4)
    else:
        return 0
def calculation (mass, MuRotational, CdA):
    Acc=[]
    Vel=[]
    Xt=[]
    T=[]
    X=0
    Velocity=0
    Acceleration=0
    g=9.8
    AirDensity=1.225
    dt=0.001
    for time in np.arange(0, 5, dt):
        T.append(time)
        #Acceleration=((Fapplied(time))-(1/2)*AirDensity*(Velocity*Velocity)*CdA-MuRotational*mass*g)/mass
        Acceleration=((Fapplied(time))-(1/2)*AirDensity*(Velocity*Velocity)*CdA-MuRotational*mass*g)/mass
        Acc.append(Acceleration)
        Velocity=Velocity+Acceleration*dt
        Vel.append(Velocity)
        X=X+Velocity*dt
        Xt.append(X)
        if(X>=20): break
    return time


MuRotational=0.01
print(calculation(0.08, MuRotational, 0.19*0.002))

for mass in np.arange(0.02, 0.1, 0.003):
    print(mass*1000)
    for CdA in np.arange(0.01, 0.018, 0.0005):
        Time.append(5-calculation(mass, MuRotational, CdA))
        Mass.append(mass)
        CdAt.append(CdA)


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(Mass, CdAt, Time)

ax.set_xlabel('Mass')
ax.set_ylabel('CdA')
ax.set_zlabel('Time')

plt.show()


A=[]
B=[]
for time in np.arange(0, 0.5, 0.001):
    A.append(time)
    B.append(Fapplied(time))
print(B)
fig, ax = plt.subplots()
ax.plot(A, B)
ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()


#fig.savefig("test.png")
plt.show()

