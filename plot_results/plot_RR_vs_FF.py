import argparse
import pandas as pd
import matplotlib.pyplot as plt

# 📌 Load CSV File
def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# 📌 Plot: Round-Robin vs FIFO for Different Weibull Shapes
def plot_rr_vs_fifo(df, output_file):
    plt.figure(figsize=(8, 6))

    # Filter data where λ, μ, N, d remain constant
    df_filtered = df[
        (df["lambd"] == 0.5) &  # Keeping λ constant (adjust as needed)
        (df["mu"] == 1) & 
        (df["n"] == 10) & 
        (df["d"] == 5)
    ]

    if df_filtered.empty:
        print("⚠️ No matching data found! Check CSV values.")
        return

    # Define FIFO quantum value (a very large number, e.g., 100000)
    FIFO_QUANTUM = 100000

    # Separate FIFO data (quantum equals FIFO_QUANTUM) and Round-Robin data
    df_fifo = df_filtered[df_filtered["quantum"] == FIFO_QUANTUM]
    df_rr = df_filtered[df_filtered["quantum"] != FIFO_QUANTUM]

    # Plot Round-Robin results (for each quantum value)
    rr_quantum_values = sorted(df_rr["quantum"].unique())
    for quantum in rr_quantum_values:
        df_quantum = df_rr[df_rr["quantum"] == quantum]
        weibull_shapes = df_quantum["weibull_shape"]
        avg_times = df_quantum["w"]
        plt.plot(weibull_shapes, avg_times, marker='o', linestyle='-', label=f"Quantum={quantum}")

    # Plot FIFO data as one line
    if not df_fifo.empty:
        fifo_weibull_shapes = df_fifo["weibull_shape"]
        fifo_avg_times = df_fifo["w"]
        plt.plot(fifo_weibull_shapes, fifo_avg_times, marker='s', linestyle='--', color='black', label="FIFO")

    plt.xlabel("Weibull Shape")
    plt.ylabel("Average Time in System (W)")
    plt.title("Round-Robin vs FIFO for Different Weibull Shapes")
    plt.grid()
    plt.legend(title="Scheduling Method")
    plt.savefig(output_file)
    plt.close()

# 📌 Run Plot Function
def main():
    parser = argparse.ArgumentParser(description='Plot results from a CSV file.')
    parser.add_argument('--csv', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output image file.')
    args = parser.parse_args()

    df = load_csv(args.csv)
    plot_rr_vs_fifo(df, args.output)

if __name__ == "__main__":
    main()
