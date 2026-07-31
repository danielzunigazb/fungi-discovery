"""Command-line interface for fungi-discovery."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from Bio import Entrez

from fungi_discovery.annotation import annotate_report
from fungi_discovery.core import (
    clean_fasta,
    fasta_records,
    parse_best_hits,
    results_from_hits,
    write_report,
)

DEFAULT_NCBI_QUERY = 'Fungi[Organism] AND ("internal transcribed spacer"[Title] OR ITS[Title])'


def find_executable(name: str, blast_bin: Path | None) -> str:
    """Find an executable in an explicit BLAST directory or PATH."""
    if blast_bin is not None:
        local = blast_bin / name
        if local.is_file():
            return str(local)
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(f"No encontré {name}. Instala BLAST+ o usa --blast-bin.")


def fetch_reference(args: argparse.Namespace) -> None:
    if "@" not in args.email:
        raise ValueError("NCBI exige un correo de contacto válido: --email tu_correo@dominio")
    Entrez.email = args.email
    if args.api_key:
        Entrez.api_key = args.api_key

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    print("Buscando ITS fúngicos en NCBI…")
    with Entrez.esearch(db="nuccore", term=args.query, retmax=0, usehistory="y") as handle:
        search = Entrez.read(handle)
    total = int(search["Count"])
    if total == 0:
        raise ValueError("La búsqueda no devolvió secuencias. Cambia --query.")

    count = min(total, args.max_records)
    print(
        f"NCBI encontró {total:,} registros; se descargarán {count:,} para esta referencia piloto."
    )
    with output.open("w", encoding="utf-8") as destination:
        for start in range(0, count, args.batch_size):
            batch = min(args.batch_size, count - start)
            print(f"  {start + 1:,}-{start + batch:,} / {count:,}")
            with Entrez.efetch(
                db="nuccore",
                rettype="fasta",
                retmode="text",
                retstart=start,
                retmax=batch,
                webenv=search["WebEnv"],
                query_key=search["QueryKey"],
            ) as handle:
                destination.write(handle.read())
            time.sleep(0.4 if not args.api_key else 0.12)
    print(f"Referencia guardada en: {output}")


def make_database(args: argparse.Namespace) -> None:
    if not args.fasta.is_file():
        raise FileNotFoundError(f"No existe la referencia: {args.fasta}")
    args.prefix.parent.mkdir(parents=True, exist_ok=True)
    command = [
        find_executable("makeblastdb", args.blast_bin),
        "-in",
        str(args.fasta),
        "-dbtype",
        "nucl",
        "-parse_seqids",
        "-out",
        str(args.prefix),
    ]
    subprocess.run(command, check=True)
    print(f"Base BLAST creada: {args.prefix}")


def screen(args: argparse.Namespace) -> None:
    work_dir = args.report.parent / ".work"
    cleaned = work_dir / f"{args.report.stem}.queries_clean.fasta"
    blast_table = work_dir / f"{args.report.stem}.blast_hits.tsv"
    accepted, rejected = clean_fasta(args.queries, cleaned, args.min_length, args.max_n_percent)
    if accepted == 0:
        raise ValueError(
            "Ninguna secuencia pasó el control de calidad. Revisa el FASTA o los umbrales."
        )
    print(f"Control de calidad: {accepted:,} aceptadas; {rejected:,} excluidas.")

    command = [
        find_executable("blastn", args.blast_bin),
        "-query",
        str(cleaned),
        "-db",
        str(args.database),
        "-task",
        args.blast_task,
        "-max_target_seqs",
        "5",
        "-max_hsps",
        "1",
        "-num_threads",
        str(args.threads),
        "-outfmt",
        "6 qseqid sseqid pident length qlen qstart qend evalue bitscore stitle",
        "-out",
        str(blast_table),
    ]
    print("Comparando contra la referencia local con BLAST…")
    subprocess.run(command, check=True)
    results = results_from_hits(
        fasta_records(cleaned),
        parse_best_hits(blast_table),
        args.known_identity,
        args.min_coverage,
    )
    write_report(args.report, results)
    counts = Counter(result.classification for result in results)
    print(f"Reporte: {args.report}")
    print("Resumen: " + ", ".join(f"{name}={count}" for name, count in sorted(counts.items())))
    print(
        "Una candidata NO es una especie nueva confirmada: "
        "verifica quimeras, taxonomía y replicación."
    )


def annotate(args: argparse.Namespace) -> None:
    total, candidates = annotate_report(
        args.report,
        args.taxonomy,
        args.queries,
        args.output,
        args.priority_output,
        args.min_abundance,
    )
    print(f"Reporte anotado: {args.output} ({total:,} variantes)")
    print(
        f"Candidatas con abundancia >= {args.min_abundance}: "
        f"{args.priority_output} ({candidates:,})"
    )


def path_argument(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Triage reproducible de secuencias ITS; no confirma especies nuevas.",
    )
    parser.add_argument(
        "--blast-bin",
        type=path_argument,
        default=Path("tools/blast/bin"),
        help="Directorio de binarios BLAST+. Si no existe, se busca en PATH.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser(
        "fetch-reference", help="Descarga una referencia ITS piloto desde NCBI."
    )
    fetch.add_argument("--email", required=True)
    fetch.add_argument("--api-key")
    fetch.add_argument("--max-records", type=int, default=1000)
    fetch.add_argument("--batch-size", type=int, default=200)
    fetch.add_argument("--query", default=DEFAULT_NCBI_QUERY)
    fetch.add_argument(
        "--output", type=path_argument, default=Path("data/reference/ncbi_fungi_its.fasta")
    )
    fetch.set_defaults(handler=fetch_reference)

    database = commands.add_parser("make-db", help="Construye un índice BLAST de nucleótidos.")
    database.add_argument("--fasta", type=path_argument, required=True)
    database.add_argument(
        "--prefix", type=path_argument, default=Path("data/reference/ncbi_fungi_its")
    )
    database.set_defaults(handler=make_database)

    screen_parser = commands.add_parser(
        "screen", help="Prioriza secuencias ITS divergentes frente a una referencia."
    )
    screen_parser.add_argument("--queries", type=path_argument, required=True)
    screen_parser.add_argument(
        "--database", type=path_argument, default=Path("data/reference/ncbi_fungi_its")
    )
    screen_parser.add_argument(
        "--report", type=path_argument, default=Path("results/candidate_report.tsv")
    )
    screen_parser.add_argument("--min-length", type=int, default=150)
    screen_parser.add_argument("--max-n-percent", type=float, default=5.0)
    screen_parser.add_argument("--known-identity", type=float, default=97.0)
    screen_parser.add_argument("--min-coverage", type=float, default=80.0)
    screen_parser.add_argument("--threads", type=int, default=4)
    screen_parser.add_argument(
        "--blast-task", choices=("megablast", "dc-megablast", "blastn"), default="megablast"
    )
    screen_parser.set_defaults(handler=screen)

    annotate_parser = commands.add_parser(
        "annotate", help="Añade taxonomía UNITE y abundancia al reporte."
    )
    annotate_parser.add_argument("--report", type=path_argument, required=True)
    annotate_parser.add_argument("--taxonomy", type=path_argument, required=True)
    annotate_parser.add_argument("--queries", type=path_argument, required=True)
    annotate_parser.add_argument("--output", type=path_argument, required=True)
    annotate_parser.add_argument("--priority-output", type=path_argument, required=True)
    annotate_parser.add_argument("--min-abundance", type=int, default=5)
    annotate_parser.set_defaults(handler=annotate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2) from error
