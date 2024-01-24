#!/bin/bash
#SBATCH --job-name=download_files
#SBATCH --output=download_files_%A_%a.out
#SBATCH --error=download_files_%A_%a.err
#SBATCH --array=0-11
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --time=00:30:00

# Read the URL from urls.txt based on the task ID
URL=$(sed -n "${SLURM_ARRAY_TASK_ID}p" urls.txt)

# make a directory to download the file to
mkdir -p 01_raw_fastq

# Download the file using wget
wget "$URL" -P 01_raw_fastq

# Print the downloaded file name
echo "Downloaded file: $(basename "$URL")"
