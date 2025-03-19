#!/bin/bash

# Simulation parameters
lambd_values=(0.5 0.7 0.9 0.95 0.99)
mu=1
n=10
d_values=(1 2 5 10)
quantum_values=(0.1 0.5 1 2 5)
weibull_shapes=(0.5 1 1.5 3 3.75)
max_t=100000

# Create an output directory if it doesn't exist
output_dir="./data"
mkdir -p "$output_dir"

# Run simulations for FIFO scheduling with supermarket model
for lambd in "${lambd_values[@]}"; do
    for d in "${d_values[@]}"; do
        output_file="$output_dir/fifo_sm_lambd_${lambd}_d_${d}.csv"
        echo "Running FIFO simulation with supermarket model, lambda=$lambd, d=$d"
        python3 ../main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --max-t "$max_t" --csv "$output_file"
    done
done

# Run simulations for Round Robin scheduling with supermarket model
for lambd in "${lambd_values[@]}"; do
    for d in "${d_values[@]}"; do
        for quantum in "${quantum_values[@]}"; do
            output_file="$output_dir/rr_sm_lambd_${lambd}_d_${d}_quantum_${quantum}.csv"
            echo "Running Round Robin simulation with supermarket model, lambda=$lambd, d=$d, quantum=$quantum"
            python3 ../main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --use-rr --quantum "$quantum" --max-t "$max_t" --csv "$output_file"
        done
    done
done

# Run simulations for Weibull job size distributions with supermarket model (optional)
for lambd in "${lambd_values[@]}"; do
    for d in "${d_values[@]}"; do
        for shape in "${weibull_shapes[@]}"; do
            output_file="$output_dir/weibull_sm_lambd_${lambd}_d_${d}_shape_${shape}.csv"
            echo "Running Weibull simulation with supermarket model, lambda=$lambd, d=$d, shape=$shape"
            python3 ../main/main.py --lambd "$lambd" --mu "$mu" --n "$n" --d "$d" --shape "$shape" --max-t "$max_t" --csv "$output_file"
        done
    done
done