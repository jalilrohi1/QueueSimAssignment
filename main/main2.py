import argparse
import logging
import csv
import sys
import os

# Add the parent directory of 'implementation' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from implementation.queue_sim import Simulation, Queues, MonitorQueueSizes
from random import seed

CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w', 'queue_size', 'waiting_time', 'server_utilization']

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--lambd', type=float, default=0.7, help="arrival rate")
    parser.add_argument('--mu', type=float, default=1, help="service rate")
    parser.add_argument('--max-t', type=float, default=1_000_000, help="maximum time to run the simulation")
    parser.add_argument('--n', type=int, default=1, help="number of servers")
    parser.add_argument('--d', type=int, default=1, help="number of queues to sample")
    parser.add_argument('--use-rr', action='store_true', help="use Round Robin scheduling")
    parser.add_argument('--quantum', type=float, default=1, help="quantum of time for Round Robin")
    parser.add_argument('--monitor-interval', type=float, default=1, help="interval to monitor queue sizes")
    parser.add_argument('--shape', type=float, help="shape parameter for Weibull distribution")
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    args = parser.parse_args()

    params = [getattr(args, column) for column in CSV_COLUMNS[:-4]]

    if any(x <= 0 for x in params):
        logging.error("lambd, mu, max-t, n and d must all be positive")
        exit(1)

    if args.seed:
        seed(args.seed)
    if args.verbose:
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')
    if args.d > args.n:
        logging.error("The number of queues to sample (d) cannot be greater than the number of servers (n).")
        exit(1)
    if args.lambd >= args.mu:
        logging.warning("The system is unstable: lambda >= mu")

    sim = Queues(args.lambd, args.mu, args.n, args.d, args.use_rr, args.quantum, args.monitor_interval, args.shape)
    sim.run(args.max_t)

    completions = sim.completions
    w = ((sum(completions.values()) - sum(sim.arrivals[job_id] for job_id in completions))
         / len(completions))
    print(f"Average time spent in the system: {w}")
    if args.mu == 1 and args.lambd!= 1:
        W_T = 1 / (1 - args.lambd)
        print(f"Theoretical expectation for random server choice (d=1): {W_T}")

    if args.csv is not None:
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(sim.queue_size_log)):
                 writer.writerow([args.lambd, args.mu, args.max_t, args.n, args.d, w, sim.queue_size_log[i], sim.waiting_time_log[i], sim.server_utilization_log[i]])

if __name__ == '__main__':
    main()