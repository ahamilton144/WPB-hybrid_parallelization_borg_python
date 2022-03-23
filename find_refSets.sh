#/bin/bash

python pareto.py results/*.set -o 6-9 -e 0.01 0.01 0.001 0.001 --output results/overall.resultfile --delimiter=" " --comment="#"
cut -d ' ' -f 7-10 results/overall.resultfile >results/overall.reference

