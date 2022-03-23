#!/bin/bash
SEEDS=$(seq 0 4)
for SEED in ${SEEDS}
do
	for TASK in 16 8 4 2 1 
	do
		awk 'BEGIN {FS=" "}; /^#/ {print $0}; /^[^#/]/ {printf("%s %s %s %s\n",$7,$8,$9,$10)}' results/msmp_${TASK}task_s${SEED}.runtime >results/msmp_${TASK}task_s${SEED}.obj  
	done
done
