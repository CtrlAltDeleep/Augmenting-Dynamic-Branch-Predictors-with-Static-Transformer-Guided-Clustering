#!/bin/bash
#PBS -l select=1:ncpus=10:mem=300gb
#PBS -l walltime=50:00:00
#PBS -N gobmk_small_seq_EMERGENCY_MEMORY

cd $PBS_O_WORKDIR

module load anaconda3/personal
source activate pytorch_env

python3 -c "import torch;print(torch.cuda.is_available())"
python3 transformer_small_seq_gobmk_emergency.py /rds/general/user/ad2820/home/meng_project_misc/transformer/spec2006/train/gobmk /rds/general/user/ad2820/home/meng_project_misc/transformer/spec2006/test/gobmk 3
