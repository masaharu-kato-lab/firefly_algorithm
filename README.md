# firefly_algorithm
Implementation of Firefly Algorithm

# Installation
```
virtualenv env --python=/usr/bin/python3
pip install numpy
pip install distance
```

# Running
- Before running
```
source env/bin/activate
```  
  
- Tsp Problem (Example)
```
python src/discrete/_run_tsp.py -n 100 -g 0.1 -a 2.0 -t 1000 -f res/oliver30.tsp --stdout
```  
  
- After running
```
deactivate
```
