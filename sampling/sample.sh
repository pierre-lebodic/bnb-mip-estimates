#!/bin/bash

TARGETDIR=$1
mkdir -p treeinfo
mkdir -p graphs graphs/ests graphs/depths
for g in $TARGETDIR*.abc
do
  j=${g%.abc}
  k=$(basename $j)
  echo "Processing $g..."
  python3 main.py $2 $3 $4 $5 $6 $7 $8 $9 -f $g| grep "^[^>]" > treeinfo/$k.info
  mv $j*.e.png graphs/ests
  mv $j*.d.png graphs/depths
  mv $j*.png graphs
  mv $j*.est $j*.probs $j*.total treeinfo/
done
