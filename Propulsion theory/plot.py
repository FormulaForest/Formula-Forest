import pandas as pd

df1 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop1.csv')
df2 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop2.csv')
df3 = pd.read_csv(r'C:\Users\levta\OneDrive\Документы\WFS\F1\Formula-Forest\Propulsion theory\F_prop3.csv')

# plt.plot(df1['T'], df1['F'], label='F_prop1')
# plt.plot(df2['T'], df2['F'], label='F_prop2')
# plt.plot(df3['T'], df3['F'], label='F_prop3')

import matplotlib.pyplot as plt
import numpy as np

# Sample data
# t = np.linspace(0, 0.5, 100)
# T1 = np.exp(-5*t) * (10 + np.random.rand(100) * 0.5)
# T2 = np.exp(-5*t) * (9 + np.random.rand(100) * 0.5)
# T3 = np.exp(-5*t) * (10.5 + np.random.rand(100) * 0.5)
# T4 = np.exp(-5*t) * (8 + np.random.rand(100) * 0.5)
# AVG = (T1 + T2 + T3 + T4) / 4

plt.figure(figsize=(8,5))
# plt.plot(t, AVG, label='AVG', color='green', linewidth=2)
plt.plot(df1['T'], df1['F'], color='gray', linewidth=1)
plt.plot(df2['T'], df2['F'], color='black', linewidth=1)
plt.plot(df3['T'], df3['F'], color='dimgray', linewidth=2)
# plt.plot(t, T4, label='T4', color='lightgray', linewidth=1)

plt.xlabel('TIME [S]', fontsize=14, fontweight='bold')
plt.ylabel('CANISTER FORCE [N]', fontsize=14, fontweight='bold')
plt.title('AVERAGE CANISTER FORCE [N] TO TIME [S]', fontsize=16, fontweight='bold')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
