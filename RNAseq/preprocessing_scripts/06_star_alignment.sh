#!/bin/bash
#SBATCH --job-name=star_alignment
#SBATCH --output=logs/06_star_alignment/star_alignment_%A_%a.out
#SBATCH --error=logs/06_star_alignment/star_alignment_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=8:00:00
#SBATCH --array=1-8
#SBATCH --partition="pibu_el8"

# Load STAR module
# module load star
module load STAR/2.7.10a_alpha_220601-GCC-10.3.0

# Set input and output directories
input_dir="04_trimmed_data"
output_dir="06_star_alignment_1st_pass"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Get the input file based on the array task ID
input_file=$(ls -1 "$input_dir"/*_R1_trimmed.fastq.gz | sed -n "${SLURM_ARRAY_TASK_ID}p")

# Get file name without extension
filename=$(basename "$input_file" _R1_trimmed.fastq.gz)

# Set output file paths
output_bam="$output_dir/${filename}.bam"

# Run STAR alignment
STAR --runThreadN 16 \
--genomeDir reference/Ensmbl/Danio_rerio/v109/star_index_2_7_10a \
--readFilesIn "$input_file" \
--outFileNamePrefix "$output_dir/$filename." \
--outSAMtype BAM SortedByCoordinate \
--outSAMunmapped Within \
--readFilesCommand zcat \
--sjdbGTFfile reference/Ensmbl/Danio_rerio/v109/Danio_rerio.GRCz11.109.gtf \
--outSAMattributes Standard

# Check if STAR alignment completed successfully
if [ $? -eq 0 ]; then
    echo "STAR alignment completed successfully for $filename"
else
    echo "STAR alignment failed for $filename"
fi

# Remove the bam file from the previous step
rm $output_bam

# Filter SJ.out.tab files for the current sample
awk '{ if ($7 >= 3) print $0}' "$output_dir/$filename.SJ.out.tab" > "$output_dir/$filename.SJ.filtered.tab"




# Check if STAR alignment completed successfully
if [ $? -eq 0 ]; then
    echo "STAR alignment completed successfully for $filename"
else
    echo "STAR alignment failed for $filename"
fi
