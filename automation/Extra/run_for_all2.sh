#!/bin/bash

# Simulation parameters
mu=1
n=10
max_t=100000

# Create an output directory if it doesn't exist
output_dir="./data/newdata"
mkdir -p "$output_dir"

# --- M/M/1 and M/M/N Simulations ---
output_file_mm1="$output_dir/mm1.csv"
output_file_mmn="$output_dir/mmn.csv"
lambd=0.7
python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n 1 --max-t "$max_t" --csv "$output_file_mm1"
python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --max-t "$max_t" --csv "$output_file_mmn"

# --- Supermarket Model Simulations ---
output_file_supermarket_n="$output_dir/supermarket_n.csv"
lambd=0.99
d=2
for n_value in 10 50 100; do
    python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n "$n_value" --d "$d" --max-t "$max_t" --csv "$output_file_supermarket_n"
done

output_file_supermarket_d="$output_dir/supermarket_d.csv"
lambd=0.5
n=100
for d in 1 2 5 10; do
    python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --max-t "$max_t" --csv "$output_file_supermarket_d"
done

# --- Round Robin Simulations ---
output_file_round_robin="$output_dir/round_robin.csv"
lambd=0.5
d=1
n=10
for shape in 0.5 1 1.5 3 3.75; do
    python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --use-rr --shape "$shape" --max-t "$max_t" --csv "$output_file_round_robin"
done

output_file_round_robin_supermarket="$output_dir/round_robin_supermarket.csv"
d=5
for shape in 0.5 1 1.5 3 3.75; do
    python3 ./main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --use-rr --shape "$shape" --max-t "$max_t" --csv "$output_file_round_robin_supermarket"
done

# --- Plot the Results ---
python3 ./plot_results/plot_results.py --csv "$output_dir"/*.csv --output_dir "./plots1"