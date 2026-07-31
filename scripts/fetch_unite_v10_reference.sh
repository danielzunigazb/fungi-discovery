#!/usr/bin/env bash
# Descarga UNITE v10.0 (2025-02-19), extrae Fungi/dynamic/sin singletons y verifica SHA-256.
# Ejecutar desde raíz del repositorio: bash scripts/fetch_unite_v10_reference.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REFERENCE_DIR="data/reference"
ARCHIVE="$REFERENCE_DIR/unite_v10_fungi_qiime_2025-02-19.tgz"
FASTA="$REFERENCE_DIR/unite_v10_dynamic_fungi_2025-02-19.fasta"
TAXONOMY="$REFERENCE_DIR/unite_v10_dynamic_fungi_2025-02-19.taxonomy.tsv"
EXPECTED_ARCHIVE_SHA256="9a4c185308790f3667f50198659969525f95860d08aaf156ec5f5d309b2723ea"
EXPECTED_FASTA_SHA256="834b9af8d9c07e69a2ce826954fdb7320eea6b28dd0213f3990cb76e644e0aff"
EXPECTED_TAXONOMY_SHA256="ff3094c66da87eedc442e7cc3f84517d4c4d4e0524318d579386f629048433fa"
URL="https://s3.hpc.ut.ee/plutof-public/original/6fa9d7a2-1d4a-4846-ab03-59a251f9477f.tgz"

mkdir -p "$REFERENCE_DIR"
curl --fail --location --retry 4 --continue-at - -o "$ARCHIVE" "$URL"
printf '%s  %s\n' "$EXPECTED_ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check --strict

tar xzf "$ARCHIVE" -C "$REFERENCE_DIR" \
  --transform='s|developer/sh_refs_qiime_ver10_dynamic_19.02.2025_dev.fasta|unite_v10_dynamic_fungi_2025-02-19.fasta|' \
  --transform='s|developer/sh_taxonomy_qiime_ver10_dynamic_19.02.2025_dev.txt|unite_v10_dynamic_fungi_2025-02-19.taxonomy.tsv|' \
  developer/sh_refs_qiime_ver10_dynamic_19.02.2025_dev.fasta \
  developer/sh_taxonomy_qiime_ver10_dynamic_19.02.2025_dev.txt
printf '%s  %s\n%s  %s\n' \
  "$EXPECTED_FASTA_SHA256" "$FASTA" \
  "$EXPECTED_TAXONOMY_SHA256" "$TAXONOMY" | sha256sum --check --strict

uv run fungi-discovery make-db --fasta "$FASTA" --prefix "${FASTA%.fasta}"
echo "UNITE lista. Consulta licencia/cita/procedencia en docs/DATA_PROVENANCE.md"
