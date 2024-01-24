#!/bin/bash
#SBATCH --job-name=fastqc
#SBATCH --output=logs/05_fastqc_post_trimming/fastqc_%A_%a.out
#SBATCH --error=logs/05_fastqc_post_trimming/fastqc_%A_%a.err
#SBATCH --array=1-8
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=8G
#SBATCH --time=00:20:00
#SBATCH --partition="pibu_el8"

# Load the required module
# module load UHTS/Quality_control/fastqc/0.11.9;
module load FastQC/0.11.9-Java-11

# Define the input directory
input_dir="./04_trimmed_data/"

# Get the list of FASTQ files
fastq_files=($(ls -1 $input_dir/*.fastq.gz))

# Get the current file to process
current_file=${fastq_files[$SLURM_ARRAY_TASK_ID-1]}

# Create the output directory if it doesn't exist
output_dir="05_fastqc_post_trimming_output"
mkdir -p $output_dir

# Run fastqc on the current file
fastqc $current_file -o $output_dir

echo "FastQC completed for file: $current_file"
