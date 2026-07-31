from __future__ import annotations

from pathlib import Path

import pytest
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from fungi_discovery.core import (
    BlastHit,
    classify,
    clean_fasta,
    parse_best_hits,
    results_from_hits,
    write_report,
)


def write_fasta(path: Path, records: list[SeqRecord]) -> None:
    SeqIO.write(records, path, "fasta")


def test_clean_fasta_normalizes_deduplicates_and_filters(tmp_path: Path) -> None:
    source = tmp_path / "input.fasta"
    destination = tmp_path / "nested" / "clean.fasta"
    write_fasta(
        source,
        [
            SeqRecord(Seq("acgt-acgt"), id="same"),
            SeqRecord(Seq("ACGTACGT"), id="same"),
            SeqRecord(Seq("ACGTNNNN"), id="too_many_n"),
            SeqRecord(Seq("ACGTXCGT"), id="invalid"),
            SeqRecord(Seq("ACG"), id="short"),
        ],
    )

    accepted, rejected = clean_fasta(source, destination, min_length=5, max_n_percent=10)

    assert (accepted, rejected) == (2, 3)
    records = list(SeqIO.parse(destination, "fasta"))
    assert [record.id for record in records] == ["same", "same_2"]
    assert [str(record.seq) for record in records] == ["ACGTACGT", "ACGTACGT"]


def test_clean_fasta_rejects_missing_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No existe el FASTA"):
        clean_fasta(tmp_path / "missing.fasta", tmp_path / "output.fasta", 100, 5)


def test_blast_hit_coverage_uses_query_span_not_alignment_length() -> None:
    hit = BlastHit("q", "s", 99, 120, 100, 1, 100, "1e-20", 50, "title")

    assert hit.query_coverage == 100


def test_parse_best_hits_selects_highest_bitscore(tmp_path: Path) -> None:
    table = tmp_path / "hits.tsv"
    table.write_text(
        "q1\ts_low\t99\t100\t100\t1\t100\t1e-20\t50\tlow\n"
        "q1\ts_high\t95\t100\t100\t1\t100\t1e-10\t70\thigh\n"
        "q2\ts2\t90\t80\t100\t1\t80\t1e-5\t10\tpartial\n",
        encoding="utf-8",
    )

    hits = parse_best_hits(table)

    assert hits["q1"].subject_id == "s_high"
    assert hits["q1"].bitscore == 70
    assert hits["q2"].query_coverage == 80


@pytest.mark.parametrize(
    ("identity", "coverage", "expected"),
    [
        (99, 70, "ALINEAMIENTO_PARCIAL"),
        (99, 100, "COINCIDENCIA_CONOCIDA"),
        (96, 100, "CANDIDATA_DIVERGENTE"),
        (89, 100, "CANDIDATA_MUY_DIVERGENTE"),
    ],
)
def test_classify(identity: float, coverage: float, expected: str) -> None:
    label, _ = classify(identity, coverage, known_identity=97, min_coverage=80)

    assert label == expected


def test_results_from_hits_and_write_report(tmp_path: Path) -> None:
    records = [
        SeqRecord(Seq("ACGT" * 25), id="known"),
        SeqRecord(Seq("ACGT" * 25), id="missing"),
    ]
    hits = {
        "known": BlastHit("known", "reference", 98, 100, 100, 1, 100, "1e-20", 80, "Known fungus")
    }

    results = results_from_hits(records, hits, known_identity=97, min_coverage=80)
    report = tmp_path / "result.tsv"
    write_report(report, results)

    lines = report.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert "COINCIDENCIA_CONOCIDA" in lines[1]
    assert "SIN_MATCH_CERCANO" in lines[2]
