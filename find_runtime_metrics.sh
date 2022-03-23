SEEDS=$(seq 0 4)
JAVA_ARGS="-cp MOEAFramework-2.12-Demo.jar"

for SEED in ${SEEDS}
do
	for TASK in 16 8 4 2 1
	do
		NAME=_${TASK}task_s${SEED}
		slurmscript="\
		#!/bin/bash\n\
		#SBATCH -J ${NAME}\n\
		#SBATCH -N 1\n\
		#SBATCH -n 1\n\
		#SBATCH -p normal\n\
		#SBATCH -t 1:00:00\n\
		java ${JAVA_ARGS} org.moeaframework.analysis.sensitivity.ResultFileEvaluator \
			-d 4 -i results/msmp_${TASK}task_s${SEED}.obj -r results/overall.reference \
			-o results/msmp_${TASK}task_s${SEED}.metrics"
		echo -e $slurmscript | sbatch
	done
done
