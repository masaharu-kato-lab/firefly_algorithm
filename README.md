# firefly_algorithm
Implementation of Firefly Algorithm

# Installation
```
virtualenv env --python=/usr/bin/python3
pip install -r requirements.txt
```

# Running
- Before running
```
source env/bin/activate
```  
  
- OPU Route Problem (Example)
```
python src/discrete/_run_opu.py -n 30 -g 0.01502 -a 2.0 -ba 2.0 -t 100 -d 2 -u 0 --init random --quiet --stdout
```  
  
- After running
```
deactivate
```
