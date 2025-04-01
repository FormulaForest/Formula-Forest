import matplotlib.pyplot as plt
import numpy as np

# Data
categories = ["Travel", "Food", "Hotel", "Entry Fees", "Marketing", "Engineering"]
expected_budget = [3480.74, 420, 1145.60, 1700, 1494, 814.50]
actual_budget = [1700, 280, 0, 1700, 164.94, 837.90]  # Hotel not finalized

# Bar Chart: Expected vs Actual Budget
x = np.arange(len(categories))

plt.figure(figsize=(10, 6))
plt.bar(x - 0.2, expected_budget, 0.4, label='Expected Budget', color='skyblue')
plt.bar(x + 0.2, actual_budget, 0.4, label='Actual Budget', color='orange')

plt.xlabel("Categories")
plt.ylabel("Amount ($)")
plt.title("Expected vs Actual Budget")
plt.xticks(ticks=x, labels=categories, rotation=20)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to make it wider

plt.show()

# Pie Chart: Expected Budget Breakdown
plt.figure(figsize=(8, 8))
plt.pie(expected_budget, labels=categories, autopct='%1.1f%%', startangle=140, colors=['lightcoral', 'gold', 'lightblue', 'green', 'purple', 'cyan'])
plt.title("Expected Budget Distribution")
plt.show()

# Pie Chart: Actual Budget Breakdown
plt.figure(figsize=(8, 8))
plt.pie(actual_budget, labels=categories, autopct='%1.1f%%', startangle=140, colors=['lightcoral', 'gold', 'lightblue', 'green', 'purple', 'cyan'])
plt.title("Actual Budget Distribution")
plt.show()