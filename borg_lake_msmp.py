# Master-worker Borg run with Python wrapper
# ensure libborgms.so or libborgms.so is compiled and in this directory
from borg import *
from lake_mp import *
import sys

# set max time in hours
maxEvals = 800
runtimeFreq = 1
nSeeds = 5
nCorePerNode = 16
nTasksPerNode = 1
nCorePerFE = int(nCorePerNode / nTasksPerNode)

# need to start up MPI first
Configuration.startMPI()
for seed in range(nSeeds):
    # create an instance of Borg with the Lake problem
    borg = Borg(nvars, nobjs, nconstrs, LakeProblemDPS)
    Configuration.seed(seed)

    runtimeFile = 'results/msmp_' + str(nTasksPerNode) + 'task_s' + str(seed) + '.runtime'
    set1File = 'results/msmp_' + str(nTasksPerNode) + 'task_s' + str(seed) + '.set'

    # set bounds and epsilons for the Lake problem
    borg.setBounds(*[[-2, 2], [0, 2], [0, 1]] * int((nvars / 3)))
    borg.setEpsilons(0.01, 0.01, 0.0001, 0.0001)

    # perform the optimization
    result = borg.solveMPI(maxEvaluations=maxEvals, runtime=runtimeFile, frequency=runtimeFreq)
    # print the objectives to output
    if result:
        result.display()
        f = open(set1File, 'w')
        for solution in result:
            line = ''
            for v in solution.getVariables():
                line += str(v) + ' '
            for o in solution.getObjectives():
                line += str(o) + ' '
            f.write(line[:-1] + '\n')
        f.write('#')
        f.close()

# shut down MPI
Configuration.stopMPI()

