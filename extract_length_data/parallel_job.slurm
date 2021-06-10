#!/bin/bash
#
#SBATCH --job-name=extract_length_data_pro_conv
#SBATCH --output=extract_length_output_pro_conv.txt
#
#SBATCH --account=vnarsim
#SBATCH --ntasks=6
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=2048

module load anaconda
source activate sci_env
python parallel_extract_length.py /scratch/brown/lin891/os_ext_conv_test/ /home/lin891/cluster_git/BEM_analysis_scripts/extract_length_data/conv_test/ 10
