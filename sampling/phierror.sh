#!/bin/bash

TARGETDIR=$1
>phierror.info
for g in $TARGETDIR*.abc
do
  j=${g%.abc}
  k=$(basename $j)
  echo "Processing $g..."
  python3 main.py -p -f $g 0 | grep "^[^>]" >> phierror.info
done
