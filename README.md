# Queue Simulation Plotting

This repository contains a Python script to plot the fraction of queues with at least a certain size for different values of `lambda` and `d` from a CSV file. The script generates a single image with four subplots, each representing a different value of `d` (1, 2, 5, 10).

## Prerequisites

- Python 3.x
- `pandas` library
- `matplotlib` library

You can install the required libraries using pip:

```sh
pip install pandas matplotlib


Usage
To run the script, use the following command:
```python3 ./plot_results/th2.py --csv <path_to_csv_file> --output <path_to_output_image>
