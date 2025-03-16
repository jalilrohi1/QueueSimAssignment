#!/bin/bash
# filepath: d:\0001Second Year\DistributedComputing\queue_sim\automation\lambda_value_effect.sh

# Default parameters
OUTPUT_FILE="./data/lambda_effect.csv"
LAMBDA_VALUES_STR="0.5,0.7,0.9,0.95,0.99"
D_VALUES_STR="1,2,5,10"
SHAPE_VALUES_STR="0.5,1,1.5,3,3.75"
MU=1
MAX_T=100000
N=10
USE_RR=False
QUANTUM=1
PLOT_FILE="./plots/Effect_of_lamdaDShape.png"
# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --csv)
            OUTPUT_FILE="$2"; shift ;;
        --lambda-values)
            LAMBDA_VALUES_STR="$2"; shift ;;
        --d-values)
            D_VALUES_STR="$2"; shift ;;
        --shape-values)
            SHAPE_VALUES_STR="$2"; shift ;;
        --mu)
            MU="$2"; shift ;;
        --max-t)
            MAX_T="$2"; shift ;;
        --n)
            N="$2"; shift ;;
        --use-rr)
            USE_RR=True ;;
        --no-use-rr)
            USE_RR=False ;;
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

# Convert comma separated strings into arrays
IFS=',' read -r -a LAMBDA_VALUES <<< "$LAMBDA_VALUES_STR"
IFS=',' read -r -a D_VALUES <<< "$D_VALUES_STR"
IFS=',' read -r -a SHAPE_VALUES <<< "$SHAPE_VALUES_STR"

# Define output CSV header
echo "lambd,mu,max_t,n,d,w,queue_size,quantum,weibull_shape" > "$OUTPUT_FILE"

# Calculate total simulations to run
total_runs=$((${#LAMBDA_VALUES[@]} * ${#D_VALUES[@]} * ${#SHAPE_VALUES[@]}))
run_count=0

for d in "${D_VALUES[@]}"; do
  for shape in "${SHAPE_VALUES[@]}"; do
    for lambda in "${LAMBDA_VALUES[@]}"; do
      run_count=$((run_count + 1))
      echo "Running simulation $run_count of $total_runs: lambda=$lambda, d=$d, shape=$shape"
      
      CMD=(python3 ./main/main.py 
           --lambd "$lambda" 
           --mu "$MU" 
           --max-t "$MAX_T" 
           --n "$N" 
           --d "$d" )
      # If use_rr is requested, append the flag and quantum
      if [ "$USE_RR" = True ]; then
          CMD+=(--use-rr --quantum "$QUANTUM")
      fi
      CMD+=(--shape "$shape" --csv "$OUTPUT_FILE")
      
      if ! "${CMD[@]}"; then
        echo "Error running simulation for lambda=$lambda, d=$d, shape=$shape" >&2
        exit 1
      fi
    done
  done
done

echo "All simulations completed."
echo "Plotting results...{PLOT_FILE}"
python3 ./plot_results/plot_effect_lambda_for_D_shapes.py --output "$PLOT_FILE" --csv "$CSV_FILE"