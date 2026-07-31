# Setup reproducible

Esta guía permite reconstruir el entorno del proyecto desde una máquina Linux x86_64. No contiene correos, API keys ni otros secretos.

## Requisitos

| Requisito | Uso |
|---|---|
| Linux x86_64 | Binarios locales de BLAST+ y VSEARCH |
| `curl`, `tar`, `gzip` | Descargar y descomprimir herramientas/datos |
| [uv](https://docs.astral.sh/uv/) | Entorno y paquetes Python |
| Python >= 3.14 | Declarado en `pyproject.toml` |
| ~2 GB libres para el piloto | Herramientas, referencia y FASTQ; más para estudios grandes |

## 1. Clonar/preparar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO> fungi-discovery
cd fungi-discovery
uv sync --extra dev --extra preprocess
mkdir -p data/reference data/raw data/queries results metadata tools
```

`uv sync` instala las dependencias bloqueadas en `uv.lock`. No uses el Python global para ejecutar el pipeline: usa `uv run ...`. Para comprobar la instalación ejecuta `make check` y `uv run fungi-discovery --help`.

## 2. Instalar BLAST+ localmente

BLAST+ construye la base de referencia y compara secuencias contra ella.

```bash
mkdir -p tools && cd tools
curl --fail --location --retry 3 -o blast.tar.gz \
  'https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.17.0+-x64-linux.tar.gz'
tar xzf blast.tar.gz
rm blast.tar.gz
ln -sfn ncbi-blast-2.17.0+ blast
./blast/bin/blastn -version
cd ..
```

Versión usada en el piloto: **BLAST+ 2.17.0+**.

## 3. Instalar VSEARCH localmente

VSEARCH será usado para desreplicación y detección de quimeras. No se ejecutó aún sobre el piloto: antes debe verificarse el primer forward en los metadatos del estudio.

```bash
mkdir -p tools && cd tools
curl --fail --location --retry 3 -o vsearch.tar.gz \
  'https://github.com/torognes/vsearch/releases/download/v2.31.0/vsearch-2.31.0-linux-x86_64.tar.gz'
tar xzf vsearch.tar.gz
rm vsearch.tar.gz
ln -sfn vsearch-2.31.0-linux-x86_64 vsearch
./vsearch/bin/vsearch --version
cd ..
```

Versión usada: **VSEARCH 2.31.0**.

## 4. Configurar contacto NCBI sin guardarlo en el repositorio

NCBI requiere un correo de contacto para E-utilities. Define una variable solo en tu terminal:

```bash
export NCBI_EMAIL='tu_correo@dominio.com'
```

No escribas esa variable en `README.md`, scripts, `metadata/`, Git ni capturas públicas. Una API key de NCBI es opcional y también debe permanecer fuera del repositorio:

```bash
export NCBI_API_KEY='...'
```

## 5. Crear una referencia ITS piloto

```bash
uv run fungi-discovery fetch-reference \
  --email "$NCBI_EMAIL" \
  --max-records 1000

uv run fungi-discovery make-db \
  --fasta data/reference/ncbi_fungi_its.fasta
```

Para análisis real, sustituye la referencia piloto por una descarga versionada de UNITE y registra versión, fecha, URL, checksum y criterios de filtrado en `metadata/`.

## Recuperar el piloto reproducible

Los datos grandes no se suben a Git. Los scripts siguientes descargan solo fuentes públicas, verifican checksums y reconstruyen entradas/referencia:

```bash
bash scripts/fetch_srr38913145_inputs.sh
bash scripts/fetch_unite_v10_reference.sh
bash scripts/run_srr38913145_pilot.sh
```

Lee `docs/RESULTS_SRR38913145.md` antes de interpretar cualquier salida.

## Verificación del entorno

```bash
make check
uv run fungi-discovery --help
./tools/blast/bin/blastn -version
./tools/vsearch/bin/vsearch --version
uv run cutadapt --version
```

## Versiones del primer piloto

| Componente | Versión |
|---|---|
| Sistema | Arch Linux, kernel 7.0.10-arch1-1, x86_64 |
| Python | 3.14.x (la versión exacta instalada se comprueba con `uv run python --version`) |
| Biopython | 1.87 |
| Cutadapt | 5.2 |
| BLAST+ | 2.17.0+ |
| VSEARCH | 2.31.0 |

Las versiones Python exactas están bloqueadas en `uv.lock`.
