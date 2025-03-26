import argparse
import configparser
import logging
import random
import sys
import os
import csv
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.backup import Backup
from humanfriendly import parse_size, parse_timespan
from core.node import Node


def save_to_csv(filename, data, headers):
    """Save data to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


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
        cfg = [parse(class_config[name]) for name, parse in parsing_functions]
        nodes.extend(Node(f"{node_class}-{i}", *cfg) for i in range(class_config.getint('number')))
    sim = Backup(nodes, parallel_up_down=args.parallel)
    sim.run(parse_timespan(args.max_t))
    sim.log_info(f"Simulation over")

    # Save simulation data to CSV files
    times = np.array([t / (365 * 24 * 60 * 60) for t in sim.up_bw_wasted.keys()])
    upload_waste = np.array(list(sim.up_bw_wasted.values()))
    download_waste = np.array(list(sim.dw_bw_wasted.values()))
    transfer_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.transfer_counts.keys()])
    transfer_counts = np.array(list(sim.transfer_counts.values()))

    save_to_csv("bandwidth_waste.csv", zip(times, upload_waste, download_waste), ["Time (years)", "Upload Waste", "Download Waste"])
    save_to_csv("data_transfers.csv", zip(transfer_times, transfer_counts), ["Time (years)", "Transfer Counts"])

    if hasattr(sim, "failure_events") and sim.failure_events:
        failure_times = np.array([t / (365 * 24 * 60 * 60) for t in sim.failure_events.keys()])
        failure_counts = np.array(list(sim.failure_events.values()))
        save_to_csv("failures.csv", zip(failure_times, failure_counts), ["Time (years)", "Failure Counts"])

 
if __name__ == '__main__':
    main()