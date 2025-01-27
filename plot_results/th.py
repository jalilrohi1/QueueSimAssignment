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
data = pd.read_csv(csv_file, header=None)

# Assign column names based on the data structure
data.columns = ['lambda', 'mu', 'max_t', 'n', 'd', 'average_time_spent', 'queue_sizes', 'waiting_times', 'server_utilizations']

# Convert string representations of lists to actual lists
data['queue_sizes'] = data['queue_sizes'].apply(eval)
data['waiting_times'] = data['waiting_times'].apply(eval)
data['server_utilizations'] = data['server_utilizations'].apply(eval)

# Plot fraction of queue sizes that are at least a certain size for different lambda values
plt.figure(figsize=(10, 6))

# Define the range of queue sizes to consider
queue_size_range = range(1, 21)

for lambda_value in data['lambda'].unique():
    subset = data[data['lambda'] == lambda_value]
    all_queue_sizes = [size for sublist in subset['queue_sizes'] for size in sublist]
    fractions = []
    for q in queue_size_range:
        fraction = sum(1 for size in all_queue_sizes if size >= q) / len(all_queue_sizes)
        fractions.append(fraction)
    plt.plot(queue_size_range, fractions, marker='o', label=f'lambda={lambda_value}')

plt.xlabel('Queue Size (Q)')
plt.ylabel('Fraction of Queues with at least Q size')
plt.title('Fraction of Queues with at least Q size vs Queue Size for Different Lambda Values')
plt.legend()
plt.grid(True)

# Save the plot to a file
output_file = args.output
plt.savefig(output_file)