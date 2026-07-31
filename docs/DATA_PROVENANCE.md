# Procedencia de datos

Este archivo registra de dónde vino cada dato y cómo se comprobó. Los datos crudos no se suben a Git; se descargan desde la fuente indicada y se verifican con checksum.

## Referencia ITS piloto de NCBI

| Campo | Valor |
|---|---|
| Base de datos | NCBI Nucleotide (`nuccore`) |
| Consulta | `Fungi[Organism] AND ("internal transcribed spacer"[Title] OR ITS[Title])` |
| Fecha de consulta | 2026-07-30 UTC (fecha de sesión) |
| Registros encontrados | 1.980.731 |
| Registros descargados | 1.000 |
| Archivo | `data/reference/ncbi_fungi_its.fasta` |
| Tamaño | 2,78 MiB |
| Longitudes | mínimo 186 bp; mediana 563 bp; máximo 9.954 bp |
| Método | CLI `fungi-discovery fetch-reference` usando E-utilities y WebEnv/QueryKey |
| Uso | Referencia mínima de prueba; **no** referencia taxonómica final |

La consulta mezcla ITS completo, ITS parcial y registros que contienen genes flanqueantes. Esto es adecuado para probar el software, pero para inferencia taxonómica se debe usar una versión fechada y documentada de UNITE con región/criterio adecuados.

## Referencia curada usada para el ranking: UNITE

| Campo | Valor |
|---|---|
| Base | UNITE v10.0, QIIME release for Fungi |
| Fecha de la release | 2025-02-19 |
| DOI | `10.15156/BIO/3301241` |
| Subconjunto extraído | Fungi; agrupación dinámica; sin singletons; archivos `developer` usados por RESCRIPt |
| Archivo fuente | `sh_qiime_release_19.02.2025.tgz` |
| URL resuelta por API PlutoF | `https://s3.hpc.ut.ee/plutof-public/original/6fa9d7a2-1d4a-4846-ab03-59a251f9477f.tgz` |
| Licencia reportada por la API | CC BY 4.0 |
| SHA-256 archivo fuente | `9a4c185308790f3667f50198659969525f95860d08aaf156ec5f5d309b2723ea` |
| FASTA extraído | `data/reference/unite_v10_dynamic_fungi_2025-02-19.fasta`; 102.137 secuencias |
| Taxonomía extraída | `data/reference/unite_v10_dynamic_fungi_2025-02-19.taxonomy.tsv`; 102.137 IDs |
| Validación | 0 IDs FASTA sin taxonomía y 0 IDs taxonomía sin FASTA |

La respuesta API original se conserva como `metadata/unite_v10_dynamic_fungi_api_response.json`. La release se obtuvo siguiendo el mecanismo oficial de `RESCRIPt get-unite-data`; no se utilizó el clasificador QIIME `.qza` como una base BLAST.

## Piloto: microbioma de mucílago de café, Boyacá, Colombia

| Campo | Valor |
|---|---|
| Archivo de entrada | `data/raw/SRR38913145/SRR38913145_1.fastq.gz`, `SRR38913145_2.fastq.gz` |
| Archivo de metadatos local | `metadata/SRR38913145.json` |
| Archivo de metadatos fuente | `metadata/SAMN60516043.xml` (si se descarga completo) |
| Archivo de procedencia de la muestra | `metadata/SRR38913145.json` |
| Archivo de datos públicos | ENA / SRA |
| Run | `SRR38913145` |
| Study / BioProject | `SRP705069` / `PRJNA1472785` |
| Sample | `SAMN60516043` |
| Estrategia | Amplicon; `PAIRED`; Illumina MiSeq |
| Marcador según título SRA | ITS |
| Muestra | Mucílago de café fermentado, código 605 |
| Lugar | Miraflores, provincia de Lengupá, Boyacá, Colombia; 5.189 N, 73.150611 W |
| Año de colección | 2025 |
| Contexto | Ecosistema agrícola; finca de café; mucílago fermentado |
| Lecturas | 121.873 pares, 301 bp por read |
| Tamaño descargado | R1: 3.125.037 bytes; R2: 3.175.552 bytes según ENA |

### URLs fuente

- Página de run NCBI: https://www.ncbi.nlm.nih.gov/sra/SRR38913145
- Página de BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1472785
- ENA filereport: `https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRR38913145&result=read_run`
- R1: `https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR389/045/SRR38913145/SRR38913145_1.fastq.gz`
- R2: `https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR389/045/SRR38913145/SRR38913145_2.fastq.gz`

### Integridad verificada

| Archivo | MD5 publicado por ENA | MD5 local | Resultado |
|---|---|---|---|
| `SRR38913145_1.fastq.gz` | `f0346886e29277bd56ceb0c7b8f3b728` | `f0346886e29277bd56ceb0c7b8f3b728` | Coincide |
| `SRR38913145_2.fastq.gz` | `4155f0afa7b0f3114505ffadfb6d5c90` | `4155f0afa7b0f3114505ffadfb6d5c90` | Coincide |

### Limitaciones y uso responsable

- Este dataset fue publicado por terceros; se respetan las condiciones del archivo y se atribuye la fuente.
- La muestra procede de un proceso alimentario/agrícola, no de una prospección diseñada para especies desconocidas. Es un **piloto técnico** para validar el pipeline.
- El título indica ITS. La inspección de reads encontró ITS3 en R1 (`GCATCGATGAAGAACGCAGC`) e ITS4 en R2 (`TCCTCCGCTTATTGATATGC`), consistente con un amplicón ITS2. Falta recuperar el protocolo/paper de autores para una confirmación documental independiente de primers y condiciones de PCR.
- Se generaron candidatas de **revisión** en el piloto; `docs/RESULTS_SRR38913145.md` documenta por qué no son especies nuevas confirmadas.
