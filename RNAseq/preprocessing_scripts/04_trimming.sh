#!/bin/bash
#SBATCH --job-name=fastp_trim
#SBATCH --output=logs/04_trimming/fastp_trim_%A_%a.out
#SBATCH --error=logs/04_trimming/fastp_trim_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --time=2:00:00
#SBATCH --array=1-8
#SBATCH --partition="pibu_el8"

# Load fastp module
# module load fastp
module load fastp/0.23.4-GCC-10.3.0

# Set input and output directories
input_dir="raw_fastq"
output_dir="04_trimmed_data"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Get the input file based on the array task ID
input_file=$(ls -R $input_dir/Sample_*/*fastq.gz| sed -n "${SLURM_ARRAY_TASK_ID}p")

# Get file name without extension
filename=$(basename "$input_file" .fastq.gz)

# Set output file paths
output_r1="$output_dir/${filename}_R1_trimmed.fastq.gz"

# Run fastp
fastp -i "$input_file" -o "$output_r1" -w 8

# Check if fastp completed successfully
if [ $? -eq 0 ]; then
    echo "fastp completed successfully for $filename"
else
    echo "fastp failed for $filename"
fi
