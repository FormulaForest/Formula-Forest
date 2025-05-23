import numpy as np
import matplotlib.pyplot as plt


'''

Creates the svg file for the curved used in designing the intake section of the tunnel. Svg is then imported into fusion.

'''

x = np.linspace(0, 600, 100000)
y = (-10*pow(x/600,3) + 15*pow(x/600,4) - 6*pow(x/600, 5))*(300-105)+300

plt.plot(x, y, color='black')
plt.axis('off')  # No axes
plt.gca().set_aspect('equal')  # Keep proportions

# Save as SVG
plt.savefig(r"C:\Users\levta\Документы\WFS\Engineering\Wind Tunnel\curve1.svg", format="svg", bbox_inches='tight')