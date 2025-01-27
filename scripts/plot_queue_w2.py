import argparse
import collections
import csv
from matplotlib import pyplot as plt
from queue_sim import CSV_COLUMNS

Row = collections.namedtuple('Row', CSV_COLUMNS)
Params = collections.namedtuple('Params', 'mu max_t n d w')

class Params:
         def __init__(self, mu, max_t, n, d, w):  # Add 'w' here
             self.mu = mu
             self.max_t = max_t
             self.n = n
             self.d = d
             self.w = w  # Initialize w
             
def parse_rows(reader: csv.reader):
    """Parse the rows of the CSV file."""
    next(reader)  # Skip the header row
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
                data[Params(row.mu, row.max_t, row.n, row.d,row.w)].append((row.lambd, row.w))
    return data

def plot(data: dict[Params, list[tuple[float, float]]], log_scale: bool, output_file: str):
    """Plot the data in the dictionary."""

    if log_scale:
        plt.yscale('log')

    for params, values in data.items():
        lambdas, Ws = zip(*sorted(values))
        plt.plot(lambdas, Ws, label=f'mu={params.mu}, max_t={params.max_t}, n={params.n}, d={params.d}')

    plt.xlabel('Lambda')
    plt.ylabel('w')
    plt.legend()
    plt.savefig(output_file)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', help="CSV file containing the data")
    parser.add_argument('--mu', type=float, nargs='+', required=True, help="Service rates to plot")
    parser.add_argument('--max-t', type=float, nargs='*', default=[1_000_000], help="Maximum times to plot")
    parser.add_argument('--n', type=int, nargs='*', default=[1], help="Number of servers to plot")
    parser.add_argument('--d', type=int, nargs='*', default=[1], help="Number of queues to sample")
    parser.add_argument('--log-scale', action='store_true', help="Use logarithmic scale for y-axis")
    parser.add_argument('--output-file', type=str, default='plot.png', help="Output file for the plot")
    args = parser.parse_args()

    data = read_csv(args.filename, args.mu, args.max_t, args.n, args.d)
    plot(data, args.log_scale, args.output_file)

if __name__ == '__main__':
    main()