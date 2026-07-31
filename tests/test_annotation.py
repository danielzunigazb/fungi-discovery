from __future__ import annotations

import csv
from pathlib import Path

import pytest

from fungi_discovery.annotation import (
    abundance_from_description,
    annotate_report,
    priority,
    read_taxonomy,
)


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)


def test_abundance_from_description() -> None:
    assert abundance_from_description("ASV_1;size=42;") == 42
    with pytest.raises(ValueError, match="No encontré size"):
        abundance_from_description("ASV_1")


@pytest.mark.parametrize(
    ("classification", "abundance", "expected"),
    [
        ("CANDIDATA_MUY_DIVERGENTE", 5, "ALTA_REVISION"),
        ("CANDIDATA_DIVERGENTE", 5, "REVISION"),
        ("CANDIDATA_DIVERGENTE", 4, "BAJA_ABUNDANCIA"),
        ("COINCIDENCIA_CONOCIDA", 100, "NO_PRIORIZAR"),
    ],
)
def test_priority(classification: str, abundance: int, expected: str) -> None:
    assert priority(classification, abundance, min_abundance=5) == expected


def test_read_taxonomy_rejects_wrong_header(tmp_path: Path) -> None:
    path = tmp_path / "bad.tsv"
    path.write_text("id\ttaxonomy\nref\tFungi\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Cabecera inesperada"):
        read_taxonomy(path)


def test_annotate_report_writes_sorted_all_and_priority_outputs(tmp_path: Path) -> None:
    queries = tmp_path / "queries.fasta"
    queries.write_text(
        ">q_low;size=2;\nACGT\n>q_high;size=7;\nTGCA\n>q_known;size=20;\nAAAA\n",
        encoding="utf-8",
    )
    taxonomy = tmp_path / "taxonomy.tsv"
    write_tsv(
        taxonomy,
        ["Feature ID", "Taxon"],
        [["ref_high", "k__Fungi;s__Example"], ["ref_known", "k__Fungi;s__Known"]],
    )
    report = tmp_path / "report.tsv"
    write_tsv(
        report,
        ["query_id", "classification", "best_reference_id"],
        [
            ["q_low;size=2;", "CANDIDATA_DIVERGENTE", "ref_high"],
            ["q_high;size=7;", "CANDIDATA_MUY_DIVERGENTE", "ref_high"],
            ["q_known;size=20;", "COINCIDENCIA_CONOCIDA", "ref_known"],
        ],
    )
    output = tmp_path / "annotated.tsv"
    candidates = tmp_path / "candidates.tsv"

    total, candidate_count = annotate_report(
        report, taxonomy, queries, output, candidates, min_abundance=5
    )

    assert (total, candidate_count) == (3, 1)
    rows = list(csv.DictReader(output.open(encoding="utf-8"), delimiter="\t"))
    assert [row["query_id"] for row in rows] == [
        "q_known;size=20;",
        "q_high;size=7;",
        "q_low;size=2;",
    ]
    assert rows[1]["priority"] == "ALTA_REVISION"
    assert rows[1]["unite_taxonomy"] == "k__Fungi;s__Example"
    candidate_rows = list(csv.DictReader(candidates.open(encoding="utf-8"), delimiter="\t"))
    assert [row["query_id"] for row in candidate_rows] == ["q_high;size=7;"]


def test_annotate_report_rejects_query_missing_from_fasta(tmp_path: Path) -> None:
    queries = tmp_path / "queries.fasta"
    queries.write_text(">q1;size=5;\nACGT\n", encoding="utf-8")
    taxonomy = tmp_path / "taxonomy.tsv"
    write_tsv(taxonomy, ["Feature ID", "Taxon"], [])
    report = tmp_path / "report.tsv"
    write_tsv(
        report,
        ["query_id", "classification", "best_reference_id"],
        [["missing", "CANDIDATA_DIVERGENTE", ""]],
    )

    with pytest.raises(ValueError, match="Query ausente"):
        annotate_report(
            report, taxonomy, queries, tmp_path / "out.tsv", tmp_path / "priority.tsv", 5
        )
