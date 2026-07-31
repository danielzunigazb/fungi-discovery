# Arquitectura del repositorio

## Principios

1. **Código y datos se separan.** El repositorio contiene código, tests, documentación y manifiestos pequeños; FASTQ, referencias, índices BLAST, logs y resultados se regeneran y están ignorados por Git.
2. **Cada conclusión tiene trazabilidad.** Un resultado debe enlazar a datos de entrada, versión de referencia, checksums, parámetros, software y comando.
3. **Triage no es taxonomía formal.** La CLI prioriza secuencias para revisión; no nombra especies.
4. **Tests sin red ni archivos pesados.** CI ejecuta fixtures sintéticas y mocks de BLAST/NCBI. Las descargas y análisis completos se ejecutan localmente o en infraestructura científica.

## Estructura

```text
src/fungi_discovery/       Paquete Python instalable
  core.py                  FASTA, hits BLAST, cobertura, clasificación y TSV
  annotation.py            Unión de abundancia + taxonomía UNITE
  cli.py                   CLI y llamadas a NCBI / BLAST+
tests/                     Suite determinista sin red
scripts/                   Descarga verificada y orquestación de corridas concretas
docs/                      Método, ADRs, setup, procedencia y resultados
metadata/                  Manifiestos JSON pequeños de procedencia
data/                      Ignorado: inputs, referencias, índices y artefactos
results/                   Ignorado: reportes generados
logs/                      Ignorado: stdout/stderr de herramientas externas
tools/                     Ignorado: binarios locales BLAST+/VSEARCH
.github/workflows/         CI
```

## Interfaces estables

### CLI

```bash
uv run fungi-discovery fetch-reference ...
uv run fungi-discovery make-db ...
uv run fungi-discovery screen ...
uv run fungi-discovery annotate ...
```

La salida de `screen` es TSV con columnas definidas por `REPORT_FIELDS` en `core.py`. Cambiar o quitar una columna es un cambio de compatibilidad y debe documentarse en un ADR o nota de versión.

### Dependencias externas

| Componente | Responsabilidad | Cómo se verifica |
|---|---|---|
| NCBI E-utilities | Descargar una referencia piloto | Tests mockean red; ejecución real guarda consulta/fecha |
| BLAST+ | Índices y alineamiento local | Tests mockean subproceso; pipeline real guarda logs |
| Cutadapt | Recorte de primers/calidad | Requerido solo para FASTQ, extra `preprocess` |
| VSEARCH | Unión, desreplicación y quimeras | Binario versionado localmente; logs por corrida |
| UNITE | Referencia ITS taxonómica | DOI, licencia, URL, release y SHA-256 en procedencia |

## Modelo de datos mínimo

- **Query:** secuencia ITS/ASV en FASTA.
- **Abundancia:** etiqueta VSEARCH `size=<N>;` preservada en el ID/description.
- **Hit:** mejor alineamiento por query según mayor bitscore entre hasta cinco resultados BLAST.
- **Cobertura:** span de query (`abs(qend-qstart)+1`) / longitud query. Nunca usar `alignment_length/query_length` porque inserciones pueden superar 100%.
- **Candidata:** etiqueta de prioridad reproducible, no una asignación de especie.

## Política de cambios

- Lógica pura: añadir test unitario primero o en el mismo cambio.
- CLI: añadir test de handler con herramientas externas mockeadas.
- Parámetros científicos: documentar motivo, impacto y fecha en `docs/WORKLOG.md` o ADR.
- Dataset/referencia: añadir manifiesto con fuente, licencia, fecha, tamaño y checksum antes de analizar.
