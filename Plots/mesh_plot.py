import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = {
    'Mesh quality': [6.5, 7, 7.5, 8, 9],
    'Sim Time (min)': [69, 71, 72, 75, 103],
    'Drag coefficient': [0.823, 0.804, 0.813, 0.812, 0.811]
}

df = pd.DataFrame(data)

# Make a function that gives an option for controlled smoothening (scatter -> line plot)
plt.figure(figsize=(10, 6))

# Create the first y-axis for Drag Coefficient
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(df['Mesh quality'], df['Drag coefficient'], marker='s', label='Drag Coefficient', color='orange', linewidth=3)
ax1.set_xlabel('Mesh Quality [%]', fontname="Arial", fontsize=15, fontweight='bold')
ax1.set_ylabel('Drag Coefficient', fontname="Arial", fontsize=15, fontweight='bold', color='orange')
ax1.tick_params(axis='y', labelcolor='orange')

# Create the second y-axis for Sim Time
ax2 = ax1.twinx()
ax2.plot(df['Mesh quality'], df['Sim Time (min)'], marker='o', label='Sim Time (min)', color='black', linewidth=3)
ax2.set_ylabel('Sim Time [min]', fontname="Arial", fontsize=15, fontweight='bold', color='black')
ax2.tick_params(axis='y', labelcolor='black')

# Add title and grid
plt.title('Simulation Time and Drag Coefficient vs Mesh Quality', fontname="Arial", fontsize=14, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)

plt.show()