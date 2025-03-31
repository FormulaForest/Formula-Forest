import pandas as pd

df1 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop1.csv')
df2 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop2.csv')
df3 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop3.csv')
df_avg = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_avg.csv')

# df1 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop1.csv")
# df2 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop2.csv")
# df3 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop3.csv")
# df_avg = pd.read_csv("Formula-Forest/Propulsion theory/F_avg.csv")

import matplotlib.pyplot as plt
import numpy as np

# Make a function that gives an option for controlled smoothening (scatter -> line plot)

plt.figure(figsize=(8,5))
plt.scatter(df1['T'], df1['F'], color='gray', s=1, label="Trial 1")
plt.scatter(df2['T'], df2['F'], color='black', s=1, label="Trial 2")
plt.scatter(df3['T'], df3['F'], color='dimgray', s=1, label="Trial 3")
plt.plot(df_avg['T'], df_avg['F'], color='orange', linewidth=2, label="Trial Avg") # right now the smoothening is automatic, but we need to control how much it smoothes

plt.xlabel('Time [s]', fontname="Arial", fontsize=15, fontweight='bold')
plt.ylabel('Propulsion Force [N]', fontname="Arial", fontsize=15, fontweight='bold')
plt.title('Propulsion Force vs. Time', fontname="Arial", fontsize=17, fontweight='bold')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4, fontsize=10, frameon=False)
# plt.xticks(fontname="Times New Roman", fontsize=10, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to make it wider
plt.show()