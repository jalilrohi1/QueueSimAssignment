import csv
import numpy as np
from plot_utils import (
    plot_bandwidth_waste,
    plot_smoothed_bandwidth_waste,
    plot_data_transfers,
    plot_used_vs_wasted_bandwidth,
    plot_bandwidth_waste_distribution,
    plot_failures_vs_bandwidth_waste,
    plot_failures_vs_bandwidth_waste_with_availability,
    plot_used_vs_wasted_bandwidth_dual_axis
)


def read_csv(filename):
    """Read data from a CSV file."""
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip the header
        data = np.array(list(reader), dtype=float)
    return data


def main():
    # Read data from CSV files
    bandwidth_data = read_csv("bandwidth_waste.csv")
    transfer_data = read_csv("data_transfers.csv")

    times = bandwidth_data[:, 0]
    upload_waste = bandwidth_data[:, 1]
    download_waste = bandwidth_data[:, 2]
    transfer_times = transfer_data[:, 0]
    transfer_counts = transfer_data[:, 1]

    # Compute used and wasted bandwidth
    used_bandwidth = upload_waste + download_waste
    wasted_bandwidth = upload_waste + download_waste

    # Generate plots
    plot_bandwidth_waste(times, upload_waste, download_waste)
    plot_smoothed_bandwidth_waste(times, upload_waste, download_waste)
    plot_data_transfers(transfer_times, transfer_counts)
    plot_used_vs_wasted_bandwidth(times, used_bandwidth, wasted_bandwidth)
    plot_bandwidth_waste_distribution(upload_waste, download_waste)

    # Check for failures and plot if data exists
    try:
        failure_data = read_csv("failures.csv")
        failure_times = failure_data[:, 0]
        failure_counts = failure_data[:, 1]
        plot_failures_vs_bandwidth_waste(failure_times, failure_counts, times, upload_waste, download_waste)
        plot_failures_vs_bandwidth_waste_with_availability(failure_times, failure_counts, times, upload_waste, download_waste, None)
    except FileNotFoundError:
        print("No failure data found. Skipping failure plots.")


if __name__ == '__main__':
    main()