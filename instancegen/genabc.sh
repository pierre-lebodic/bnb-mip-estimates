#!/bin/bash

if [ ! -f pathtoscip ]; then
  echo "Enter path to SCIP:"
  read SCIP
  echo $SCIP > pathtoscip
fi
SCIP=$(<pathtoscip)
TARGETDIR=$1
for f in $TARGETDIR*.mps
do
  if [ ! -f ${f%.mps}.abc ]; then
    echo "Generating vbc file for $f..."
    { echo "set load scip.set"; echo "read $f"; echo opt; echo quit; } | $SCIP
    mv sciptree.vbc ${f%.mps}.vbc
  fi
done

for h in $TARGETDIR*.vbc
do
  if [ ! -f ${h%.vbc}.abc ]; then
    python3 compressvbc.py $h
    rm $h
  fi
done
