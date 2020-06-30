#!/bin/bash
#
#SBATCH --job-name=extract_length_data_oblate
#SBATCH --output=extract_length_output.txt
#
#SBATCH --account=vnarsim
#SBATCH --ntasks=4
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=100

module load anaconda
source activate sci_env
python extract_length_data.py /depot/vnarsim/data/lin_data/to_local/
