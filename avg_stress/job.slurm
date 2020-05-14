#!/bin/bash
#
#SBATCH --job-name=extract_stress_data
#SBATCH --output=extract_stress_data.txt
#
#SBATCH --account=vnarsim
#SBATCH --ntasks=4
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=100

module load anaconda
source activate sci_env
python parallel_stress_calc.py /scratch/brown/lin891/oblate/
