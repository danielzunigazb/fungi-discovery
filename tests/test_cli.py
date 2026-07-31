from __future__ import annotations

from pathlib import Path

import pytest

from fungi_discovery.cli import build_parser, find_executable


def test_parser_defaults_to_megablast() -> None:
    args = build_parser().parse_args(["screen", "--queries", "queries.fasta"])

    assert args.blast_task == "megablast"
    assert args.database == Path("data/reference/ncbi_fungi_its")


def test_parser_accepts_annotate_command() -> None:
    args = build_parser().parse_args(
        [
            "annotate",
            "--report",
            "report.tsv",
            "--taxonomy",
            "taxonomy.tsv",
            "--queries",
            "queries.fasta",
            "--output",
            "annotated.tsv",
            "--priority-output",
            "priority.tsv",
        ]
    )

    assert args.min_abundance == 5
    assert args.output == Path("annotated.tsv")


def test_find_executable_uses_explicit_directory(tmp_path: Path) -> None:
    executable = tmp_path / "blastn"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")

    assert find_executable("blastn", tmp_path) == str(executable)


def test_find_executable_raises_for_missing_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("fungi_discovery.cli.shutil.which", lambda _: None)

    with pytest.raises(FileNotFoundError, match="No encontré blastn"):
        find_executable("blastn", tmp_path)
