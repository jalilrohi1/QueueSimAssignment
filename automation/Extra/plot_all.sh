#!/bin/bash

# Path to the Python script for plotting
plot_script="../plot_results/plot_all.py"  # Assuming the plotting script is named 'plot_results.py'

# Directory containing the CSV files
data_dir="../automation/data"

# Output directory for plots
output_dir="./plots1"

# Find all CSV files in the data directory
csv_files=$(find "$data_dir" -name "*.csv")

# Execute the plotting script with the CSV files and output directory
python3 "$plot_script" "$csv_files" --output_dir "$output_dir"