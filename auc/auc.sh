#!/bin/bash

# input: [directory containing folders of .total] [shift] [step]

> auc.info
for f in $1*.total; # $1 is the target directory
do
  python3 calcauc.py $f $2 $3 # filename, shift, step
done
python3 totalauc.py auc.info > auc.ave.info
