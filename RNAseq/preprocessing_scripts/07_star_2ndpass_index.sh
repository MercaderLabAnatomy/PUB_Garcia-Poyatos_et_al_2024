#!/bin/bash
#SBATCH --job-name=star_2ndindex
#SBATCH --output=logs/07_star_2ndpass_index/star_alignment_%A_%a.out
#SBATCH --error=logs/07_star_2ndpass_index/star_alignment_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH --partition="pibu_el8"

# Load STAR module
# module load star
module load STAR/2.7.10a_alpha_220601-GCC-10.3.0


STAR --runMode genomeGenerate \
--genomeDir star_2ndpass_index/ \
--genomeFastaFiles reference/Ensmbl/Danio_rerio/v108/Danio_rerio.GRCz11.dna_sm.primary_assembly.fa \
--sjdbGTFfile reference/Ensmbl/Danio_rerio/v109/Danio_rerio.GRCz11.109.gtf \
--runThreadN 32 \
--sjdbOverhang 99 \
--sjdbFileChrStartEnd 06_star_alignment_1st_pass/*.SJ.filtered.tab
