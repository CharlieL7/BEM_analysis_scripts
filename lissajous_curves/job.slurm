#!/bin/bash
#
#SBATCH --job-name=extract_length_data
#SBATCH --output=extract_length_output.txt
#
#SBATCH --account=vnarsim
#SBATCH --ntasks=24
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=100

module load anaconda
source activate sci_env
python parallel_extract_length.py /depot/vnarsim/data/phase_fill/
