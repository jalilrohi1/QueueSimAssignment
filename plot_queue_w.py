#!/usr/bin/env python3

import argparse
import collections
import csv

from matplotlib import pyplot as plt

from queue_sim import CSV_COLUMNS


Row = collections.namedtuple('Row', CSV_COLUMNS)

Params = collections.namedtuple('Params', 'mu max_t n d')

def parse_rows(reader: csv.reader):
    """Parse the rows of the CSV file."""

    for row in reader:
        row = Row(*row)
        yield Row(lambd=float(row.lambd), mu=float(row.mu), max_t=float(row.max_t),
                  n=int(row.n), d=int(row.d), w=float(row.w))


def read_csv(filename: str, mu: list[float], max_t: list[float], n: list[int], d: list[int]) \
      -> dict[Params, list[tuple[float, float]]]:
    """Read the CSV file and return a dictionary with the data.
    
    Keys are the parameters of the simulation, values are lists of pairs with the lambda
    and W values."""

    data = collections.defaultdict(list)

    with open(filename, 'r') as f:
        for row in parse_rows(csv.reader(f)):
            if row.mu in mu and row.max_t in max_t and row.n in n and row.d in d:
                data[Params(row.mu, row.max_t, row.n, row.d)].append((row.lambd, row.w))
    return data


def plot(data: dict[Params, list[tuple[float, float]]], log_scale: bool):
    """Plot the data in the dictionary."""

    if log_scale:
        plt.yscale('log')

    for params, values in data.items():
        lambdas, Ws = zip(*sorted(values))
        plt.plot(lambdas, Ws, label=f'mu={params.mu}, max_t={params.max_t}, n={params.n}, d={params.d}')

    plt.xlabel('lambda')
    plt.ylabel('W')
    plt.legend(loc=0)
    plt.grid()


def main():

    description = """Plot the W metric of an MMN queue from a CSV file, use lambda as x-axis.
    
    You can specify multiple values for mu, max-t, n and d. The program will plot the W metric for
    all the combinations of these values that are present in the CSV file.

    The CSV file must have the following columns: lambd, mu, max_t, n, d, w.

    Example:
        plot_queue_w.py out.csv --max-t 100000 -d 1 2 5 10 -n 10
    will plot the W metric for d=1, 2, 5 and 10, with n=10 and max_t=100000.
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Plot the W metric of an MMN queue from a CSV file, use lambda as x-axis.")
    parser.add_argument('filename', help='name of the CSV file with the results')
    parser.add_argument('--mu', type=float, nargs='*', default=[1], help="service rate")
    parser.add_argument('--max-t', type=float, nargs='*', default=[1_000_000],
                        help="maximum time the simulation was run")
    parser.add_argument('--n', type=int, nargs='*', default=[1], help="number of servers")
    parser.add_argument('--d', type=int, nargs='*', default=[1], help="number of queues to sample")
    parser.add_argument('--log-scale', action='store_true',
                        help="use a logarithmic scale for the y-axis")
    args = parser.parse_args()

    data = read_csv(args.filename, args.mu, args.max_t, args.n, args.d)
    plot(data, args.log_scale)
    plt.show()

if __name__ == '__main__':
    main()