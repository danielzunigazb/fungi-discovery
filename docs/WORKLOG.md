# Bitácora de trabajo reproducible

Formato: fecha UTC aproximada, acción, comando/herramienta, resultado y decisión. No se registran secretos como correo, tokens o API keys.

## 2026-07-30 / 2026-07-31 — Inicialización

### Entorno Python

- **Acción:** crear proyecto `hongos-descubrimiento` con `uv` e instalar dependencias.
- **Dependencias:** Biopython 1.87, Requests 2.34.2; posteriormente Cutadapt 5.2.
- **Estado:** completado. El lockfile `uv.lock` fija las versiones exactas.

### BLAST+

- **Acción:** descargar e instalar BLAST+ local bajo `tools/blast`.
- **Versión:** `blastn 2.17.0+`, build 2025-07-01.
- **Incidente:** la primera descarga quedó truncada (246.595.584 de 296.006.458 bytes). Se reanudó con `curl --continue-at -`; la verificación de versión confirmó instalación válida.
- **Decisión:** no usar paquetes del sistema; binario local versionado por instrucciones de setup.

### Código inicial

- **Archivo histórico:** `fungi_discovery.py`; posteriormente migrado al paquete `src/fungi_discovery/` con CLI `fungi-discovery`.
- **Funciones:** descargar referencia desde NCBI (`fetch-reference`), construir DB BLAST (`make-db`) y filtrar/comparar ASVs FASTA (`screen`).
- **Prueba:** se creó una referencia sintética y una query idéntica de 240 bp; `screen` la clasificó `COINCIDENCIA_CONOCIDA`, identidad/cobertura 100%.
- **Corrección aplicada:** la descarga de NCBI ahora usa `esearch(usehistory="y")` y pasa `WebEnv`/`QueryKey` a `efetch`; evita reejecutar una consulta grande por lote.

## 2026-07-30 — Referencia ITS piloto

- **Acción:** ejecutar `fetch-reference` con la consulta por defecto de ITS fúngico, límite 1.000.
- **Resultado de NCBI:** 1.980.731 registros encontrados; 1.000 descargados.
- **Salida:** `data/reference/ncbi_fungi_its.fasta`.
- **Características:** 2,78 MiB; mínimo 186 bp, mediana 563 bp, máximo 9.954 bp.
- **Acción posterior:** `make-db --fasta data/reference/ncbi_fungi_its.fasta`.
- **Resultado:** DB BLAST `data/reference/ncbi_fungi_its.*`, 1.000 secuencias indexadas.
- **Decisión:** se etiqueta como referencia piloto, no como UNITE ni referencia curada definitiva.

## 2026-07-30 — Selección y descarga de dataset ambiental

- **Búsqueda SRA:** consulta `("fungal ITS"[All Fields]) AND Colombia[All Fields]`.
- **Resultado:** 775 registros al momento de la búsqueda.
- **Criterio de selección:** piloto ITS en Colombia, público, paired-end y pequeño para validar el flujo sin descargar GB.
- **Dataset elegido:** `SRR38913145`; estudio `SRP705069`, BioProject `PRJNA1472785`.
- **Muestra:** mucílago de café fermentado, Lengupá, Boyacá, Colombia, 2025; Illumina MiSeq ITS amplicon paired-end.
- **Descarga:** reads FASTQ desde ENA, R1 y R2.
- **Resultado:** ambos MD5 calculados localmente coincidieron con los MD5 publicados por ENA. Ver `docs/DATA_PROVENANCE.md`.

## 2026-07-30 — Inspección inicial de FASTQ

- **Lecturas:** 121.873 en R1 y 121.873 en R2; todas 301 bp.
- **Calidad media por read:** mediana Phred 38 en ambos; mínimos R1=19,1, R2=16,6.
- **Observación de primer:** R2 inicia con `TCCTCCGCTTATTGATATGC`, compatible con ITS4.
- **Decisión:** no recortar ni clasificar todavía. Falta confirmar mediante documentación del estudio el primer forward y el protocolo, para no alterar mal las lecturas.

## 2026-07-31 — Herramientas de preprocesamiento y documentación

- **Cutadapt:** instalado mediante `uv`, versión 5.2.
- **VSEARCH:** instalado localmente bajo `tools/vsearch`, versión 2.31.0.
- **Documentos añadidos:** `docs/SETUP.md`, `docs/PIPELINE.md`, `docs/DATA_PROVENANCE.md`, este archivo.
- **Estado científico actual:** no se han calculado ASVs, removido quimeras ni identificado candidatas. La única conclusión válida es que los archivos de entrada son públicos, íntegros y de calidad inicial alta.

## 2026-07-31 — Procesamiento ITS2 y ranking UNITE

### Confirmación operativa de primers

- **R1 observado:** `GCATCGATGAAGAACGCAGC`, secuencia de ITS3.
- **R2 observado:** `TCCTCCGCTTATTGATATGC`, secuencia de ITS4.
- **Interpretación:** amplicón ITS2. Se documenta como confirmación por inspección de reads; falta recuperar/publicar protocolo de los autores si se busca una reproducción metodológica completa.

### Recorte y filtrado (Cutadapt 5.2)

