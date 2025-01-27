

### Queue Simulation and Analysis

```markdown

This repository contains a set of scripts for simulating queue systems and analyzing the results.
The main components include running simulations with varying parameters and plotting the results
to visualize the performance of the queue systems.

## Prerequisites

- Python 3.x
- `pandas` library
- `matplotlib` library

You can install the required libraries using pip:

```sh
pip install pandas matplotlib
```

## Repository Structure

- 

queue_experiments.sh

: A Bash script to run multiple queue simulations with varying parameters.
- 

main.py

: The main Python script to run a single queue simulation.
- 

th2.py

: A Python script to plot the results of the simulations from a CSV file.
- 

data

: Directory to store the output CSV files from the simulations.
- 

plot_results

: Directory to store the generated plots.

## Usage

### Running Simulations

To run multiple simulations with varying parameters, use the `queue_experiments.sh` script:

```sh
bash ./automation/queue_experiments.sh [options]
```

#### Options

- `--lambdas`: Comma-separated list of arrival rates (lambda) to test.
- `--ds`: Comma-separated list of values for `d` (number of servers to choose from).
- `--mu`: Service rate (default: 1).
- `--n`: Number of servers (default: 10).
- `--max-t`: Maximum simulation time (default: 100000).
- `--monitor-interval`: Monitoring interval (default: 10).
- `--csv`: Path to the output CSV file (default: 

out.csv

).

#### Example

```sh
bash ./automation/queue_experiments.sh --lambdas "0.5,0.7,0.9" --ds "1,2,5" --mu 1 --n 10 --max-t 100000 --monitor-interval 10 --csv ./data/out.csv
```

### Plotting Results

To plot the results from a CSV file, use the `th2.py` script:

```sh
python3 ./plot_results/th2.py --csv <path_to_csv_file> --output <path_to_output_image>
```

#### Arguments

- `--csv`: Path to the input CSV file containing the simulation data.
- `--output`: Path to the output image file where the plot will be saved.

#### Example

```sh
python3 ./plot_results/th2.py --csv ./data/new_out.csv --output ./plot_results/queue_size_fractions.png
```

## CSV File Format

The input CSV file should have the following columns:

1. `lambda`: Arrival rate
2. `mu`: Service rate
3. `max_t`: Maximum simulation time
4. `n`: Number of servers
5. `d`: Number of servers to choose from
6. `average_time_spent`: Average time spent in the system
7. `queue_sizes`: List of queue sizes
8. `waiting_times`: List of waiting times
9. `server_utilizations`: List of server utilizations

## Script Explanation

### `queue_experiments.sh`

This Bash script runs multiple queue simulations with varying parameters. It iterates over different values of `lambda` and `d`, running the `main.py` script for each combination and saving the results to a CSV file.

#### How It Works

1. **Default Parameters**: The script defines default values for `lambda`, `d`, `mu`, `n`, `max_t`, `monitor_interval`, and `csv_file`.
2. **Command-Line Argument Parsing**: The script uses a `while` loop and a `case` statement to parse command-line arguments and override default values.
3. **Running Simulations**: The script uses nested loops to iterate over all combinations of `lambda` and `d`, running the `main.py` script for each combination and saving the results to the specified CSV file.

### `main.py`

This Python script runs a single queue simulation based on the provided parameters. It simulates the queue system and outputs the results, including average time spent in the system, queue sizes, waiting times, and server utilizations.

#### How It Works

1. **Argument Parsing**: The script uses `argparse` to parse command-line arguments for `lambda`, `mu`, `max_t`, `n`, `d`, `monitor_interval`, `shape`, and `csv`.
2. **Simulation**: The script initializes a queue simulation with the specified parameters and runs the simulation for the specified maximum time.
3. **Output**: The script calculates the average time spent in the system and saves the results to the specified CSV file.

### `th2.py`

This Python script reads the simulation results from a CSV file and generates a plot. The plot shows the fraction of queues with at least a certain size (Q) for different values of `lambda` and `d`. The script creates a single image with four subplots, each representing a different value of `d` (1, 2, 5, 10).

#### How It Works

1. **Argument Parsing**: The script uses `argparse` to parse command-line arguments for the input CSV file and the output image file.
2. **Data Reading and Processing**: The script reads the CSV file using `pandas` and processes the data to convert string representations of lists to actual lists.
3. **Plotting**: The script creates a figure with four subplots using `matplotlib`. Each subplot represents a different value of `d` and shows the fraction of queues with at least a certain size (Q) for different values of `lambda`.
4. **Saving the Plot**: The script saves the generated plot to the specified output image file.

### Plot Example

The generated plot will contain four subplots, each representing a different value of `d` (1, 2, 5, 10). Each subplot will show the fraction of queues with at least a certain size (Q) for different values of `lambda`.

### Project Structure

```plaintext
.
├── automation
│   └── queue_experiments.sh   # Bash script to run multiple queue simulations with varying parameters
├── data                       # Directory to store the output CSV files from the simulations
│   └── new_out.csv            # Example output CSV file
├── main
│   └── main.py                # Main Python script to run a single queue simulation
├── plot_results
│   └── th2.py                 # Python script to plot the results of the simulations from a CSV file
├── README.md                  # Project README file
└── LICENSE                    # Project license file
```

### Explanation

- **automation/**
  - `queue_experiments.sh`: A Bash script to run multiple queue simulations with varying parameters. It iterates over different values of `lambda` and `d`, running the `main.py` script for each combination and saving the results to a CSV file.

- **data/**
  - `new_out.csv`: Example output CSV file containing the results of the simulations. This directory is used to store the output CSV files generated by the `queue_experiments.sh` script.

- **main/**
  - `main.py`: The main Python script to run a single queue simulation. It simulates the queue system based on the provided parameters and outputs the results, including average time spent in the system, queue sizes, waiting times, and server utilizations.

- **plot_results/**
  - `th2.py`: A Python script to plot the results of the simulations from a CSV file. The script generates a plot showing the fraction of queues with at least a certain size (Q) for different values of `lambda` and `d`. It creates a single image with four subplots, each representing a different value of `d` (1, 2, 5, 10).

- **README.md**: The project README file, providing an overview of the project, usage instructions, and explanations of the scripts.
