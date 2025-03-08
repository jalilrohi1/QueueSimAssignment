import argparse
import logging
import csv
import sys
import os
import threading

# Add the parent directory of 'implementation' to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from implementation.queue_sim import Queues
#from libs.discrete_event_sim import Simulation, Event
from random import seed

CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w', 'queue_size', 'quantum', 'weibull_shape']

# Define multiple parameter lists
param_lists = {
    'lambd': [
        {'lambd': 0.5, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.9, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.95, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.99, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd.csv', 'seed': None, 'verbose': False},

    ],
    'lambd_rr': [
        {'lambd': 0.5, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.9, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/lambd_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.95, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None,'csv': './data/lambd_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.99, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None,'csv': './data/lambd_rr.csv', 'seed': None, 'verbose': False},

    ],
    'd': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 1, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 2, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 10, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv':'./data/d.csv', 'seed': None, 'verbose': False},

    ],
    'd_rr': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 1, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 2, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/d_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 10, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv':'./data/d_rr.csv', 'seed': None, 'verbose': False},

    ],
    'n': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 30, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 50, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 150, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv':'./data/n.csv', 'seed': None, 'verbose': False},

    ],
    'n_rr': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 30, 'd': 1, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 50, 'd': 2, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv': './data/n_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 150, 'd': 10, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': None, 'csv':'./data/n_rr.csv', 'seed': None, 'verbose': False},

    ],
    'shape': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': 0.5, 'csv': './data/shape.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': 1, 'csv': './data/shape.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': 2, 'csv': './data/shape.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': False, 'quantum': 1, 'monitor_interval': 10, 'shape': 3, 'csv':'./data/shape.csv', 'seed': None, 'verbose': False},

    ],
    'shape_rr': [
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 1, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': 0.5, 'csv': './data/shape_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 2, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': 1, 'csv': './data/shape_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 5, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': 2, 'csv': './data/shape_rr.csv', 'seed': None, 'verbose': False},
        {'lambd': 0.7, 'mu': 1, 'max_t': 100000, 'n': 100, 'd': 10, 'use_rr': True, 'quantum': 1, 'monitor_interval': 10, 'shape': 3, 'csv':'./data/shape_rr.csv', 'seed': None, 'verbose': False},

    ],    
    # Add more lists as needed
}

def run_simulation(args):
    params = [getattr(args, column) for column in CSV_COLUMNS[:-4]]
    # corresponds to params = [args.lambd, args.mu, args.max_t, args.n, args.d]

    if any(x <= 0 for x in params):
        logging.error("lambd, mu, max-t, n and d must all be positive")
        exit(1)

    if args.seed:
        seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        # output info on stderr
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')
    if args.d > args.n:
        logging.error("The number of queues to sample (d) cannot be greater than the number of servers (n).")
        exit(1)
    if args.lambd >= args.mu:
        logging.warning("The system is unstable: lambda >= mu")
        
    # Suppress matplotlib font manager logs
    # logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    sim = Queues(args.lambd, args.mu, args.n, args.d, args.use_rr, args.quantum, args.monitor_interval, args.shape)
    sim.run(args.max_t)

    completions = sim.completions
    if len(completions) > 0:
    #w = ((sum(completions.values()) - sum(sim.arrivals_log[job_id] for job_id in completions))
    #     / len(completions))
    # Calculate average time spent only for completed jobs
        completed_arrivals = [sim.arrivals_log[job_id] for job_id in completions]
        w = (sum(completions.values()) - sum(completed_arrivals)) / len(completions)
    else :
        w = 0 # Prevent division by zero

    print(f"Average time spent in the system: {w}")

    if args.mu == 1 and args.lambd != 1:
        W_T=1/(1-args.lambd)
        print(f"Theoretical expectation for random server choice (d=1): {W_T}")    
        val = 1 / (args.mu * (1 - (args.lambd / args.mu)))  # theoretical expectation for random choice
        print(f"Theoretical2 expectation for random server choice: {val}")
    if args.csv is not None:
        args.shape = args.shape if args.shape is not None else "None"
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            # Write headers if file is empty
            if f.tell() == 0:
                writer.writerow(["lambd", "mu", "max_t", "n", "d", "w", "queue_size", "quantum", "weibull_shape"])
            for i in range(len(sim.queue_size_log)):
                writer.writerow([args.lambd, args.mu, args.max_t, args.n, args.d, w, sim.queue_size_log[i], args.quantum, args.shape])

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--lambd', type=float, default=0.7, help="arrival rate")
    parser.add_argument('--mu', type=float, default=1, help="service rate")
    parser.add_argument('--max-t', type=float, default=10000, help="maximum time to run the simulation")
    parser.add_argument('--n', type=int, default=1, help="number of servers")
    parser.add_argument('--d', type=int, default=1, help="number of queues to sample")
    parser.add_argument('--use-rr', action='store_true', help="use Round Robin scheduling")
    parser.add_argument('--quantum', type=float, default=1, help="quantum of time for Round Robin")
    parser.add_argument('--monitor-interval', type=float, default=10, help="interval to monitor queue sizes")
    parser.add_argument('--shape', type=float, help="shape parameter for Weibull distribution")
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--param-list", choices=param_lists.keys(), help="name of the parameter list to use")
    parser.add_argument("--run-all", action='store_true', help="run all predefined parameter lists")
    args = parser.parse_args()

    if args.param_list:
        logging.info(f"Running with specified parameter list: {args.param_list}")
        param_set = param_lists[args.param_list]
        for param in param_set:
            thread_args = argparse.Namespace(**param)
            run_simulation(thread_args)
    elif args.run_all:
        logging.info("Running with all predefined parameter lists")
        threads = []
        for param_list in param_lists.values():
            for param in param_list:
                thread_args = argparse.Namespace(**param)
                thread = threading.Thread(target=run_simulation, args=(thread_args,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()
    else:
        logging.info("Running with command-line parameters")
        run_simulation(args)

if __name__ == '__main__':
    main()