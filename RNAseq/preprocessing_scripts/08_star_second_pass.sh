#!/bin/bash
#SBATCH --job-name=star_alignment
#SBATCH --output=logs/08_star_2ndpass_alignment/star_2ndpass_alignment_%A_%a.out
#SBATCH --error=logs/08_star_2ndpass_alignment/star_2ndpass_alignment_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH --array=1-8
#SBATCH --partition="pibu_el8"

# Load STAR module
module load STAR/2.7.10a_alpha_220601-GCC-10.3.0

# Set input and output directories

output_dir="08_star_alignment_2nd_pass"

# Set input and output directories for second pass alignment
input_dir="04_trimmed_data"
output_dir="08_star_alignment_2nd_pass"
first_pass_dir="06_star_alignment_1st_pass"

# Create output directory for second pass alignment if it doesn't exist
mkdir -p "$output_dir"

# Get the input file based on the array task ID
input_file=$(ls -1 "$input_dir"/*_R1_trimmed.fastq.gz | sed -n "${SLURM_ARRAY_TASK_ID}p")


# Get file name without extension
filename=$(basename "$input_file" _R1_trimmed.fastq.gz)

# Set output file paths for second pass alignment
output_bam="$output_dir/${filename}.bam"


# Run second pass STAR alignment
STAR --runThreadN 16 \
--genomeDir star_2ndpass_index \
--readFilesIn "$input_file" \
--outFileNamePrefix "$output_dir/$filename." \
--outSAMtype BAM SortedByCoordinate \
--outSAMunmapped Within \
--readFilesCommand zcat \
--outSAMattributes Standard

# Check if second pass STAR alignment completed successfully
if [ $? -eq 0 ]; then
    echo "Second pass STAR alignment completed successfully for $filename"
else
    echo "Second pass STAR alignment failed for $filename"
fi
