import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

v = np.linspace(0, 25, 100)
fy = v**3 * 5.199750e-06 - v**2 * 5.607575e-04

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

# Make a function that gives an option for controlled smoothening (scatter -> line plot)

# Plot 1: Drag Force vs Speed
plt.figure(figsize=(10, 6))
plt.plot(v, fy, label='Drag Force [$N$]', color='#f1a93b', linewidth=3)
plt.scatter([10, 20], [-0.050876, -0.182705], color='black', s=50, zorder=3, label='CFD Data')

# plt.plot(speeds, drag_forces, marker='s', label='Drag Force [N]', color='#f1a93b', linewidth=3)
plt.xlabel('Speed [$m/s$]', fontname="Arial", fontsize=15, fontweight='bold')
plt.ylabel('Drag Force [$N$]', fontname="Arial", fontsize=15, fontweight='bold', color='black')
plt.title('Drag Force vs Speed', fontname="Arial", fontsize=17, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend()

plt.show()