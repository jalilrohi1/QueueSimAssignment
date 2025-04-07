import pandas as pd
import matplotlib.pyplot as plt
import ast
import os
import argparse
import logging
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Load CSV File
def load_csv(file_path):
    logger.info(f"Loading CSV file from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded CSV with {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        raise

# Plot: Round-Robin vs FIFO for Different Weibull Shapes and Server Counts
def plot_rr_vs_fifo(df, output_file):
    # Filter data for constant parameters: λ, μ, d are fixed.
    # We will vary n (number of servers).
    # We'll assume LAMBDA=0.5, MU=1, d=5 are fixed in our simulation.
    df_filtered = df[
        (df["lambd"] == 0.5) &
        (df["mu"] == 1) &
        (df["d"] == 5)
    ]
    if df_filtered.empty:
        print("No matching data found! Check CSV values.")
        return

    # Define server counts (n) to plot.
    server_values = sorted(df_filtered["n"].unique())
    num_plots = len(server_values)
    
    # Create subplots: we'll arrange in a 2x2 grid if 4 server counts.
    rows = cols = 2 if num_plots > 1 else 1
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), squeeze=False)
    fig.suptitle("Round-Robin vs FIFO for Different Weibull Shapes\n(Varying Number of Servers)", fontsize=14)

    FIFO_QUANTUM = 100000

    # Loop over each server count (each subplot)
    for idx, n in enumerate(server_values):
        ax = axes[idx // cols][idx % cols]
        df_n = df_filtered[df_filtered["n"] == n]

        # Separate FIFO and Round-Robin data
        df_fifo = df_n[df_n["quantum"] == FIFO_QUANTUM]
        df_rr = df_n[df_n["quantum"] != FIFO_QUANTUM]

        # Plot Round-Robin data: one line per quantum value
        rr_quantum_values = sorted(df_rr["quantum"].unique())
        for quantum in rr_quantum_values:
            df_quantum = df_rr[df_rr["quantum"] == quantum]
            # For each quantum value, x-axis: Weibull shape, y-axis: average time (w)
            ax.plot(df_quantum["weibull_shape"], df_quantum["w"], marker='o', linestyle='-', label=f"RR Q={quantum}")

        # Plot FIFO data as one line (if available)
        if not df_fifo.empty:
            ax.plot(df_fifo["weibull_shape"], df_fifo["w"], marker='s', linestyle='--', color='black', label="FIFO")

        ax.set_xlabel("Weibull Shape")
        ax.set_ylabel("Avg. Time in System (W)")
        ax.set_title(f"Servers (n) = {n}")
        ax.grid(True)
        ax.legend()

    # If there are unused subplots, remove them.
    total_subplots = rows * cols
    if num_plots < total_subplots:
        for i in range(num_plots, total_subplots):
            fig.delaxes(axes[i // cols][i % cols])
            
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_file)
    plt.close()

# Run Plot Function
def main():
    parser = argparse.ArgumentParser(description="Plot Round-Robin vs FIFO results for different server counts.")
    parser.add_argument('--csv', type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument('--output', type=str, required=True, help="Path to the output image file.")
    args = parser.parse_args()

    # Validate input paths
    if not os.path.exists(args.csv):
        logger.error(f"CSV file not found: {args.csv}")
        raise FileNotFoundError(f"CSV file not found: {args.csv}")

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Load and process data
    logger.info("Starting plot generation...")
    df = load_csv(args.csv)
    plot_rr_vs_fifo(df, args.output)
    logger.info(f"Plot saved successfully to: {args.output}")

if __name__ == "__main__":
    main()
