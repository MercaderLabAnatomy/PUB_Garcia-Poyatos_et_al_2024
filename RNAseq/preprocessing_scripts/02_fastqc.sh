#!/bin/bash
#SBATCH --job-name=fastqc
#SBATCH --output=logs/02_fastqc_before_trimming_output/fastqc_%A_%a.out
#SBATCH --error=logs/02_fastqc_before_trimming_output/fastqc_%A_%a.err
#SBATCH --array=0-7
#SBATCH --mem-per-cpu=4G
#SBATCH --cpus-per-task=3
#SBATCH --time=00:20:00

# Load FastQC module
module load UHTS/Quality_control/fastqc/0.11.9;

# Set the input directory
input_dir="raw_fastq"

# Get the list of input files
input_files=($(ls -R $input_dir/Sample_*/*fastq.gz))

# Get the current input file based on the array task ID
current_file=${input_files[$SLURM_ARRAY_TASK_ID]}

# make a directory for output files
mkdir -p 02_fastqc_before_trimming_output

# Run FastQC on the current input file
fastqc $current_file -o 02_fastqc_before_trimming_output

