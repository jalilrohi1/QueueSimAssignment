#!/bin/bash

# Define the parameters for the experiment
LAMBDA_VALUES=(0.5 0.7 0.9 0.95 0.99)
D_VALUES=(1 2 5 10)
MU=1
N=10
MAX_T=100000
MONITOR_INTERVAL=10
CSV_FILE="out.csv"

# Run the experiment for each combination of lambda and d
for LAMBD in "${LAMBDA_VALUES[@]}"; do
  for D in "${D_VALUES[@]}"; do
    echo "Running simulation with lambda=$LAMBD, d=$D"
    python3 queue_sim.py --lambd $LAMBD --mu $MU --d $D --n $N --csv $CSV_FILE --monitor-interval $MONITOR_INTERVAL --max-t $MAX_T
  done
done