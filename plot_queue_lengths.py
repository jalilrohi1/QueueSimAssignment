import argparse
import csv
import collections
import matplotlib.pyplot as plt
import numpy as np

# ... (Helper functions to read and parse CSV data) ...

def plot_queue_lengths(data, log_scale=False):
    """Plot queue length distribution from experimental data."""

    if log_scale:
        plt.yscale('log')

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))  # Create 2x2 subplots

    for (d, values), ax in zip(data.items(), axs.flatten()):
        queue_lengths = np.array(values)
        max_queue_size = queue_lengths.max()
        fractions = []
        for x in range(max_queue_size + 1):
            fraction = np.sum(queue_lengths >= x) / len(queue_lengths)
            fractions.append(fraction)
        ax.plot(range(max_queue_size + 1), fractions)
        ax.set_xlabel("Queue Size")
        ax.set_ylabel("Fraction of Queues")
        ax.set_title(f"d={d}")
        ax.grid()

    plt.tight_layout()
    plt.show()

def main():
    # ... (Argument parsing) ...

    data = read_csv(args.filename, args.d)  # Read data from CSV
    plot_queue_lengths(data, args.log_scale)  # Plot the queue lengths

if __name__ == '__main__':
    main()