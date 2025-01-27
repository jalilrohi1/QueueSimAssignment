

```markdown
# Queue Simulation and Analysis

This repository contains scripts for simulating queue systems and analyzing their behavior. The main functionalities include running simulations with varying parameters and visualizing the results through plots.

## Prerequisites

- Python 3.x
- `pandas` library
- `matplotlib` library

You can install the required libraries using pip:

```bash
pip install pandas matplotlib
```

## Repository Structure

- **`queue_experiments.sh`**: A Bash script to run multiple queue simulations with varying parameters.
- **`main.py`**: The main Python script to run a single queue simulation.
- **`th2.py`**: A Python script to visualize simulation results from a CSV file.
- **`data/`**: Directory to store output CSV files from simulations.
- **`plot_results/`**: Directory to store the generated plots.

## Usage

### Running Simulations

To run multiple simulations with varying parameters, use the `queue_experiments.sh` script:

```bash
bash ./automation/queue_experiments.sh [options]
```

#### Options

- `--lambdas`: Comma-separated list of arrival rates (`λ`) to test.
- `--ds`: Comma-separated list of `d` values (number of servers to choose from).
- `--mu`: Service rate (default: 1).
- `--n`: Number of servers (default: 10).
- `--max-t`: Maximum simulation time (default: 100000).
- `--monitor-interval`: Monitoring interval (default: 10).
- `--csv`: Path to the output CSV file (default: `out.csv`).

#### Example

```bash
bash ./automation/queue_experiments.sh --lambdas "0.5,0.7,0.9" --ds "1,2,5" --mu 1 --n 10 --max-t 100000 --monitor-interval 10 --csv ./data/out.csv
```

### Visualizing Results

To plot results from a CSV file, use the `th2.py` script:

```bash
python3 ./plot_results/th2.py --csv <path_to_csv_file> --output <path_to_output_image>
```

#### Arguments

- `--csv`: Path to the input CSV file containing the simulation data.
- `--output`: Path to the output image file where the plot will be saved.

#### Example

```bash
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

## Script Details

### `queue_experiments.sh`

This Bash script automates running multiple queue simulations by iterating over various combinations of `λ` (arrival rate) and `d` values. The results are saved to a specified CSV file.

#### Workflow

1. Sets default simulation parameters.
2. Parses user-specified arguments to override defaults.
3. Iterates over combinations of `λ` and `d`, running `main.py` for each and appending results to the CSV file.

### `main.py`

This Python script simulates a queue system for given parameters, including:

- Arrival rate (`λ`)
- Service rate (`μ`)
- Number of servers (`n`)
- Maximum simulation time (`max_t`)
- Number of servers to choose from (`d`)

The script calculates metrics like average time spent in the system, queue sizes, and server utilization, saving the results to a CSV file.

### `th2.py`

This Python script reads simulation data from a CSV file and generates a plot showing the fraction of queues with at least a certain size (Q) for different `λ` and `d` values.

#### Workflow

1. Reads the CSV file using `pandas` and processes the data.
2. Generates a figure with four subplots using `matplotlib`. Each subplot represents a specific value of `d` (1, 2, 5, 10).
3. Saves the resulting plot to the specified file.

### Plot Example

The generated plot will contain four subplots, each representing a different value of `d` (1, 2, 5, 10). Each subplot shows the fraction of queues with at least a certain size (Q) for varying arrival rates (`λ`).

---

# Project Structure

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

- **`automation/`**
  - `queue_experiments.sh`: Bash script to automate running multiple queue simulations with different parameter combinations. This script iterates over specified values for arrival rate (`lambda`) and server selection (`d`) and stores the results in CSV format.

- **`data/`**
  - `new_out.csv`: Example CSV file containing the output from a queue simulation. This folder is used to store all simulation results.

- **`main/`**
  - `main.py`: The primary Python script for running a single queue simulation. It simulates the system with specified parameters like `lambda`, `mu`, `n`, and `d`, and saves metrics like average queue sizes, waiting times, and server utilization to a CSV file.

- **`plot_results/`**
  - `th2.py`: Python script for visualizing simulation results from a CSV file. It generates a plot with four subplots, each showing queue size distributions for a specific value of `d`.

- **`README.md`**
  - A comprehensive guide for the project, including installation steps, usage examples, and file descriptions.
