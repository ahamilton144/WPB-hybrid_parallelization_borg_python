#!/bin/bash
SEEDS=$(seq 0 4)
for SEED in ${SEEDS}
do
	for TASK in 16 8 4 2 1 
	do
		for OPERATOR in SBX DE PCX SPX UNDX UM NFE ElapsedTime
		do
			operatorfile=results/msmp_${TASK}task_s${SEED}.${OPERATOR}
			runtimefile=results/msmp_${TASK}task_s${SEED}.runtime
			grep $OPERATOR $runtimefile | grep -Eo '[+-]?[0-9]+([.][0-9]+)?' | tee $operatorfile >/dev/null
		done
	done
done
