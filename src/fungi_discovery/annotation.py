"""UNITE taxonomy and abundance annotation for screening reports."""

from __future__ import annotations

import csv
from pathlib import Path

from Bio import SeqIO


def abundance_from_description(description: str) -> int:
    """Read the VSEARCH `size=<count>;` abundance annotation."""
    for item in description.split(";"):
        if item.startswith("size="):
            return int(item.removeprefix("size="))
    raise ValueError(f"No encontré size= en: {description}")


def read_taxonomy(path: Path) -> dict[str, str]:
    """Read a QIIME/UNITE two-column taxonomy TSV."""
    taxonomy: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != ["Feature ID", "Taxon"]:
            raise ValueError(f"Cabecera inesperada en taxonomía: {reader.fieldnames}")
        for row in reader:
            taxonomy[row["Feature ID"]] = row["Taxon"]
    return taxonomy


def priority(classification: str, abundance: int, min_abundance: int) -> str:
    """Assign a review priority; this is not a taxonomic conclusion."""
    if classification == "CANDIDATA_MUY_DIVERGENTE" and abundance >= min_abundance:
        return "ALTA_REVISION"
    if classification == "CANDIDATA_DIVERGENTE" and abundance >= min_abundance:
        return "REVISION"
    if classification.startswith("CANDIDATA"):
        return "BAJA_ABUNDANCIA"
    return "NO_PRIORIZAR"


def annotate_report(
    report_path: Path,
    taxonomy_path: Path,
    queries_path: Path,
    output_path: Path,
    priority_output_path: Path,
    min_abundance: int,
) -> tuple[int, int]:
    """Annotate a screening report and return (all_rows, priority_rows)."""
    taxonomy = read_taxonomy(taxonomy_path)
    abundance = {
        record.id: abundance_from_description(record.description)
        for record in SeqIO.parse(queries_path, "fasta")
    }
    rows: list[dict[str, str]] = []
    with report_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            query_id = row["query_id"]
            if query_id not in abundance:
                raise ValueError(f"Query ausente del FASTA: {query_id}")
            count = abundance[query_id]
            row["abundance_reads"] = str(count)
            row["unite_taxonomy"] = taxonomy.get(row["best_reference_id"], "")
            row["priority"] = priority(row["classification"], count, min_abundance)
            rows.append(row)

    rows.sort(key=lambda row: (-int(row["abundance_reads"]), row["query_id"]))
    fields = list(rows[0]) if rows else []
    priority_rows = [
        row
        for row in rows
        if row["classification"].startswith("CANDIDATA")
        and int(row["abundance_reads"]) >= min_abundance
    ]
    for target, selected in ((output_path, rows), (priority_output_path, priority_rows)):
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(selected)
    return len(rows), len(priority_rows)
