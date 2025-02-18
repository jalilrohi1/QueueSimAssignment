import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_supermarket_avg_waiting_time_vs_n(csv_files, output_dir):
    """
    Plots average waiting time vs. number of servers for supermarket model simulations.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    supermarket_n_file = [f for f in csv_files if 'supermarket_n' in f]
    if not supermarket_n_file:
        raise ValueError("No file containing 'supermarket_n' found in the provided csv_files.")
    
    supermarket_n_df = pd.read_csv(supermarket_n_file[0])

    plt.figure(figsize=(10, 6))
    plt.plot(supermarket_n_df['n'], supermarket_n_df['w'], marker='o', label='Supermarket Model')
    plt.xlabel('Number of Servers (n)')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Number of Servers (Supermarket Model)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'supermarket_avg_waiting_time_vs_n.png'))
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot supermarket model results from CSV files.')
    parser.add_argument('csv_files', nargs='+', help='List of CSV files to process')
    parser.add_argument('--output_dir', default='plots', help='Directory to save the plots')
    args = parser.parse_args()

    plot_supermarket_avg_waiting_time_vs_n(args.csv_files, args.output_dir)