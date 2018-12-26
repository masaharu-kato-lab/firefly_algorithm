#!/bin/sh
if [ "$#" -ne 5 ]; then
  echo "Usage: $0 seed_begin seed_end n_iteration knn_k u_weight" >&2
  exit 1
fi

log_path=logs/$(basename "$0" .sh)_t$3_k$4_u$5

mkdir -p $log_path

for i in `seq $1 $2`
do
    env/bin/python src/discrete/_run_opu.py -s $i -is $i -n 93 -g 0.01502 -a 6.0 -ba 6.0 -t $3 -d 2 -i knn -k $4 -u $5 -o $log_path/$(printf %04d $i).txt
done
