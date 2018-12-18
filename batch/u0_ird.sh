#!/bin/sh
source env/bin/activate
for i in `seq 1 100`
do
    python src/discrete/_run_opu.py -n 93 -g 0.01502 -a 6.0 -ba 6.0 -e 0.1 -t 1000 -d 2 -fnr -u 0 -i random --stdout > logs/u0_ird/u0_ird_$(print %04d $i).txt
done
