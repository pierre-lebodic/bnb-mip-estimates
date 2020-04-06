#! /bin/bash

ABCFILES=$@

for i in ${ABCFILES[@]}
do
    for method in 1
    do
        echo $i $method
        ./main.py -f $i 100000000 --debug -o --method $method -w
    done
done
