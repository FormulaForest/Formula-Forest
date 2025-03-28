import pandas as pd

# df1 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop1.csv')
# df2 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop2.csv')
# df3 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop3.csv')
# df_avg = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_avg.csv')

df1 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop1.csv")
df2 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop2.csv")
df3 = pd.read_csv("Formula-Forest/Propulsion theory/F_prop3.csv")
df_avg = pd.read_csv("Formula-Forest/Propulsion theory/F_avg.csv")

import matplotlib.pyplot as plt
import numpy as np

# Make a function that gives an option for controlled smoothening (scatter -> line plot)

plt.figure(figsize=(8,5))
plt.scatter(df1['T'], df1['F'], color='gray', s=1, label="Trial 1")
plt.scatter(df2['T'], df2['F'], color='black', s=1, label="Trial 2")
plt.scatter(df3['T'], df3['F'], color='dimgray', s=1, label="Trial 3")
plt.plot(df_avg['T'], df_avg['F'], color='orange', linewidth=2, label="Trial Avg") # right now the smoothening is automatic, but we need to control how much it smoothes

plt.xlabel('Time [S]', fontname="Times New Roman", fontsize=12, fontweight='bold')
plt.ylabel('Canister Force [N]', fontname="Times New Roman", fontsize=12, fontweight='bold')
plt.title('Average Canister Force [N] vs. Time [S]', fontname="Times New Roman", fontsize=14, fontweight='bold')

# plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()