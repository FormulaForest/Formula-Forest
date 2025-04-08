import matplotlib.pyplot as plt

# Data
risks = [
    "Fighting within team",
    "Absence within team",
    "Missing a deadline",
    "Falling behind on tasks"
]
risk_levels = [6, 7, 9, 9]
color = '#f1a93b'

# Create a 4x1 grid of horizontal bar charts with refined styling
plt.figure(figsize=(10, 8))

for i, (risk, level) in enumerate(zip(risks, risk_levels)):
    plt.subplot(4, 1, i + 1)  # 4 rows, 1 column
    plt.barh(risk, level, color=color, height=0.05)  # Thinner bars for a refined look
    plt.xlim(0, 10)
    if i == 3:
        plt.xlabel("Risk Level (out of 10)", fontsize=12, fontweight='bold')
    plt.xticks(fontsize=10)
    # plt.title(risk, fontsize=14, fontweight='bold')
    
    # Customize the left-hand labels to be bold and larger
    plt.yticks(fontsize=12, fontweight='bold')

    plt.grid(axis='x', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.show()
