from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from fungi_discovery import cli


def test_fetch_reference_rejects_invalid_email(tmp_path: Path) -> None:
    args = argparse.Namespace(email="invalid", api_key=None, output=tmp_path / "ref.fasta")

    with pytest.raises(ValueError, match="correo de contacto"):
        cli.fetch_reference(args)


def test_make_database_invokes_blast(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fasta = tmp_path / "reference.fasta"
    fasta.write_text(">ref\nACGT\n", encoding="utf-8")
    prefix = tmp_path / "db" / "reference"
    calls: list[list[str]] = []
    monkeypatch.setattr(cli, "find_executable", lambda name, _: f"/fake/{name}")
    monkeypatch.setattr(cli.subprocess, "run", lambda command, check: calls.append(command))
    args = argparse.Namespace(fasta=fasta, prefix=prefix, blast_bin=None)

    cli.make_database(args)

    assert prefix.parent.is_dir()
    assert calls == [
        [
            "/fake/makeblastdb",
            "-in",
            str(fasta),
            "-dbtype",
            "nucl",
            "-parse_seqids",
            "-out",
            str(prefix),
        ]
    ]


def test_make_database_rejects_missing_fasta(tmp_path: Path) -> None:
    args = argparse.Namespace(
        fasta=tmp_path / "missing.fasta", prefix=tmp_path / "db", blast_bin=None
    )

    with pytest.raises(FileNotFoundError, match="No existe la referencia"):
        cli.make_database(args)


def test_screen_runs_blast_and_writes_report(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    queries = tmp_path / "queries.fasta"
    queries.write_text(">query\nACGTACGT\n", encoding="utf-8")
    report = tmp_path / "results" / "report.tsv"
    calls: list[list[str]] = []

    def fake_run(command: list[str], check: bool) -> None:
        calls.append(command)
        output = Path(command[command.index("-out") + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "query\tref\t98\t8\t8\t1\t8\t1e-5\t20\tKnown fungus\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(cli, "find_executable", lambda name, _: f"/fake/{name}")
    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    args = argparse.Namespace(
        queries=queries,
        report=report,
        database=tmp_path / "database",
        min_length=4,
        max_n_percent=5.0,
        known_identity=97.0,
        min_coverage=80.0,
        threads=2,
        blast_task="megablast",
        blast_bin=None,
    )

    cli.screen(args)

    assert calls[0][0] == "/fake/blastn"
    assert "megablast" in calls[0]
    assert "COINCIDENCIA_CONOCIDA" in report.read_text(encoding="utf-8")


def test_screen_rejects_when_quality_filter_accepts_nothing(tmp_path: Path) -> None:
    queries = tmp_path / "queries.fasta"
    queries.write_text(">short\nACG\n", encoding="utf-8")
    args = argparse.Namespace(
        queries=queries,
        report=tmp_path / "report.tsv",
        database=tmp_path / "database",
        min_length=4,
        max_n_percent=5.0,
        known_identity=97.0,
        min_coverage=80.0,
        threads=1,
        blast_task="megablast",
        blast_bin=None,
    )

    with pytest.raises(ValueError, match="Ninguna secuencia"):
        cli.screen(args)


def test_annotate_handler_delegates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called: list[object] = []
    monkeypatch.setattr(cli, "annotate_report", lambda *args: called.append(args) or (4, 2))
    args = argparse.Namespace(
        report=tmp_path / "report.tsv",
        taxonomy=tmp_path / "taxonomy.tsv",
        queries=tmp_path / "queries.fasta",
        output=tmp_path / "out.tsv",
        priority_output=tmp_path / "priority.tsv",
        min_abundance=5,
    )

    cli.annotate(args)

    assert len(called) == 1
    assert called[0][-1] == 5


def test_main_turns_known_errors_into_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    class Parser:
        def parse_args(self) -> argparse.Namespace:
            def failing_handler(_: argparse.Namespace) -> None:
                raise ValueError("bad input")

            return argparse.Namespace(handler=failing_handler)

    monkeypatch.setattr(cli, "build_parser", lambda: Parser())

    with pytest.raises(SystemExit, match="2"):
        cli.main()
