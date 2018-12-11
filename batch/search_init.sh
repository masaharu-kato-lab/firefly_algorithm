source env/bin/activate
for i in `seq 1 100`
do
    python src/discrete/_run_opu.py -n 93 -g 0.01502 -a 6.0 -ba 6.0 -e 0.1 -t 1000 -d 2 -s $i -is $i -fnr -i random  --stdout
    python src/discrete/_run_opu.py -n 93 -g 0.01502 -a 6.0 -ba 6.0 -e 0.1 -t 1000 -d 2 -s $i -is $i -fnr -i nn      --stdout
done