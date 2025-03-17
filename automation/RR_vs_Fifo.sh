#!/bin/bash

# Default parameters
LAMBDA=0.7
D=5
N=10
QUANTUM_VALUES=(0.1 0.5 1 2 5)  # Different time slices for RR
SHAPE_VALUES=(0.5 1 1.5 3 3.75)  # Adjust as needed
MU=1
MAX_T=100000
MONITOR_INTERVAL=10
USE_RR=False
OUTPUT_FILE="./data/RR_vs_Fifo.csv"
CSV_FILE=$OUTPUT_FILE  # Ensures CSV_FILE is assigned properly if not passed as argument
PLOT_FILE="./plots/RR_vs_Fifo.png"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --d) D="$2"; shift ;;
        --n) N="$2"; shift ;;
        --shapes) IFS=',' read -r -a SHAPE_VALUES <<< "$2"; shift ;;
        --lambda) LAMBDA="$2"; shift ;;
        --mu) MU="$2"; shift ;;
        --max-t) MAX_T="$2"; shift ;;
        --monitor-interval) MONITOR_INTERVAL="$2"; shift ;;
        --csv) CSV_FILE="$2"; shift ;;
        --use-rr) USE_RR=True; shift ;;
        --quantum) IFS=',' read -r -a QUANTUM_VALUES <<< "$2"; shift ;;
        --plot-file) PLOT_FILE="$2"; shift ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1 ;;
    esac
    shift
done

# Calculate total simulations to run
total_runs=$((${#QUANTUM_VALUES[@]} * ${#SHAPE_VALUES[@]} + ${#SHAPE_VALUES[@]}))  # Include FIFO runs
run_count=0

echo "lambd,mu,max_t,n,d,w,queue_size,quantum,weibull_shape" > "$CSV_FILE"

# Run simulations for Round-Robin
for quantum in "${QUANTUM_VALUES[@]}"; do
  for shape in "${SHAPE_VALUES[@]}"; do
    run_count=$((run_count + 1))
    echo "Running simulation $run_count of $total_runs: with lambda=$LAMBDA, d=$D, quantum=$quantum, shape=$shape"
    python3 ./main/main.py --lambd $LAMBDA --mu $MU --max-t $MAX_T --n $N --d $D --use-rr --monitor-interval $MONITOR_INTERVAL --quantum $quantum --shape $shape --csv "$CSV_FILE"
  done
done

# Run FIFO Simulation (Quantum = 100000, Ensuring Only One FIFO Line)
FIFO_QUANTUM=100000
for shape in "${SHAPE_VALUES[@]}"; do
  run_count=$((run_count + 1))
  echo "Running FIFO simulation $run_count of $total_runs: with lambda=$LAMBDA, d=$D, quantum=FIFO, shape=$shape"
  python3 ./main/main.py --lambd $LAMBDA --mu $MU --max-t $MAX_T --n $N --d $D --monitor-interval $MONITOR_INTERVAL --quantum $FIFO_QUANTUM --shape $shape --csv "$CSV_FILE"
done

# Call the Python script to plot results
echo "All simulations completed."
echo "Plotting results... Output file: $PLOT_FILE"
python3 ./plot_results/plot_RR_vs_FF.py --output "$PLOT_FILE" --csv "$CSV_FILE"
echo "Plotting complete."