# 🔬 fungi-discovery

**Reproducible fungal ITS screening and candidate triage.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Herramientas reproducibles para procesar amplicones ITS de hongos y **priorizar secuencias que requieren revisión taxonómica**.

> **Límite científico:** una coincidencia BLAST distante no demuestra una especie nueva. Este software produce candidatas de revisión; confirmar o describir una especie requiere controles, réplicas, referencias curadas, evidencia adicional y, cuando corresponda, una muestra/voucher y taxonomía formal.

## Estado

- Paquete Python instalable con CLI: `fungi-discovery`.
- Pipeline piloto documentado: ITS2 de mucílago de café fermentado de Boyacá, Colombia.
- Referencia de análisis: UNITE v10.0, release 2025-02-19, Fungi, delimitación dinámica.
- Calidad automatizada: Ruff, Ty, Pytest, cobertura ≥85%, build y GitHub Actions.

## Inicio rápido

```bash
git clone https://github.com/danielzunigazb/fungi-discovery
cd fungi-discovery
uv sync --extra dev --extra preprocess
make check
uv run fungi-discovery --help
```

Instala BLAST+ y VSEARCH localmente siguiendo [`docs/SETUP.md`](docs/SETUP.md). Los tests no necesitan red, BLAST, VSEARCH ni datos grandes.

## CLI

```bash
# Descargar una referencia piloto pequeña de NCBI. No escribas tu correo en Git.
export NCBI_EMAIL='tu_correo@dominio.com'
uv run fungi-discovery fetch-reference --email "$NCBI_EMAIL" --max-records 1000

# Crear índice BLAST local.
uv run fungi-discovery make-db \
  --fasta data/reference/ncbi_fungi_its.fasta \
  --prefix data/reference/ncbi_fungi_its

# Clasificar ASVs o consensos ITS en FASTA contra una referencia local.
uv run fungi-discovery screen \
  --queries data/queries/muestra_its.fasta \
  --database data/reference/unite_v10_dynamic_fungi_2025-02-19 \
  --report results/muestra_unite.tsv \
  --blast-task megablast

# Añadir abundancia VSEARCH (size=N) y taxonomía UNITE al reporte.
uv run fungi-discovery annotate \
  --report results/muestra_unite.tsv \
  --taxonomy data/reference/unite_v10_dynamic_fungi_2025-02-19.taxonomy.tsv \
  --queries data/queries/muestra_its.fasta \
  --output results/muestra_unite_annotated.tsv \
  --priority-output results/muestra_candidates_ge5.tsv
```

Para una búsqueda rápida de coincidencias cercanas se usa `megablast`. Las secuencias sin hit cercano deben pasar por una segunda búsqueda más sensible (`--blast-task dc-megablast`) y revisión de cobertura antes de interpretarse.

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/SETUP.md`](docs/SETUP.md) | Instalación, binarios externos y versiones |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Diseño, interfaces y política de cambios |
| [`docs/PIPELINE.md`](docs/PIPELINE.md) | Método, umbrales y validación científica |
| [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md) | Fuentes, licencias, URLs y checksums |
| [`docs/WORKLOG.md`](docs/WORKLOG.md) | Bitácora reproducible de decisiones y ejecuciones |
| [`docs/RESULTS_SRR38913145.md`](docs/RESULTS_SRR38913145.md) | Resultados del piloto y límites de interpretación |
| [`docs/adr/`](docs/adr/) | Decisiones de arquitectura |

## Desarrollo

```bash
make format      # Formatea src/ y tests/
make lint        # Ruff
make typecheck   # Ty
make test        # Pytest + cobertura
make check       # lint + tipos + tests
make build       # wheel + source distribution
```

## Licencia

MIT. Las referencias, datasets y herramientas externas conservan sus propias licencias.