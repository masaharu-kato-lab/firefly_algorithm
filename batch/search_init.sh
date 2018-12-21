source env/bin/activate
for i in `seq 1 1000`
do
    python src/discrete/_run_opu.py -n 93 -g 0.01502 -a 6.0 -ba 6.0 -e 0.1 -t 1000 -d 2 -fnr -i random
    python src/discrete/_run_opu.py -n 93 -g 0.01502 -a 6.0 -ba 6.0 -e 0.1 -t 1000 -d 2 -fnr -i nn
done