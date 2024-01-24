#!/bin/bash
#SBATCH --job-name=feature_counts
#SBATCH --output=logs/09_feature_counts/feature_counts_%A.out
#SBATCH --error=logs/09_feature_counts/feature_counts_%A.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH --partition="pibu_el8"

# Load required modules
module load Subread/2.0.3-GCC-10.3.0

# Set input and output directories
input_dir="08_star_alignment_2nd_pass"
output_dir="09_feature_counts_s1"

# Create output directory for feature counts if it doesn't exist
mkdir -p "$output_dir"

# Set output file path for feature counts
output_counts="$output_dir/feature_counts.txt"

# Run featureCounts
featureCounts -T 16 \
    -a reference/Ensmbl/Danio_rerio/v109/Danio_rerio.GRCz11.109.gtf \
    -o "$output_counts" \
    -t exon \
    -g gene_id \
    -s 2 \
    "$input_dir"/*.bam

# Check if featureCounts completed successfully
if [ $? -eq 0 ]; then
    echo "Feature counts completed successfully"
else
    echo "Feature counts failed"
fi
