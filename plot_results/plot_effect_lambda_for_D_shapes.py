import pandas as pd
import matplotlib.pyplot as plt
import ast
import argparse

# Load CSV File
def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# Plot: Effect of λ on Queue Length for Different `d` and Weibull Shapes
def plot_effect_of_lambda_for_d_and_shapes(df,output_file):
    # Define the four `d` values for subplots
    d_values = [1, 2, 5, 10]
    
    # Create a figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Effect of `λ` on Queue Length for Different `d` Values and Weibull Shapes", fontsize=14)

    # Flatten axes array for easy iteration
    axes = axes.flatten()

    for idx, d in enumerate(d_values):
        ax = axes[idx]

        # Filter data where μ = 1, N = 10, quantum = 1, d = current value
        df_filtered = df[
            (df["mu"] == 1) & 
            (df["n"] == 10) & 
            (df["d"] == d) & 
            (df["quantum"] == 1)
        ]

        if df_filtered.empty:
            print(f"No data found for d = {d}. Skipping...")
            continue  # Skip empty plots

        # Get unique Weibull shape values
        shape_values = sorted(df_filtered["weibull_shape"].dropna().unique())

        for shape in shape_values:
            df_shape = df_filtered[df_filtered["weibull_shape"] == shape]

            lambda_values = []
            avg_queue_sizes = []

            for lambda_val in sorted(df_shape["lambd"].unique()):
                subset = df_shape[df_shape["lambd"] == lambda_val]

                # Convert `queue_size` from string representation of list to actual list
                queue_sizes = [
                    ast.literal_eval(q) for q in subset["queue_size"]
                ]
                avg_queue_size = [sum(q) / len(q) for q in queue_sizes]

                lambda_values.append(lambda_val)
                avg_queue_sizes.append(sum(avg_queue_size) / len(avg_queue_size))  # Average across multiple runs

            # Plot for current Weibull shape
            ax.plot(lambda_values, avg_queue_sizes, marker='o', linestyle='-', label=f"Shape={shape}")

        ax.set_xlabel("Arrival Rate λ")
        ax.set_ylabel("Average Queue Length")
        ax.set_title(f"d = {d}")
        ax.set_xticks(lambda_values)  # Ensure all λ values appear on X-axis
        ax.grid()
        ax.legend(title="Weibull Shape")

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_file)

# Run Plot Function
def main():
    parser = argparse.ArgumentParser(description='Plot results from a CSV file.')
    parser.add_argument('--csv', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output image file.')
    args = parser.parse_args()

    df = load_csv(args.csv)
    plot_effect_of_lambda_for_d_and_shapes(df, args.output)


if __name__ == "__main__":
    main()
