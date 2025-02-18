import pandas as pd
import matplotlib.pyplot as plt
import ast

# 📌 Load CSV File
def load_csv(file_path):
    #df = pd.read_csv(file_path)
    df = pd.read_csv(file_path, names=["lambd", "mu", "max_t", "n", "d", "w", "queue_size","quantum","weibull_shape"], skiprows=1)
    return df

# 📌 Plot 1: Queue Length Distribution (CDF)
def plot_queue_length_distribution(df):
    plt.figure(figsize=(8, 6))

    for name, group in df.groupby("n"):  # Group by number of servers (N)
        queue_lengths = []
        for q in group["queue_size"]:
            try:
                queue_lengths.extend(ast.literal_eval(q))  # Convert string list to actual list
            except (ValueError, SyntaxError):
                print(f"Skipping malformed queue_size value: {q}")
        
        sorted_lengths = sorted(queue_lengths)
        cdf = [i / len(sorted_lengths) for i in range(len(sorted_lengths))]

        plt.plot(sorted_lengths, cdf, label=f"N={name}")

    plt.xlabel("Queue Length")
    plt.ylabel("Fraction of Queues (CDF)")
    plt.title("Queue Length Distribution (Supermarket Model)")
    plt.legend()
    plt.grid()
    #plt.show()
    plt.savefig("queue_length_distribution.png")

# 📌 Plot 2: Effect of Increasing `d` (Sample Size) on Queue Lengths
def plot_effect_of_d(df):
    plt.figure(figsize=(8, 6))

    for d_val in sorted(df["d"].unique()):
        subset = df[df["d"] == d_val]
        avg_queue_size = [sum(ast.literal_eval(q)) / len(ast.literal_eval(q)) for q in subset["queue_size"]]

        plt.plot(subset["n"], avg_queue_size, marker='o', label=f"d={d_val}")

    plt.xlabel("Number of Servers (N)")
    plt.ylabel("Average Queue Length")
    plt.title("Effect of Increasing Sample Dimension `d`")
    plt.legend()
    plt.grid()
    #plt.show()
    plt.savefig("effect_of_d_onQlenth.png")  # Save instead of showing

# 📌 Plot 3: Effect of Increasing Lambda (λ) on Queue Lengths
def plot_effect_of_lambda(df):
    plt.figure(figsize=(8, 6))

    for name, group in df.groupby("d"):
        avg_queue_size = [sum(ast.literal_eval(q)) / len(ast.literal_eval(q)) for q in group["queue_size"]]
        plt.plot(group["lambd"], avg_queue_size, marker='o', label=f"d={name}")

    plt.xlabel("Arrival Rate (λ)")
    plt.ylabel("Average Queue Length")
    plt.title("Effect of Increasing λ on Queue Lengths")
    plt.legend()
    plt.grid()
    #plt.show()
    plt.savefig("effect_ofLamda_onQlenth.png")  # Save instead of showing

# 📌 Plot 4: Round-Robin vs. FIFO for Different Weibull Shapes
def plot_round_robin_vs_fifo(df):
    plt.figure(figsize=(8, 6))

    if "weibull_shape" in df.columns:  # Ensure the column exists
        for q_val in sorted(df["quantum"].unique()):
            subset = df[df["quantum"] == q_val]
            plt.plot(subset["weibull_shape"], subset["w"], marker='o', label=f"Quantum={q_val}")

        plt.xlabel("Weibull Shape")
        plt.ylabel("Average Time in System (W)")
        plt.title("Round-Robin vs FIFO for Different Weibull Shapes")
        plt.legend()
        plt.grid()
        #plt.show()
        plt.savefig("RR_vs_Fifo_Sahpes.png")  # Save instead of showing

    else:
        print("Weibull shape data is missing in CSV.")

# 📌 Run All Plots
def main():
    file_path = "./data/shape.csv"  # 🔹 Change to your actual CSV file name
    df = load_csv(file_path)
    
    plot_queue_length_distribution(df)
    plot_effect_of_d(df)
    plot_effect_of_lambda(df)
    plot_round_robin_vs_fifo(df)

if __name__ == "__main__":
    main()
