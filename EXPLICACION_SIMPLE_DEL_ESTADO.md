# Estado del proyecto, explicado simple

## Resumen

El proyecto ya funciona como un pequeño laboratorio computacional: toma ADN ambiental de hongos, elimina parte del ruido técnico, lo compara contra una referencia curada y produce una lista de **candidatas de revisión**.

No ha descubierto oficialmente una especie nueva. Eso requeriría validación experimental, controles, réplicas, filogenia y trabajo taxonómico.

```text
Idea y setup                           ✅
Datos públicos reales de Colombia      ✅
Verificación de integridad             ✅
Recorte de primers y calidad           ✅
Unión de pares                         ✅
Desreplicación y quimeras preliminar   ✅
Referencia curada UNITE                ✅
Ranking de candidatas                  ✅
Denoising estadístico (DADA2)          ⏳ siguiente mejora
Réplicas/controles                     ❌ pendiente
Confirmación de especies               ❌ pendiente
```

## Qué se procesó

Dataset público `SRR38913145`:

```text
Origen: mucílago de café fermentado
Lugar: Lengupá, Boyacá, Colombia
Año: 2025
Tecnología: Illumina MiSeq, 2 × 301 bp
Marcador: ITS2 (primers ITS3/ITS4 observados en reads)
```

Resultados técnicos principales:

```text
121.873 pares de reads originales
120.066 pares tras recorte/filtro (98,5%)
95.034 pares unidos
7.363 variantes exactas
2.260 variantes con >=2 reads
2.073 variantes no quiméricas preliminares
```

Los 25.032 pares no unidos se conservaron. La mayoría parecen amplicones largos (`staggered`), no basura; todavía necesitan una ruta de análisis separada.

## Qué encontró UNITE

Se compararon las 2.073 variantes no quiméricas contra **UNITE v10.0, 19-02-2025**, referencia ITS fúngica curada.

```text
1.375 coincidencias cercanas (>=97%)
130 candidatas divergentes (90–<97%)
8 candidatas muy divergentes (<90%)
38 alineamientos parciales
522 sin hit rápido; una segunda búsqueda sensible las dejó como parciales
```

Tras exigir al menos cinco reads, quedaron:

```text
37 candidatas para revisión
33 prioridad "revisión"
4 prioridad "alta revisión"
```

Esto **no significa 37 o 4 especies nuevas**. Son secuencias que sobrevivieron filtros iniciales y merecen comprobación. Las cuatro de prioridad alta aparecen solo 5–7 veces y no tienen réplicas ni controles, así que pueden ser variación rara, error residual o señal biológica real: aún no se sabe.

## La regla más importante

```text
“Raro en una base de datos” ≠ “especie nueva”
```

Una secuencia puede parecer rara por cobertura parcial, error de PCR, contaminación, quimera no detectada, ADN no fúngico, base incompleta o variación de una especie conocida.

## Qué sigue

1. Ejecutar DADA2 para modelar errores y generar ASVs de mayor confianza.
2. Analizar los pares no ensamblados sin perder amplicones ITS largos.
3. Descargar más muestras del mismo estudio y buscar señales repetidas.
4. Revisar controles negativos y contaminación.
5. Inspeccionar manualmente las candidatas que persistan contra UNITE/NCBI actualizados.
6. Si una señal se replica: obtener muestra independiente, otros loci y colaboración taxonómica.

## Dónde está la evidencia

- Resultado completo: [`docs/RESULTS_SRR38913145.md`](docs/RESULTS_SRR38913145.md)
- Fuentes y checksums: [`docs/DATA_PROVENANCE.md`](docs/DATA_PROVENANCE.md)
- Método: [`docs/PIPELINE.md`](docs/PIPELINE.md)
- Decisiones y comandos históricos: [`docs/WORKLOG.md`](docs/WORKLOG.md)
- Arquitectura y controles de calidad: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
