import numpy as np
import matplotlib.pyplot as plt

def theoretical_queue_length(d, lambd, mu, max_queue_size):
    rho = lambd / mu
    fractions = []
    for x in range(max_queue_size + 1):
        fraction = (1 - rho) * (rho ** x)
        fractions.append(fraction)
    return fractions

def main():
    lambd_values = [0.5,0.9, 0.95, 0.99]  # Different lambda values to plot
    mu = 1.0
    queue_counts = [1, 2, 5, 10]  # Different number of queues to plot
    max_queue_size = 14  # Maximum queue size to plot

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))  # Create a 2x2 grid of subplots

    for i, d in enumerate(queue_counts):
        ax = axs[i // 2, i % 2]  # Select the subplot
        for lambd in lambd_values:
            fractions = theoretical_queue_length(d, lambd, mu, max_queue_size)
            ax.plot(range(max_queue_size + 1), fractions, label=f"λ={lambd}")
        ax.set_xlabel("Queue Size")
        ax.set_ylabel("Fraction of Queues")
        ax.set_ylim(0, 1)  # Set y-axis limits from 0 to 1
        ax.set_title(f"Theoretical Queue Length for d={d}")
        ax.legend()
        ax.grid()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()