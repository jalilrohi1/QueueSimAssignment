import matplotlib.pyplot as plt
import numpy as np
import os
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)  # suppress matplotlib logging

# Ensure the plots directory exists
os.makedirs("plots", exist_ok=True)

def plot_bandwidth_waste(times, upload_waste, download_waste):
    """Plot upload and download bandwidth waste over time."""
    plt.figure(figsize=(10, 6))
    plt.plot(times, upload_waste, color='blue', label="Upload Bandwidth Waste")
    plt.plot(times, download_waste, color='red', label="Download Bandwidth Waste")
    plt.xlabel("Time (years)")
    plt.ylabel("Wasted Bandwidth")
    plt.title("Bandwidth Waste Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/bandwidth_waste_over_time.png")
    #plt.show()

def plot_smoothed_bandwidth_waste(times, upload_waste, download_waste, window_size=10):
    """Plot smoothed bandwidth waste using a configurable moving average."""
    if len(upload_waste) < window_size:
        window_size = max(1, len(upload_waste) // 5)  # Prevents excessive smoothing on small data

    smooth_upload_waste = np.convolve(upload_waste, np.ones(window_size) / window_size, mode="valid")
    smooth_download_waste = np.convolve(download_waste, np.ones(window_size) / window_size, mode="valid")
    smooth_times = times[: len(smooth_upload_waste)]

    plt.figure(figsize=(10, 6))
    plt.plot(smooth_times, smooth_upload_waste, color="blue", linewidth=2, label=f"Smoothed Upload Waste (Window={window_size})")
    plt.plot(smooth_times, smooth_download_waste, color="red", linewidth=2, label=f"Smoothed Download Waste (Window={window_size})")
    plt.xlabel("Time (years)")
    plt.ylabel("Smoothed Bandwidth Waste")
    plt.title("Smoothed Bandwidth Waste Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"./plots/smoothed_bandwidth_waste_w{window_size}.png")


def plot_smoothed_bandwidth_waste1122(times, upload_waste, download_waste, window_size=50):
    """Plot smoothed bandwidth waste using a moving average."""
    smooth_upload_waste = np.convolve(upload_waste, np.ones(window_size) / window_size, mode="valid")
    smooth_download_waste = np.convolve(download_waste, np.ones(window_size) / window_size, mode="valid")
    smooth_times = times[: len(smooth_upload_waste)]

    plt.figure(figsize=(10, 6))
    plt.plot(smooth_times, smooth_upload_waste, color="blue", linewidth=2, label="Smoothed Upload Waste")
    plt.plot(smooth_times, smooth_download_waste, color="red", linewidth=2, label="Smoothed Download Waste")
    plt.xlabel("Time (years)")
    plt.ylabel("Smoothed Bandwidth Waste")
    plt.title("Smoothed Bandwidth Waste Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/smoothed_bandwidth_waste.png")
    #plt.show()

def plot_data_transfers(transfer_times, transfer_counts):
    """Plot the number of data transfers over time."""
    plt.figure(figsize=(10, 6))
    plt.plot(transfer_times, transfer_counts, color="green", label="Number of Data Transfers")
    plt.xlabel("Time (years)")
    plt.ylabel("Data Transfers")
    plt.title("Data Transfers Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/data_transfers_over_time.png")
    #plt.show()

def plot_used_vs_wasted_bandwidth(times, used_bandwidth, wasted_bandwidth):
    """Compare used bandwidth vs wasted bandwidth over time with a stacked bar chart."""
    plt.figure(figsize=(10, 6))
    plt.bar(times, used_bandwidth, color="green", label="Used Bandwidth")
    plt.bar(times, wasted_bandwidth, bottom=used_bandwidth, color="red", label="Wasted Bandwidth")  # Stack it
    plt.xlabel("Time (years)")
    plt.ylabel("Bandwidth")
    plt.title("Used vs. Wasted Bandwidth Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/used_vs_wasted_bandwidth_stacked.png")


def plot_used_vs_wasted_bandwidth1122(times, used_bandwidth, wasted_bandwidth):
    """Compare used bandwidth vs wasted bandwidth over time."""
    plt.figure(figsize=(10, 6))
    plt.bar(times, used_bandwidth, color="green", alpha=0.6, label="Used Bandwidth")
    plt.bar(times, wasted_bandwidth, color="red", alpha=0.6, label="Wasted Bandwidth")
    plt.xlabel("Time (years)")
    plt.ylabel("Bandwidth")
    plt.title("Used vs. Wasted Bandwidth Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/used_vs_wasted_bandwidth.png")
    #plt.show()

def plot_bandwidth_waste_distribution(upload_waste, download_waste):
    """Plot a histogram of bandwidth waste distribution."""
    plt.figure(figsize=(10, 6))
    plt.hist(upload_waste, bins=50, alpha=0.6, color="blue", label="Upload Waste")
    plt.hist(download_waste, bins=50, alpha=0.6, color="red", label="Download Waste")
    plt.xlabel("Wasted Bandwidth")
    plt.ylabel("Frequency")
    plt.title("Distribution of Bandwidth Waste")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/bandwidth_waste_distribution.png")
    #plt.show()

def plot_failures_vs_bandwidth_waste(failure_times, failure_counts, times, upload_waste, download_waste):
    """Plot failures vs bandwidth waste correlation."""
    plt.figure(figsize=(10, 6))
    plt.scatter(failure_times, failure_counts, color="purple", label="Failures")
    plt.plot(times, upload_waste, color="blue", alpha=0.5, label="Upload Waste")
    plt.plot(times, download_waste, color="red", alpha=0.5, label="Download Waste")
    plt.xlabel("Time (years)")
    plt.ylabel("Failures / Bandwidth Waste")
    plt.title("Impact of Failures on Bandwidth Waste")
    plt.legend()
    plt.grid(True)
    plt.savefig("./plots/failures_vs_bandwidth_waste.png")
    #plt.show()
    
def plot_failures_vs_bandwidth_waste_with_availability(failure_times, failure_counts, times, upload_waste, download_waste, online_nodes):
    """Plot failures vs bandwidth waste with system-wide availability overlay."""
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.scatter(failure_times, failure_counts, color="purple", label="Failures")
    ax1.plot(times, upload_waste, color="blue", alpha=0.5, label="Upload Waste")
    ax1.plot(times, download_waste, color="red", alpha=0.5, label="Download Waste")
    ax1.set_xlabel("Time (years)")
    ax1.set_ylabel("Failures / Bandwidth Waste")
    ax1.legend()

    # Add a second y-axis for system-wide availability
    ax2 = ax1.twinx()
    ax2.plot(times, [online_nodes.get(t, 0) for t in times], color="green", linestyle="dashed", label="Online Nodes")
    ax2.set_ylabel("Online Nodes")
    ax2.legend(loc="upper right")

    plt.title("Impact of Failures on Bandwidth Waste with System Availability")
    plt.grid(True)
    plt.savefig("./plots/failures_vs_bandwidth_waste_with_availability.png")

def plot_used_vs_wasted_bandwidth_dual_axis(times, used_bandwidth, wasted_bandwidth):
    """Compare used bandwidth vs wasted bandwidth over time with a dual-axis plot."""
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.set_xlabel("Time (years)")
    ax1.set_ylabel("Used Bandwidth", color="green")
    ax1.plot(times, used_bandwidth, color="green", label="Used Bandwidth")
    ax1.tick_params(axis="y", labelcolor="green")

    ax2 = ax1.twinx()  # Create a second y-axis
    ax2.set_ylabel("Wasted Bandwidth", color="red")
    ax2.plot(times, wasted_bandwidth, color="red", linestyle="dashed", label="Wasted Bandwidth")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title("Used vs. Wasted Bandwidth Over Time (Dual-Axis)")
    fig.tight_layout()
    plt.savefig("./plots/used_vs_wasted_bandwidth_dual_axis.png")
