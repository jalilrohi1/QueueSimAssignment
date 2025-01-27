import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('./out.csv')  # Replace 'your_csv_file.csv' with the actual file name

# Group data by mu, n, and d
grouped = df.groupby(['mu', 'n', 'd'])

# Iterate through groups and plot
for name, group in grouped:
    mu, n, d = name
    print(f"Plotting for mu={mu}, n={n}, d={d}")  # Debug print
    print(group[['lambd', 'w']])  # Debug print
    plt.plot(group['lambd'], group['w'], label=f'mu={mu}, n={n}, d={d}')

# Customize the plot
plt.xlabel('Lambda (Arrival Rate)')
plt.ylabel('W (Average Time in System)')
plt.title('Average Time in System vs. Arrival Rate')
plt.legend()
plt.grid(True)

# Save the plot to a file
plt.savefig('plot.png')