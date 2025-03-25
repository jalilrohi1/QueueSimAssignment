#!/bin/bash

# Default parameters
LAMBDA=0.5
D=5
MU=1
MAX_T=1000
MONITOR_INTERVAL=10
# Round-Robin quantum values
QUANTUM_VALUES=(0.1 0.5 1 2 5)
# Weibull shapes to test
SHAPE_VALUES=(0.5 1 1.5 3 3.75)
# Server counts to test
N_VALUES=(10 20 50 100)
# FIFO quantum value (a very large number to simulate FIFO)
FIFO_QUANTUM=100000

# Output CSV file
OUTPUT_FILE="./data/RR_vs_Fifo_servers3.csv"
PLOT_FILE="./plots/RR_vs_FF_server3.png"
# Ensure output directory exists
mkdir -p ./data
# Write CSV header
echo "lambd,mu,max_t,n,d,w,queue_size,quantum,weibull_shape" > "$OUTPUT_FILE"

total_runs=0

# Calculate total number of simulation runs:
# For each N, for each RR quantum and each shape, plus one FIFO run per shape.
for n in "${N_VALUES[@]}"; do
  total_runs=$(( total_runs + (${#QUANTUM_VALUES[@]} + 1) * ${#SHAPE_VALUES[@]} ))
done

run_count=0
# Loop over different server counts (N)
for n in "${N_VALUES[@]}"; do
  # Run Round-Robin simulations for each quantum and shape
  for quantum in "${QUANTUM_VALUES[@]}"; do
    for shape in "${SHAPE_VALUES[@]}"; do
      run_count=$((run_count + 1))
      echo "Run $run_count of $total_runs: lambda=$LAMBDA, n=$n, d=$D, quantum=$quantum, shape=$shape (RR)"
      python3 ./main/main.py --lambd $LAMBDA --mu $MU --max-t $MAX_T --n $n --d $D --use-rr --monitor-interval $MONITOR_INTERVAL --quantum $quantum --shape $shape --csv "$OUTPUT_FILE"
    done
  done

  # Run FIFO simulation (one run per shape) using FIFO_QUANTUM
  for shape in "${SHAPE_VALUES[@]}"; do
    run_count=$((run_count + 1))
    echo "Run $run_count of $total_runs: lambda=$LAMBDA, n=$n, d=$D, quantum=FIFO, shape=$shape (FIFO)"
    python3 ./main/main.py --lambd $LAMBDA --mu $MU --max-t $MAX_T --n $n --d $D --monitor-interval $MONITOR_INTERVAL --quantum $FIFO_QUANTUM --shape $shape --csv "$OUTPUT_FILE"
  done
done


# Call the Python script to plot results
echo "All simulations completed."
echo "Plotting results... Output file: $PLOT_FILE"
python3 ./plot_results/plot_RR_vs_FF.py --output "$PLOT_FILE" --csv "$OUTPUT_FILE"
echo "Plotting complete. Results saved to $PLOT_FILE"