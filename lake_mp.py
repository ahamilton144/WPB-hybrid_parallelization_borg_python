##@author: Rohini Gupta, Andrew Hamilton

#DPS Formulation 

#Objectives:
#1) Maximize expected economic benefit
#2) Minimize worst case average P concentration 
#3) Maximize average inertia of P control policy
#4) Maximize average reliability 

#Constraints: 
#Reliability has to be <85%

#Decision Variables 
#vars: vector of size 3n 
#n is the number of radial basis functions needed to define the policy
#Each has a weight, center, and radius (w1, c1, r1..wm,cn,rn)

#Time Horizon for Planning, T: 100 Years
#Simulations, N: 100 


import numpy as np
from sys import *
import time
from math import *
from scipy.optimize import root
import scipy.stats as ss
from multiprocessing import Process, Array #cpu_count, Manager

# set number cpus per task for multiprocessing
nCorePerNode = 16
nTasksPerNode = 1
nProcesses = int(nCorePerNode / nTasksPerNode)

# wait time per MC trial
slp = 0.5

# Lake Parameters
b = 0.42
q = 2.0

# Natural Inflow Parameters
mu = 0.03
sigma = np.sqrt(10**-5)

# Economic Benefit Parameters
alpha = 0.4
delta = 0.98

# Set the number of RBFs (n), decision variables, objectives and constraints
n = 2
nvars = 3 * n
nobjs = 4
nYears = 100
nSamples = 48
nconstrs = 1

# Set Thresholds
reliability_threshold = 0.85
inertia_threshold = -0.02


###### RBF Policy ######

#Define the RBF Policy
def RBFpolicy(lake_state, C, R, W):
    # Determine pollution emission decision, Y
    Y = 0
    for i in range(len(C)):
        if R[i] != 0:
            Y = Y + W[i] * ((np.absolute(lake_state - C[i]) / R[i])**3)

    Y = min(0.1, max(Y, 0.01))

    return Y


#Define simulation model for single MC draw. return dictionary of objectives.
def LakeProblem_singleMC(s, discounted_benefit, yrs_inertia_met, yrs_Pcrit_met, average_annual_P, lake_state, natFlow_s, Y, b, q, critical_threshold, C, R, newW):
    #Run model simulation
    lake_state[0] = 0.
    db = 0.
    yim = 0
    yPm = 0
 
    #find policy-derived emission
    Y[0] = RBFpolicy(lake_state[0], C, R, newW)

    for i in range(nYears):
        lake_state[i + 1] = lake_state[i] * (1 - b) + (lake_state[i]**q) / (1 + (lake_state[i]**q)) + Y[i] + natFlow_s[i]
        db += alpha * Y[i] * delta**i

        if i >= 1 and ((Y[i] - Y[i - 1]) > inertia_threshold):
            yim += 1

        if lake_state[i + 1] < critical_threshold:
            yPm += 1

        if i < (nYears - 1):
            #find policy-derived emission
            Y[i + 1] = RBFpolicy(lake_state[i + 1], C, R, newW)

    # sleep
    time.sleep(slp)

    # fill in results for MC trial in shared memory arrays
    average_annual_P[(s*nYears):((s+1)*nYears)] = lake_state[1:]
    discounted_benefit[s] = db
    yrs_inertia_met[s] = yim
    yrs_Pcrit_met[s] = yPm


#Sub problem to dispatch MC samples from individual processes
def dispatch_MC_to_procs(proc, start, stop, discounted_benefit, yrs_inertia_met, yrs_Pcrit_met, average_annual_P, natFlow, b, q, critical_threshold, C, R, newW):
    lake_state = np.zeros([nYears + 1])
    Y = np.zeros([nYears])
    for s in range(start, stop):
        LakeProblem_singleMC(s, discounted_benefit, yrs_inertia_met, yrs_Pcrit_met, average_annual_P, lake_state, natFlow[s, :], Y, b, q, critical_threshold, C, R, newW)


###### Main Lake Problem Model ######

def LakeProblemDPS(*vars):

    seed = 1234

    #Solve for the critical phosphorus level
    def pCrit(x):
        return [(x[0]**q) / (1 + x[0]**q) - b * x[0]]

    sol = root(pCrit, 0.5)
    critical_threshold = sol.x

    #Initialize arrays
    objs = [0.0] * nobjs
    constrs = [0.0] * nconstrs

    #Generate nSamples of nYears of natural phosphorus inflows
    natFlow = np.zeros([nSamples, nYears])
    for i in range(nSamples):
        np.random.seed(seed + i)
        natFlow[i, :] = np.random.lognormal(
            mean=log(mu**2 / np.sqrt(mu**2 + sigma**2)),
            sigma=np.sqrt(log((sigma**2 + mu**2) / mu**2)),
            size=nYears)

    # Determine centers, radii and weights of RBFs
    C = vars[0::3]
    R = vars[1::3]
    W = vars[2::3]
    newW = np.zeros(len(W))

    #Normalize weights to sum to 1
    total = sum(W)
    if total != 0.0:
        for i in range(len(W)):
            newW[i] = W[i] / total
    else:
        for i in range(len(W)):
            newW[i] = 1 / n

    # create shared memory arrays which each process can access/write.
    discounted_benefit = Array('d', nSamples)
    yrs_inertia_met = Array('i',  nSamples)
    yrs_Pcrit_met = Array('i', nSamples)
    average_annual_P = Array('d', nSamples*nYears)

    # assign MC runs to different processes
    nbase = int(nSamples / nProcesses)
    remainder = nSamples - nProcesses * nbase
    start = 0
    shared_processes = []
    for proc in range(nProcesses):
        nTrials = nbase if proc >= remainder else nbase + 1
        stop = start + nTrials
        p = Process(target=dispatch_MC_to_procs, args=(proc, start, stop, discounted_benefit, yrs_inertia_met, yrs_Pcrit_met, average_annual_P, natFlow, b, q, critical_threshold, C, R, newW))

        shared_processes.append(p)
        start = stop

    # start processes
    for sp in shared_processes:
        sp.start()

    # wait for all processes to finish
    for sp in shared_processes:
        sp.join()

    # Calculate minimization objectives (defined in comments at beginning of file)
    objs[0] = -1 * np.mean(discounted_benefit)  #average economic benefit
    objs[1] = np.max(np.mean(np.reshape(average_annual_P, (nSamples, nYears)), axis=0))  #minimize the max average annual P concentration
    objs[2] = -1 * np.sum(yrs_inertia_met) / ((nYears - 1) * nSamples)  #average percent of transitions meeting inertia thershold
    objs[3] = -1 * np.sum(yrs_Pcrit_met) / (nYears * nSamples)  #average reliability

    constrs[0] = max(0.0, reliability_threshold - (-1 * objs[3]))

    return (objs, constrs)
