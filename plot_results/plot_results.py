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
data.columns = ['lambda', 'mu', 'max_t', 'n', 'd', 'average_time_spent', 'waiting_times']

# Convert string representations of lists to actual lists
data['queue_sizes'] = data['queue_sizes'].apply(eval)
data['waiting_times'] = data['waiting_times'].apply(eval)
#data['server_utilizations'] = data['server_utilizations'].apply(eval)

# Plot average time spent in the system for different lambda and d values
plt.figure(figsize=(10, 6))
for d_value in data['d'].unique():
    subset = data[data['d'] == d_value]
    plt.plot(subset['lambda'], subset['average_time_spent'], marker='o', label=f'd={d_value}')

plt.xlabel('Lambda')
plt.ylabel('Average Time Spent in System')
plt.title('Average Time Spent in System vs Lambda for Different d Values')
plt.legend()
plt.grid(True)

# Save the plot to a file
output_file = args.output
plt.savefig(output_file)