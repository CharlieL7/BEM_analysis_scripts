#!/bin/bash
#
#SBATCH --job-name=extract_length_data
#SBATCH --output=extract_length_output.txt
#
#SBATCH --account=debug
#SBATCH --ntasks=2
#SBATCH --time=0:10:00
#SBATCH --mem-per-cpu=100

module load anaconda
source activate sci_env
python parallel_stress_calc.py /home/lin891/to_local/
