import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

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

    # --- M/M/1 and M/M/N Analysis ---
    plot_mm1_mmn_results(csv_files, output_dir)

    # --- Supermarket Model Analysis ---
    plot_supermarket_results(csv_files, output_dir)

    # --- Round Robin Analysis ---
    plot_round_robin_results(csv_files, output_dir)

def plot_mm1_mmn_results(csv_files, output_dir):
    """
    Plots results for M/M/1 and M/M/N simulations.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    mm1_files = [f for f in csv_files if 'mm1' in f]
    mmn_files = [f for f in csv_files if 'mmn' in f]

    if mm1_files:
        mm1_df = pd.concat([pd.read_csv(f) for f in mm1_files])
    else:
        print("No M/M/1 files found.")
        return

    if mmn_files:
        mmn_df = pd.concat([pd.read_csv(f) for f in mmn_files])
    else:
        print("No M/M/N files found.")
        return

    # --- Plot Average Waiting Time ---
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

def plot_supermarket_results(csv_files, output_dir):
    """
    Plots results for supermarket model simulations.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    supermarket_n_files = [f for f in csv_files if 'supermarket_n' in f]
    supermarket_d_files = [f for f in csv_files if 'supermarket_d' in f]

    if supermarket_n_files:
        supermarket_n_df = pd.concat([pd.read_csv(f) for f in supermarket_n_files])
    else:
        print("No supermarket_n files found.")
        return

    if supermarket_d_files:
        supermarket_d_df = pd.concat([pd.read_csv(f) for f in supermarket_d_files])
    else:
        print("No supermarket_d files found.")
        return

    # --- Plot Average Waiting Time vs. n ---
    plt.figure(figsize=(10, 6))
    plt.plot(supermarket_n_df['n'], supermarket_n_df['w'], marker='o', label='Supermarket Model')
    plt.xlabel('Number of Servers (n)')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Number of Servers (Supermarket Model)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'supermarket_avg_waiting_time_vs_n.png'))
    plt.close()

    # --- Plot Average Waiting Time vs. d ---
    plt.figure(figsize=(10, 6))
    plt.plot(supermarket_d_df['d'], supermarket_d_df['w'], marker='o', label='Supermarket Model')
    plt.xlabel('Sample Size (d)')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Sample Size (Supermarket Model)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'supermarket_avg_waiting_time_vs_d.png'))
    plt.close()

    # --- Plot Queue Length Distribution ---
    plot_queue_length_distribution(supermarket_d_df, output_dir, 'supermarket')

def plot_round_robin_results(csv_files, output_dir):
    """
    Plots results for Round Robin simulations.

    Args:
        csv_files (list): List of CSV file paths.
        output_dir (str): Directory to save the plots.
    """

    round_robin_files = [f for f in csv_files if 'round_robin' in f]
    round_robin_supermarket_files = [f for f in csv_files if 'round_robin_supermarket' in f]

    if round_robin_files:
        round_robin_df = pd.concat([pd.read_csv(f) for f in round_robin_files])
    else:
        print("No round_robin files found.")
        return

    if round_robin_supermarket_files:
        round_robin_supermarket_df = pd.concat([pd.read_csv(f) for f in round_robin_supermarket_files])
    else:
        print("No round_robin_supermarket files found.")
        return

    # --- Plot Average Waiting Time vs. Weibull Shape (Round Robin) ---
    plt.figure(figsize=(10, 6))
    plt.plot(round_robin_df['shape'], round_robin_df['w'], marker='o', label='Round Robin (d=1)')
    plt.xlabel('Weibull Shape')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Weibull Shape (Round Robin)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'round_robin_avg_waiting_time_vs_shape.png'))
    plt.close()

    # --- Plot Average Waiting Time vs. Weibull Shape (Round Robin with Supermarket) ---
    plt.figure(figsize=(10, 6))
    plt.plot(round_robin_supermarket_df['shape'], round_robin_supermarket_df['w'], marker='o', label='Round Robin with Supermarket (d=5)')
    plt.xlabel('Weibull Shape')
    plt.ylabel('Average Waiting Time (w)')
    plt.title('Average Waiting Time vs. Weibull Shape (Round Robin with Supermarket)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'round_robin_supermarket_avg_waiting_time_vs_shape.png'))
    plt.close()

    # --- Plot Queue Length Distribution ---
    plot_queue_length_distribution(round_robin_df, output_dir, 'round_robin')

def plot_queue_length_distribution(df, output_dir, sim_type):
    """
    Plots queue length distribution as histograms for different lambda and d values.

    Args:
        df (DataFrame): DataFrame containing the data.
        output_dir (str): Directory to save the plots.
        sim_type (str): Type of simulation ('supermarket' or 'round_robin').
    """

    for lambd_value in df['lambd'].unique():
        for d_value in df['d'].unique():
            subset = df[(df['lambd'] == lambd_value) & (df['d'] == d_value)]
            queue_sizes =[]
            for queue_size_list in subset['queue_size']:
                queue_sizes.extend(eval(queue_size_list))

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