- **Comando:** ver `scripts/run_srr38913145_pilot.sh` y `logs/2026-07-31_cutadapt_SRR38913145.log`.
- **Parámetros:** exigir ITS3/ITS4, `-q 20,20`, sin bases `N`, longitud mínima 100 bp.
- **Resultado:** 120.066/121.873 pares escritos (98,5%).
- **Checksums de salida:** R1 `fbcb24212ae21508984db5b4d3e32244`; R2 `2d2bfc0e19c2eda6531bb9d535cce7c5`.

### Unión, desreplicación y quimeras

- **Unión VSEARCH:** 95.034/120.066 pares unidos (79,2%); longitud media 353,04 bp; EE medio de secuencia unida 0,06.
- **No unidos:** 25.032; 24.012 fueron `staggered`. Se conservaron, no se interpretan como reads malos y no entran al ranking actual.
- **Desreplicación exacta:** 7.363 variantes de 95.034 reads.
- **Filtro de abundancia inicial:** se conservaron >=2 reads: 2.260 variantes, 89.931 reads. Esto reduce falsos positivos de baja abundancia, pero puede excluir diversidad real rara; se declara como decisión de triage, no como verdad biológica.
- **UCHIME3 de novo:** 187/2.260 (8,3%) variantes fueron quiméricas; quedan 2.073 variantes no quiméricas y 86.962 reads.
- **Nota:** estas son variantes exactas no quiméricas, **no ASVs denoised por DADA2**.

### Corrección de cobertura BLAST

- **Error identificado:** el primer código calculaba cobertura como `length/qlen`; `length` de BLAST puede incluir huecos y dio coberturas >100%.
- **Corrección:** usar el span de query `abs(qend-qstart)+1` dividido por `qlen`. La lógica vive ahora en `src/fungi_discovery/core.py`; también se actualizó `docs/PIPELINE.md`.
- **Acción:** el reporte piloto NCBI se regeneró tras la corrección. No se usa para inferencia final.

### Referencia UNITE

- **Versión:** UNITE v10.0, 19-02-2025; Fungi; dinámica; sin singletons; archivos `developer` usados por RESCRIPt/QIIME.
- **Fuente:** API PlutoF oficial asociada a DOI `10.15156/BIO/3301241`; respuesta guardada en `metadata/unite_v10_dynamic_fungi_api_response.json`.
- **Archivo:** `sh_qiime_release_19.02.2025.tgz`; SHA-256 `9a4c185308790f3667f50198659969525f95860d08aaf156ec5f5d309b2723ea`.
- **Validación:** 102.137 FASTA IDs y 102.137 taxonomy IDs; 0 diferencias entre conjuntos.
- **Incidente documentado:** se descargó inicialmente un `.qza` de GitHub que era un clasificador entrenado de QIIME, no un FASTA. Se inspeccionó, se conservó como artefacto separado y **no** se usó como DB BLAST. La receta RESCRIPt indicó la fuente/archivo adecuados.

### Búsqueda contra UNITE

- **Intento inicial:** `blastn` sensible sobre las 2.073 queries contra 102.137 referencias superó el límite de 10 minutos y fue terminado sin reporte válido.
- **Decisión:** primer pase con `megablast` para hits cercanos; segundo pase `dc-megablast` únicamente sobre no-hits rápidos. Se añadió `--blast-task` al script, y se conservan hasta cinco hits antes de elegir el mayor bitscore.
- **MegaBLAST:** 1.375 coincidencias conocidas; 130 divergentes; 8 muy divergentes; 38 alineamientos parciales; 522 no-hits rápidos. Ver `docs/RESULTS_SRR38913145.md`.
- **Segunda pasada:** las 522 no-hits rápidos tuvieron solo alineamientos parciales con `dc-megablast`; no se etiquetan como candidatas de especie.
- **Listado conservador:** `results/SRR38913145_unite_v10_candidates_abundance_ge5.tsv`, 37 candidatas con >=5 reads: 33 revisión y 4 alta revisión. No se comunican como especies nuevas.

## 2026-07-31 — Serialización del proyecto como repositorio

- **Migración de código:** los scripts históricos se reemplazaron por el paquete instalable `src/fungi_discovery/` y la CLI `fungi-discovery` (`fetch-reference`, `make-db`, `screen`, `annotate`).
- **Calidad:** se añadieron Ruff, Ty, Pytest, cobertura mínima 85%, `Makefile`, build wheel/sdist y CI en GitHub Actions.
- **Pruebas:** 28 tests deterministas sin red, BLAST real ni datasets pesados; cubren FASTA, cobertura BLAST, clasificación, taxonomía, prioridades y handlers CLI mockeados.
- **Resultado de gate local:** `make check` pasó: lint y tipos limpios; 28 tests; cobertura 89,67%; `uv build` pasó.
- **Integración:** el subcomando `fungi-discovery annotate` recreó exactamente los dos TSV históricos del piloto (SHA-256 idénticos).
- **Reproducibilidad:** scripts añadidos para descargar/verificar FASTQ del piloto y UNITE v10 por checksums, más script de orquestación del piloto.
- **Gobernanza:** añadidos README, arquitectura, contribución, seguridad, licencia MIT, cita CFF, plantillas de issues, Dependabot y ADRs. Los datos/resultados/binarios continúan fuera de Git, con manifiestos de procedencia dentro de Git.

## Próxima acción científica recomendada

Ejecutar DADA2 sobre reads originales, recuperar controles/réplicas y procesar explícitamente los 25.032 pares no ensamblados. Solo las señales que persistan en esas validaciones deben pasar a revisión filogenética y a muestras independientes.
