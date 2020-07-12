# firefly_algorithm
Implementation of Firefly Algorithm

Requires **Python3.8.x** (Works with python3.6+, but will not support in the future.)

# Installation
Install using python virtual environment in the project root directory.
```
python3.8 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

# Running
## Before running
Activate the python virtual environment.
```
source env/bin/activate
```  
  
## OPU Route Optimization Problem (Example)
```
python src/route_planner/_run.py -ni 30 -g 0.01502 -a 2.0 -ba 2.0 -tmax 1000 -nd 2 -ibm rg -icm pamed -inc 3 --stdout
```  
Brief description of arguments:
- `-ni`: Number of fireflies
- `-g`: Constant gamma
- `-a`: Constant alpha
- `-ba`: Constant alpha when fireflies are blocked
- `-tmax`: Number of iterations
- `-nd`: Number of drones
- `-ibm`: Initialization building method (`r`:random, `rg`:random and greedy)
- `-icm`: Initialization clustering method (`none`:none, `rmed`:random k-medoids, `pamed`:normal k-medoids) 
- `-inc`: Number of clusters for initialization clustering
- `--stdout`: Print logs to stdout (Log file are generated to 'out' directory)

For the details of arguments, type `python src/route_planner/_run.py --help` or check 'src/route_planner/_arguments.py'.

## The analysis of results
You can use these tools in the directory  to analyze results of route optimization problem.

In the directory `src/route_viewer`:
- average_convergence.py
- calc_time.py
- clustering_map.py
- convergence&#46;py
- final_solutions.py
- mapper_image.py
- mean_values.py
- path_count.py
- show_args.py
- simple_route.py
- stat_values.py
- values&#46;py
- values_on_update.py
- variants&#46;py
- violin_polt.py


## After running
Deactivate the python virtual environment.
```
deactivate
```
