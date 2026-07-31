#!/usr/bin/env bash
# Descarga las entradas públicas del piloto SRR38913145 y verifica MD5 publicados por ENA.
# Ejecutar desde raíz del repositorio: bash scripts/fetch_srr38913145_inputs.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RUN="SRR38913145"
DEST="data/raw/$RUN"
mkdir -p "$DEST"

curl --fail --location --retry 3 --continue-at - \
  -o "$DEST/${RUN}_1.fastq.gz" \
  "https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR389/045/$RUN/${RUN}_1.fastq.gz"
curl --fail --location --retry 3 --continue-at - \
  -o "$DEST/${RUN}_2.fastq.gz" \
  "https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR389/045/$RUN/${RUN}_2.fastq.gz"

expected_r1="f0346886e29277bd56ceb0c7b8f3b728"
expected_r2="4155f0afa7b0f3114505ffadfb6d5c90"
printf '%s  %s\n%s  %s\n' \
  "$expected_r1" "$DEST/${RUN}_1.fastq.gz" \
  "$expected_r2" "$DEST/${RUN}_2.fastq.gz" | md5sum --check --strict

echo "Entradas verificadas. Fuente y contexto: docs/DATA_PROVENANCE.md"
