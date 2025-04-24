import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# load custom style (by name, if installed in stylelib)
plt.style.use(r'/Styles/dark.mplstyle')

speeds = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
drag_forces = np.array([
    -0.0009890971559062, -0.004040593830704, -0.009307135851632, 
    -0.0165458194505, -0.02520518387491, -0.03598502476597, 
    -0.04829570001777, -0.06106199905175, -0.07900398217662, 
    -0.0955458902612, -0.1166525443359, -0.1366622439885, 
    -0.1612050326976, -0.1850915868329, -0.2117018022794, 
    -0.2399722427203, -0.2733533233385, -0.2971802542459, 
    -0.3336498725397
])

A = 0.001864347  # m^2
rho = 1.225      # kg/m^3

Cd_values = -(2 * drag_forces) / (rho * A * speeds**2)

df = pd.DataFrame({
    'Speed': speeds,
    'DF': drag_forces,
    'DC': Cd_values
})



fig, ax = plt.subplots()
ax.plot(df['Speed'], df['DC'], label='Drag Coefficient')
ax.set_title('Drag Coefficient vs Speed')
ax.set_xlabel('Speed [m/s]')
ax.set_ylabel('Drag Coefficient')
ax.legend()
plt.show()