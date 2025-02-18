import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w', 'queue_size']

def plot_mm1_mmn_avg_waiting_time(csv_files, output_dir):
    """
    Plots average waiting time for M/M/1 and M/M/N simulations.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    mm1_file = next(f for f in csv_files if 'mm1' in f)
    mmn_file = next(f for f in csv_files if 'mmn' in f)
    
    mm1_df = pd.read_csv(mm1_file, names=CSV_COLUMNS)
    mmn_df = pd.read_csv(mmn_file, names=CSV_COLUMNS)

    print("MM1 DataFrame columns:", mm1_df.columns)
    print("MMN DataFrame columns:", mmn_df.columns)

    plt.figure(figsize=(10, 6))
    plt.plot(mm1_df['lambd'], mm1_df['w'], marker='o', label='M/M/1')
    plt.plot(mmn_df['lambd'], mmn_df['w'], marker='o', label='M/M/N')
    plt.xlabel('Arrival Rate (lambda)')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time for M/M/1 and M/M/N')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'mm1_mmn_avg_waiting_time.png'))
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot M/M/1 and M/M/N results from CSV files.')
    parser.add_argument('csv_files', nargs='+', help='List of CSV files to process')
    parser.add_argument('--output_dir', default='plots', help='Directory to save the plots')
    args = parser.parse_args()

    plot_mm1_mmn_avg_waiting_time(args.csv_files, args.output_dir)