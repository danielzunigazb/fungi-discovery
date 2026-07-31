"""Pure data-processing logic for fungal ITS triage."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

DNA_ALPHABET = frozenset("ACGTRYSWKMBDHVN")
REPORT_FIELDS = (
    "query_id",
    "query_length",
    "classification",
    "reason",
    "best_identity_percent",
    "query_coverage_percent",
    "best_reference_id",
    "best_reference_title",
    "evalue",
    "bitscore",
)


@dataclass(frozen=True)
class BlastHit:
    """The relevant fields of a tabular BLAST hit."""

    query_id: str
    subject_id: str
    identity: float
    alignment_length: int
    query_length: int
    query_start: int
    query_end: int
    evalue: str
    bitscore: float
    title: str

    @property
    def query_coverage(self) -> float:
        """Percentage of the query span covered by the alignment.

        `alignment_length` cannot be used here because it may count gaps and
        exceed the query length.
        """
        query_span = abs(self.query_end - self.query_start) + 1
        return query_span / self.query_length * 100


@dataclass(frozen=True)
class ScreeningResult:
    """A classification row written to the screening report."""

    query_id: str
    query_length: int
    classification: str
    reason: str
    best_identity_percent: str = ""
    query_coverage_percent: str = ""
    best_reference_id: str = ""
    best_reference_title: str = ""
    evalue: str = ""
    bitscore: str = ""

    def as_row(self) -> dict[str, str | int]:
        return {
            "query_id": self.query_id,
            "query_length": self.query_length,
            "classification": self.classification,
            "reason": self.reason,
            "best_identity_percent": self.best_identity_percent,
            "query_coverage_percent": self.query_coverage_percent,
            "best_reference_id": self.best_reference_id,
            "best_reference_title": self.best_reference_title,
            "evalue": self.evalue,
            "bitscore": self.bitscore,
        }


def fasta_records(path: Path) -> Iterable[SeqRecord]:
    """Yield FASTA records or raise a useful error for a missing input."""
    if not path.is_file():
        raise FileNotFoundError(f"No existe el FASTA: {path}")
    yield from SeqIO.parse(path, "fasta")


def clean_fasta(
    source: Path,
    destination: Path,
    min_length: int,
    max_n_percent: float,
) -> tuple[int, int]:
    """Normalize DNA FASTA and return (accepted_records, rejected_records)."""
    accepted: list[SeqRecord] = []
    rejected = 0
    seen_ids: set[str] = set()

    for number, record in enumerate(fasta_records(source), start=1):
        sequence = "".join(str(record.seq).upper().replace("-", "").split())
        sequence_id = (record.id or "").split()[0] if record.id else f"sequence_{number}"
        if sequence_id in seen_ids:
            sequence_id = f"{sequence_id}_{number}"
        seen_ids.add(sequence_id)
        n_percent = sequence.count("N") / len(sequence) * 100 if sequence else 100.0
        if (
            len(sequence) < min_length
            or n_percent > max_n_percent
            or not set(sequence) <= DNA_ALPHABET
        ):
            rejected += 1
            continue
        accepted.append(SeqRecord(Seq(sequence), id=sequence_id, name=sequence_id, description=""))

    destination.parent.mkdir(parents=True, exist_ok=True)
    SeqIO.write(accepted, destination, "fasta")
    return len(accepted), rejected


def parse_best_hits(path: Path) -> dict[str, BlastHit]:
    """Return the highest-bitscore BLAST hit for each query in an outfmt 6 TSV."""
    fields = (
        "query_id",
        "subject_id",
        "identity",
        "alignment_length",
        "query_length",
        "query_start",
        "query_end",
        "evalue",
        "bitscore",
        "title",
    )
    hits: dict[str, BlastHit] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t", fieldnames=fields):
            hit = BlastHit(
                query_id=row["query_id"],
                subject_id=row["subject_id"],
                identity=float(row["identity"]),
                alignment_length=int(row["alignment_length"]),
                query_length=int(row["query_length"]),
                query_start=int(row["query_start"]),
                query_end=int(row["query_end"]),
                evalue=row["evalue"],
                bitscore=float(row["bitscore"]),
                title=row["title"],
            )
            previous = hits.get(hit.query_id)
            if previous is None or hit.bitscore > previous.bitscore:
                hits[hit.query_id] = hit
    return hits


def classify(
    identity: float, coverage: float, known_identity: float, min_coverage: float
) -> tuple[str, str]:
    """Classify an alignment for triage, never for formal species designation."""
    if coverage < min_coverage:
        return "ALINEAMIENTO_PARCIAL", "No clasificar: el tramo alineado es insuficiente."
    if identity >= known_identity:
        return "COINCIDENCIA_CONOCIDA", "Compatible con una referencia conocida para este umbral."
    if identity >= 90:
        return "CANDIDATA_DIVERGENTE", "Priorizar validación: ITS distante de la mejor referencia."
    return (
        "CANDIDATA_MUY_DIVERGENTE",
        "Prioridad alta, pero descartar quimera, error o ADN no fúngico.",
    )


def results_from_hits(
    records: Iterable[SeqRecord],
    hits: dict[str, BlastHit],
    known_identity: float,
    min_coverage: float,
) -> list[ScreeningResult]:
    """Classify query records against their best hits."""
    results: list[ScreeningResult] = []
    for record in records:
        query_id = record.id or ""
        hit = hits.get(query_id)
        if hit is None:
            results.append(
                ScreeningResult(
                    query_id=query_id,
                    query_length=len(record),
                    classification="SIN_MATCH_CERCANO",
                    reason="Sin alineamiento con esta referencia; "
                    "requiere verificación independiente.",
                )
            )
            continue
        coverage = hit.query_coverage
        label, reason = classify(hit.identity, coverage, known_identity, min_coverage)
        results.append(
            ScreeningResult(
                query_id=query_id,
                query_length=len(record),
                classification=label,
                reason=reason,
                best_identity_percent=f"{hit.identity:.2f}",
                query_coverage_percent=f"{coverage:.2f}",
                best_reference_id=hit.subject_id,
                best_reference_title=hit.title,
                evalue=hit.evalue,
                bitscore=f"{hit.bitscore:g}",
            )
        )
    return results


def write_report(path: Path, results: Iterable[ScreeningResult]) -> None:
    """Write a stable TSV screening report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(result.as_row() for result in results)
