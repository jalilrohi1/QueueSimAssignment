import argparse
import configparser
import logging
import random
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from core.node import Node
from  .core.backup import Backup
from humanfriendly import format_timespan, parse_size, parse_timespan
logging.getLogger('matplotlib').setLevel(logging.WARNING)  # suppress matplotlib logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="configuration file")
    parser.add_argument("--max-t", default="100 years")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--parallel", action='store_true', help="Enable parallel uploads and downloads")

    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')  # output info on stdout

    # functions to parse every parameter of peer configuration
    parsing_functions = [
        ('n', int), ('k', int),
        ('data_size', parse_size), ('storage_size', parse_size),
        ('upload_speed', parse_size), ('download_speed', parse_size),
        ('average_uptime', parse_timespan), ('average_downtime', parse_timespan),
        ('average_lifetime', parse_timespan), ('average_recover_time', parse_timespan),
        ('arrival_time', parse_timespan)
    ]

    config = configparser.ConfigParser()
    config.read(args.config)
    nodes = []  # we build the list of nodes to pass to the Backup class
    for node_class in config.sections():
        class_config = config[node_class]
        # list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        cfg = [parse(class_config[name]) for name, parse in parsing_functions]
        # the `callable(p1, p2, *args)` idiom is equivalent to `callable(p1, p2, args[0], args[1], ...)
        nodes.extend(Node(f"{node_class}-{i}", *cfg) for i in range(class_config.getint('number')))
    sim = Backup(nodes,parallel_up_down=args.parallel)
    sim.run(parse_timespan(args.max_t))
    sim.log_info(f"Simulation over")

    import numpy as np
    from utils.plot_utils import (
        plot_bandwidth_waste,
        plot_smoothed_bandwidth_waste,
        plot_data_transfers,
        plot_used_vs_wasted_bandwidth,
        plot_bandwidth_waste_distribution,
        plot_failures_vs_bandwidth_waste,
        plot_failures_vs_bandwidth_waste_with_availability,
        plot_used_vs_wasted_bandwidth_dual_axis
    )

    # Convert seconds to years
    times = np.array([t / (365 * 24 * 60 * 60) for t in sim.up_bw_wasted.keys()])
    upload_waste = np.array(list(sim.up_bw_wasted.values()))
    download_waste = np.array(list(sim.dw_bw_wasted.values()))

    transfer_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.transfer_counts.keys()])
    transfer_counts = np.array(list(sim.transfer_counts.values()))

    # Compute used bandwidth
    used_bandwidth = upload_waste + download_waste
    wasted_bandwidth = upload_waste + download_waste

    # Only access `failure_events` if it exists
    if hasattr(sim, "failure_events") and sim.failure_events:
        failure_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.failure_events.keys()])
        failure_counts = np.array(list(sim.failure_events.values()))

        # Generate plots including failures
        plot_failures_vs_bandwidth_waste(failure_times, failure_counts, times, upload_waste, download_waste)

    # Generate standard plots
    plot_bandwidth_waste(times, upload_waste, download_waste)
    plot_smoothed_bandwidth_waste(times, upload_waste, download_waste)
    plot_data_transfers(transfer_times, transfer_counts)
    plot_used_vs_wasted_bandwidth(times, used_bandwidth, wasted_bandwidth)
    plot_bandwidth_waste_distribution(upload_waste, download_waste)
    plot_used_vs_wasted_bandwidth_dual_axis(times, used_bandwidth, wasted_bandwidth)
    plot_failures_vs_bandwidth_waste_with_availability(failure_times, failure_counts, times, upload_waste, download_waste, sim.online_nodes)


if __name__ == '__main__':
    main()
