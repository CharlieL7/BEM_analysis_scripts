#!/bin/bash
#
#SBATCH --job-name=extract_length_data_visc010
#SBATCH --output=extract_length_output_visc010.txt
#
#SBATCH --account=vnarsim
#SBATCH --ntasks=20
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=1024

module load anaconda
source activate sci_env
python parallel_extract_length.py /depot/vnarsim/data/lin_data/laoe_visc0_10_2_hal/ 10
