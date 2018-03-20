#!/bin/bash

# tests the same instance set with different seeds: compare the different behaviours of the "uniform" method #

mkdir -p results
seeds=( "ALPHA" "BRAVO" "CHARLIE" "DELTA" "ECHO" "FOXTROT" "GOLF" "HOTEL" "INDIA" "JULIETT" )
for s in "${seeds[@]}"
do
  echo "Processing set for seed $s..."
  ./sample.sh $1 $2 $3 $4 $5 $6 --seed "$s"
  mkdir -p results/"$s"
  mv treeinfo graphs results/"$s"/
done
