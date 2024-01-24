#!/bin/bash
#SBATCH --job-name=multiqc
#SBATCH --output=logs/06_multiqc_post_trimming/multiqc_%j.out
#SBATCH --error=logs/06_multiqc_post_trimming/multiqc_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --partition="pibu_el8"

# Load required modules
# module load UHTS/Analysis/MultiQC/1.11;
module load MultiQC/1.11-foss-2021a



# Run MultiQC and write the output to the same folder
multiqc 05_fastqc_post_trimming_output/ -o 05_fastqc_post_trimming_output/

