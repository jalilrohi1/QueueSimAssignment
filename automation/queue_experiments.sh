#!/bin/bash

# Default parameters
LAMBDA_VALUES=(0.5 0.7 0.9 0.95 0.99)
D_VALUES=(1 2 5 10)
MU=1
N=10
MAX_T=100000
MONITOR_INTERVAL=10
CSV_FILE="./data/out.csv"
SHAPE=None

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
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Run the experiment for each combination of lambda and d
for LAMBD in "${LAMBDA_VALUES[@]}"; do
  for D in "${D_VALUES[@]}"; do
    echo "Running simulation with lambda=$LAMBD, d=$D, shape=$SHAPE"
    if [ "$SHAPE" != "None" ]; then
      python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T --shape $SHAPE
    else
      python3 ./main/main.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T
    fi
  done
done