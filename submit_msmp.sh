#!/bin/bash

nodes=12
ntasks_per_node=1
dependency=0
t=01:00:00

SLURM="#!/bin/bash\n\
#SBATCH -J py-msmp \n\
#SBATCH -o results/msmp_${ntasks_per_node}task.out \n\
#SBATCH -e results/msmp_${ntasks_per_node}task.err \n\
#SBATCH -t ${t} \n\
#SBATCH --nodes ${nodes} \n\
#SBATCH --ntasks-per-node ${ntasks_per_node} \n\
\n\
sed -i \"s:nTasksPerNode = .*:nTasksPerNode = ${ntasks_per_node}:g\" lake_mp.py \n\
sed -i \"s:nTasksPerNode = .*:nTasksPerNode = ${ntasks_per_node}:g\" borg_lake_msmp.py\n\
\n\
time mpirun python3 borg_lake_msmp.py \n\
\n\ "

if [ $dependency -eq 0 ]
then
	echo -e $SLURM | sbatch
else
	echo -e $SLURM | sbatch --dependency=afterany:$dependency
fi

sleep 0.5
