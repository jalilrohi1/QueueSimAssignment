import argparse
import pandas as pd
import matplotlib.pyplot as plt
import ast

# 📌 Load CSV File
def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# 📌 Plot: Effect of `d` on Queue Length for Different Weibull Shapes and `N` Values
def plot_effect_of_d_for_shapes(df):
    # Define the four `N` values for subplots
    n_values = [10, 20, 50, 100]
    
    # Create a figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Effect of `d` on Queue Length for Different `N` Values and Weibull Shapes", fontsize=14)

    # Flatten axes array for easy iteration
    axes = axes.flatten()

    for idx, n in enumerate(n_values):
        ax = axes[idx]

        # Filter data where λ = 0.7, μ = 1, quantum = 1, N = current value
        df_filtered = df[
            (df["lambd"] == 0.7) & 
            (df["mu"] == 1) & 
            (df["n"] == n) & 
            (df["quantum"] == 1)
        ]

        # Get unique Weibull shape values
        shape_values = sorted(df_filtered["weibull_shape"].unique())

        for shape in shape_values:
            df_shape = df_filtered[df_filtered["weibull_shape"] == shape]

            d_values = []
            avg_queue_sizes = []

            for d_val in sorted(df_shape["d"].unique()):
                subset = df_shape[df_shape["d"] == d_val]

                # Convert `queue_size` from string representation of list to actual list
                avg_queue_size = [
                    sum(ast.literal_eval(q)) / len(ast.literal_eval(q)) for q in subset["queue_size"]
                ]

                d_values.append(d_val)
                avg_queue_sizes.append(sum(avg_queue_size) / len(avg_queue_size))  # Average across multiple runs

            # 📌 Plot for current Weibull shape
            ax.plot(d_values, avg_queue_sizes, marker='o', linestyle='-', label=f"Shape={shape}")

        ax.set_xlabel("Sample Size `d` (Supermarket Model)")
        ax.set_ylabel("Average Queue Length")
        ax.set_title(f"N = {n} Servers")
        ax.set_xticks(sorted(df_filtered["d"].unique()))  # Ensure all `d` values appear on X-axis
        ax.grid()
        ax.legend(title="Weibull Shape")

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    #plt.show()
    plt.savefig("effect_of_d_for_shapes.png")

# 📌 Run Plot Function
def main():
    parser = argparse.ArgumentParser(description='Plot results from a CSV file.')
    parser.add_argument('--csv', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output image file.')
    args = parser.parse_args()

    df = load_csv(args.csv)
    plot_effect_of_d_for_shapes(df, args.output)


if __name__ == "__main__":
    main()
