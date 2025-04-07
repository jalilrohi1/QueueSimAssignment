#!/bin/bash

# Default parameters
LAMBDA_VALUES=(0.5 0.7 0.9 0.95 0.99)
D_VALUES=(1 2 5 10)
MU=1
N=1000
MAX_T=100000
MONITOR_INTERVAL=10
CSV_FILE="./data/plot_theoritical_FF.csv"
SHAPE=None
USE_RR=False
QUANTUM=1
PLOT_FILE="./plots/Theoritical_plot_FF.png"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --lambdas) IFS=',' read -r -a LAMBDA_VALUES <<< "$2"; shift ;;
        --ds) IFS=',' read -r -a D_VALUES <<< "$2"; shift ;;
        --mu) MU="$2"; shift ;;
        --n) N="$2"; shift ;;
        --max-t) MAX_T="$2"; shift ;;
        --monitor-interval) MONITOR_INTERVAL="$2"; shift ;;
        --csv) CSV_FILE="$2"; shift ;;
        --shape) SHAPE="$2"; shift ;;
        --use-rr) USE_RR=True; shift ;;
        --quantum) QUANTUM="$2"; shift ;;
        --plot-file) PLOT_FILE="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Add this after the parameters declaration and before running simulations
# Create directories if they don't exist
mkdir -p "$(dirname "$CSV_FILE")"
mkdir -p "$(dirname "$PLOT_FILE")"

# Calculate total simulations to run
total_runs=$((${#LAMBDA_VALUES[@]} * ${#D_VALUES[@]}))
run_count=0

# Run the experiment for each combination of lambda and d
for LAMBD in "${LAMBDA_VALUES[@]}"; do
  for D in "${D_VALUES[@]}"; do
    run_count=$((run_count + 1))
    echo "Running simulation $run_count of $total_runs: with lambda=$LAMBD, d=$D, shape=$SHAPE, use_rr=$USE_RR, quantum=$QUANTUM"
    if [ "$SHAPE" != "None" ]; then
      if [ "$USE_RR" = True ]; then
        python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T --shape $SHAPE --use-rr --quantum $QUANTUM
      else
        python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T --shape $SHAPE --quantum $QUANTUM
      fi
    else
      if [ "$USE_RR" = True ]; then
        python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T --use-rr --quantum $QUANTUM
      else
        python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T --quantum $QUANTUM
      fi
    fi
  done
done

echo "All simulations completed."
echo "Plotting results...{$PLOT_FILE}"
python3 ./plot_results/plotTheoritical.py --output $PLOT_FILE --csv $CSV_FILE
echo "Plotting complete. Results saved to $PLOT_FILE"