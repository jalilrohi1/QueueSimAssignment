#!/bin/bash
# filepath: d:\0001Second Year\DistributedComputing\queue_sim\automation\queue_experiments.sh

# Default parameters
LAMBDA=0.7
D_VALUES=(1 2 5 10)
N_VALUES=(10 20 50 100)
SHAPE_VALUES=(0.5 1 2 3) 
MU=1
MAX_T=100000
MONITOR_INTERVAL=10
CSV_FILE="./data/d_effect.csv"
USE_RR=False
QUANTUM=1
PLOT_FILE="./plots/Effect_of_D.png"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --d)
            IFS=',' read -r -a D_VALUES <<< "$2"; shift ;;
        --n)
            IFS=',' read -r -a N_VALUES <<< "$2"; shift ;;
        --shapes)
            IFS=',' read -r -a SHAPE_VALUES <<< "$2"; shift ;;
        --lambda)
            LAMBDA="$2"; shift ;;
        --mu)
            MU="$2"; shift ;;
        --max-t)
            MAX_T="$2"; shift ;;
        --monitor-interval)
            MONITOR_INTERVAL="$2"; shift ;;
        --csv)
            CSV_FILE="$2"; shift ;;
        --use-rr)
            USE_RR=True; shift ;;
        --quantum)
            QUANTUM="$2"; shift ;;
        --plot-file)
            PLOT_FILE="$2"; shift ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1 ;;
    esac
    shift
done

# Calculate total simulations to run
total_runs=$((${#LAMBDA_VALUES[@]} * ${#D_VALUES[@]} * ${#SHAPE_VALUES[@]}))
run_count=0

# Run the experiment for each combination of d, n, and shape with lambda fixed at 0.7
for D in "${D_VALUES[@]}"; do
  for N in "${N_VALUES[@]}"; do
    for SHAPE in "${SHAPE_VALUES[@]}"; do
      run_count=$((run_count + 1))
      echo "Running simulation $run_count of $total_runs: with lambda=$LAMBDA, d=$D, n=$N, shape=$SHAPE, use_rr=$USE_RR, quantum=$QUANTUM"
      if [ "$USE_RR" = True ]; then
        python3 ./main/main.py --lambd "$LAMBDA" --mu "$MU" --d "$D" --n "$N" --csv "$CSV_FILE" --monitor-interval "$MONITOR_INTERVAL" --max-t "$MAX_T" --shape "$SHAPE" --use-rr --quantum "$QUANTUM"
      else
        python3 ./main/main.py --lambd "$LAMBDA" --mu "$MU" --d "$D" --n "$N" --csv "$CSV_FILE" --monitor-interval "$MONITOR_INTERVAL" --max-t "$MAX_T" --shape "$SHAPE" --quantum "$QUANTUM"
      fi
    done
  done
done
echo "All simulations completed."
echo "Plotting results...{PLOT_FILE}"
python3 ./plot_results/plot_effect_D_for_n_shapes.py --output "$PLOT_FILE" --csv "$CSV_FILE"