#!/usr/bin/env bash
# Reproduce el procesamiento ejecutado para SRR38913145.
# Ejecutar desde la raíz del repositorio: bash scripts/run_srr38913145_pilot.sh
#
# No descarga input ni instala software. Ver docs/SETUP.md y docs/DATA_PROVENANCE.md.
# El script no borra salidas existentes: usa nombres fechados/definidos en el proyecto.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CUTADAPT=(uv run cutadapt)
VSEARCH="./tools/vsearch/bin/vsearch"
CLI=(uv run fungi-discovery)

R1="data/raw/SRR38913145/SRR38913145_1.fastq.gz"
R2="data/raw/SRR38913145/SRR38913145_2.fastq.gz"
TRIM="data/trimmed/SRR38913145"
MERGED="data/merged/SRR38913145"
ASV="data/asv/SRR38913145"
REF="data/reference/unite_v10_dynamic_fungi_2025-02-19"

mkdir -p "$TRIM" "$MERGED" "$ASV" results logs

"${CUTADAPT[@]}" \
  -g GCATCGATGAAGAACGCAGC \
  -G TCCTCCGCTTATTGATATGC \
  --pair-filter any --discard-untrimmed \
  -q 20,20 --max-n 0 --minimum-length 100 --cores 4 \
  -o "$TRIM/SRR38913145_R1.trimmed.fastq.gz" \
  -p "$TRIM/SRR38913145_R2.trimmed.fastq.gz" \
  "$R1" "$R2" \
  2>&1 | tee logs/2026-07-31_cutadapt_SRR38913145.log

"$VSEARCH" \
  --fastq_mergepairs "$TRIM/SRR38913145_R1.trimmed.fastq.gz" \
  --reverse "$TRIM/SRR38913145_R2.trimmed.fastq.gz" \
  --fastq_minovlen 20 --fastq_maxdiffs 5 --fastq_maxee 1.0 \
  --fastqout "$MERGED/SRR38913145.merged.fastq" \
  --fastqout_notmerged_fwd "$MERGED/SRR38913145.not_merged_R1.fastq" \
  --fastqout_notmerged_rev "$MERGED/SRR38913145.not_merged_R2.fastq" \
  --threads 4 \
  2>&1 | tee logs/2026-07-31_vsearch_merge_SRR38913145.log

"$VSEARCH" \
  --fastx_uniques "$MERGED/SRR38913145.merged.fastq" \
  --fastaout "$ASV/uniques_all.fasta" --sizeout \
  --relabel SRR38913145_unique_ \
  2>&1 | tee logs/2026-07-31_vsearch_derep_SRR38913145.log

"$VSEARCH" \
  --sortbysize "$ASV/uniques_all.fasta" \
  --output "$ASV/uniques_abundance_ge2.fasta" \
  --minsize 2 --sizein --sizeout \
  2>&1 | tee logs/2026-07-31_vsearch_sortbysize_SRR38913145.log

"$VSEARCH" \
  --uchime3_denovo "$ASV/uniques_abundance_ge2.fasta" \
  --nonchimeras "$ASV/nonchimeric_candidates_ge2.fasta" \
  --chimeras "$ASV/chimeras_denovo_ge2.fasta" \
  --uchimeout "$ASV/uchime3_denovo.tsv" \
  --sizein --sizeout \
  2>&1 | tee logs/2026-07-31_vsearch_uchime3_SRR38913145.log

"${CLI[@]}" screen \
  --queries "$ASV/nonchimeric_candidates_ge2.fasta" \
  --database "$REF" \
  --report results/SRR38913145_unite_v10_megablast_report.tsv \
  --min-length 150 --max-n-percent 0 --known-identity 97 --min-coverage 80 \
  --threads 4 --blast-task megablast \
  2>&1 | tee logs/2026-07-31_megablast_unite_v10_SRR38913145.log

"${CLI[@]}" annotate \
  --report results/SRR38913145_unite_v10_megablast_report.tsv \
  --taxonomy data/reference/unite_v10_dynamic_fungi_2025-02-19.taxonomy.tsv \
  --queries "$ASV/nonchimeric_candidates_ge2.fasta" \
  --output results/SRR38913145_unite_v10_annotated.tsv \
  --min-abundance 5 \
  --priority-output results/SRR38913145_unite_v10_candidates_abundance_ge5.tsv

echo "Piloto terminado. Lee docs/RESULTS_SRR38913145.md antes de interpretar las candidatas."
