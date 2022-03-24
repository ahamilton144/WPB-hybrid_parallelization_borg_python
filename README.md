# WPB-hybrid_parallelization_borg_python

This repository contains all code related to the post ["To parallelize or not to parallelize? On performance of hybrid schemes in Python with the Borg MOEA,"](https://waterprogramming.wordpress.com/2022/03/23/to-parallelize-or-not-to-parallelize-on-performance-of-hybrid-schemes-in-python-with-the-borg-moea/) by Andrew Hamilton, on the Water Programming Blog.

All experiments were run on the Cube cluster at Cornell University, using 12 nodes. I used Python 3.9.4, and the only non-standard modules needed are scipy and Jupyter Notebooks. You will also need to download the [Borg MOEA](http://borgmoea.org/), the [MOEA Framework](http://moeaframework.org/), and [pareto.py](https://github.com/matthewjwoodruff/pareto.py), and place them in the same directory as the files from this repo. See [Andrew Dircks' blog post] on the Borg MOEA Python wrapper for instructions on how to compile the Borg libraries. This repository borrows heavily from the code in that blog post, but modifies it to include parallelization of the Monte Carlo samples in each function evaluation.0

To repeat the analysis, run the following steps:

1. Create a new folder called "results/"
2. Run 5 seeds with the default of 1 task per node (i.e., 16 CPU/task): ```sh submit_msmp.sh```
3. Change the ```ntasks_per_node``` parameter in ```submit_msmp.sh``` to 2, 4, 8, and 16, and repeat step 2 each time. To add dependencies, so that the jobs run one at a time, change the ```dependency``` parameter to the SLURM jobid of the previous job each time.
4. Run the postprocessing scripts in this order: 
    - Find the overall reference Pareto set across all seeds: ```sh find_refSets.sh```
    - Extract the objective values of each seed at each printed time step: ```sh find_objs.sh```; 
    - Extract the recombination operator selection probabilities, number of function evaluations, and elapsed time at each printed time step: ```sh find_operators.sh```; 
    - Find the performance metrics at each printed time step: ```sh find_runtime_metrics.sh```
5. Now repeat this analysis with 10,000 function evaluations rather than 800
    - Copy the results folder ```results/``` to ```results_800FE```
    - In ```borg_lake_msmp.py```, change the ```maxEvals``` variable to 10000, and the ```runtimeFreq``` variable to 50
    - Repeat steps 1-4. I only did 1 and 16 tasks per node for step 2-3, but you can repeat for 2, 4, and 8 if interested.
6. Copy the results folder to ```results_10kFE```
7. Copy all results to a local computer, then open and run the Jupyter Notebook ```process_results.ipynb```, which will create all figures from the blog post.
