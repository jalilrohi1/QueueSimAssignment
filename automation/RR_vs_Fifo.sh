#!/bin/bash

# Define output CSV file
OUTPUT_FILE="./data/RR_vs_Fifo.csv"
# Define output plot file
PLOT_FILE="./plots/RR_vs_Fifo.png"
# Ensure the file starts with a header
echo "lambd,mu,max_t,n,d,w,queue_size,quantum,weibull_shape" > $OUTPUT_FILE

# Define values for lambda (arrival rate)
LAMBDA=0.5  # Keep λ constant

# Define values for d (Supermarket sample size)
D=5  # Keep d constant

# Define values for quantum (time slices for Round-Robin)
QUANTUM_VALUES=(0.1 0.5 1 2 5)  # Different time slices for RR

# Define values for Weibull Shape (Job Size Variability)
SHAPE_VALUES=(0.5 1 1.5 3 3.75)  # Adjust as needed

# Run simulations for all combinations
for quantum in "${QUANTUM_VALUES[@]}"; do
  for shape in "${SHAPE_VALUES[@]}"; do
    python3 ./main/main.py --lambd $LAMBDA --mu 1 --max-t 100000 --n 10 --d $D --use-rr --quantum $quantum --shape $shape --csv $OUTPUT_FILE
  done
done

# Call the Python script to plot results
echo "All simulations completed."
echo "Plotting results...{PLOT_FILE}"
python3 ./plot_results/plot_RR_vs_FF.py --output "$PLOT_FILE" --csv "$CSV_FILE"