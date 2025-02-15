import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_data(csv_files, output_dir):
    """
    Plots and analyzes data from CSV files.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load data from CSV files into a dictionary
    data = {}
    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")  # Add logging to check file paths
        df = pd.read_csv(csv_file)
        sim_type = csv_file.split('/')[-1].split('_')  # Extract simulation type from filename
        data[sim_type] = df

    # --- Average Waiting Time Analysis ---
    plot_avg_waiting_time(data, output_dir)

    # --- Queue Length Distribution Analysis ---
    plot_queue_length_distribution(data, output_dir)

def plot_avg_waiting_time(data, output_dir):
    """
    Plots average waiting time against lambda for different d values.

    Args:
        data (dict): Dictionary containing DataFrames for each simulation type.
        output_dir (str): Directory to save the plots.
    """

    # Plot average waiting time (w) against lambda for different d values
    plt.figure(figsize=(10, 6))
    for sim_type, df in data.items():
        for d_value in df['d'].unique():
            subset = df[df['d'] == d_value]
            plt.plot(subset['lambd'], subset['w'], marker='o', label=f'{sim_type}, d={d_value}')

    plt.xlabel('Arrival Rate (lambda)')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Arrival Rate')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'avg_waiting_time.png'))
    plt.close()

def plot_queue_length_distribution(data, output_dir):
    """
    Plots queue length distribution as a histogram for different lambda and d values.

    Args:
        data (dict): Dictionary containing DataFrames for each simulation type.
        output_dir (str): Directory to save the plots.
    """

    # Plot queue length distribution as histograms for different lambda and d values
    for sim_type, df in data.items():
        for lambd_value in df['lambd'].unique():
            for d_value in df['d'].unique():
                subset = df[(df['lambd'] == lambd_value) & (df['d'] == d_value)]
                queue_sizes = []
                for queue_size_list in subset['queue_size']:
                    queue_sizes.extend(eval(queue_size_list))  # Convert string representation to list

                plt.figure(figsize=(10, 6))
                plt.hist(queue_sizes, bins=range(min(queue_sizes), max(queue_sizes) + 2), align='left', rwidth=0.8)
                plt.xlabel('Queue Length')
                plt.ylabel('Frequency')
                plt.title(f'Queue Length Distribution (lambda={lambd_value}, d={d_value}, {sim_type})')
                plt.grid(True)
                plt.savefig(os.path.join(output_dir, f'queue_length_dist_lambd_{lambd_value}_d_{d_value}_{sim_type}.png'))
                plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot results from CSV files.')
    parser.add_argument('csv_files', nargs='+', help='List of CSV files to process')
    parser.add_argument('--output_dir', default='plots', help='Directory to save the plots')
    args = parser.parse_args()

    plot_data(args.csv_files, args.output_dir)