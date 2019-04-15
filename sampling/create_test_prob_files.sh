#! /bin/bash

ABCFILES=$@

for i in ${ABCFILES[@]}
do
    for method in 0 1
    do
        echo $i $method
        ./main.py -f $i 1000000 --debug -o --method $method -w
    done
done
