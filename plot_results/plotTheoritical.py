import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Plot results from a CSV file.')
parser.add_argument('--csv', type=str, required=True, help='Path to the input CSV file.')
parser.add_argument('--output', type=str, required=True, help='Path to the output image file.')
args = parser.parse_args()

# Read the CSV file
csv_file = args.csv
data = pd.read_csv(csv_file, skiprows=1)

# Assign column names based on the data structure
data.columns = ['lambd', 'mu', 'max_t', 'n', 'd', 'w', 'queue_size',"quantum","weibull_shape"]

# Convert string representations of lists to actual lists
data['queue_size'] = data['queue_size'].apply(eval)
#data['waiting_times'] = data['waiting_times'].apply(eval)
#data['server_utilizations'] = data['server_utilizations'].apply(eval)

# Define the range of queue sizes to consider
queue_size_range = range(1, 21)

# Define the values of d to plot
d_values = [1, 2, 5, 10]

# Create a figure with 4 subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 10))
axs = axs.flatten()

for i, d_value in enumerate(d_values):
    ax = axs[i]
    for lambda_value in data['lambd'].unique():
        subset = data[(data['lambd'] == lambda_value) & (data['d'] == d_value)]
        all_queue_sizes = [size for sublist in subset['queue_size'] for size in sublist]
        fractions = []
        for q in queue_size_range:
            fraction = sum(1 for size in all_queue_sizes if size >= q) / len(all_queue_sizes)
            fractions.append(fraction)
        ax.plot(queue_size_range, fractions, marker='o', label=f'lambd={lambda_value}')
    ax.set_title(f'd={d_value}')
    ax.set_xlabel('Queue Length (Q)')
    ax.set_ylabel('Fraction of Queues with at least Q size')
    ax.legend()
    ax.grid(True)

plt.suptitle('Fraction of Queues with at least Q size vs Queue Length for Different Lambda Values and d Values')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save the plot to a file
output_file = args.output
plt.savefig(output_file)