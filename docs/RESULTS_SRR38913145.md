# Resultados del piloto SRR38913145

**Estado:** análisis exploratorio reproducible. Este documento no comunica especies nuevas.

## Pregunta del piloto

¿Puede el pipeline procesar ITS2 público de una muestra colombiana, documentar la procedencia y priorizar secuencias divergentes frente a una base ITS curada?

La respuesta técnica es sí. La respuesta biológica sobre especies nuevas es **todavía no**: el estudio contiene una sola muestra, no se han analizado controles ni réplicas, y la detección de diversidad se hizo con variantes exactas, no con ASVs denoised por DADA2.

## Datos

- **Run:** `SRR38913145`.
- **Muestra:** mucílago de café fermentado (código 605), Miraflores, provincia de Lengupá, Boyacá, Colombia; 2025.
- **Marcador:** ITS2, inferido por los primers observados ITS3/ITS4.
- **Plataforma:** Illumina MiSeq, paired-end 2×301 bp.
- **Procedencia, enlaces y MD5 de entrada:** [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md).

## Flujo ejecutado y retención

| Etapa | Parámetros principales | Resultado | Retención respecto a pares iniciales |
|---|---|---:|---:|
| Entrada pública verificada | MD5 contra ENA | 121.873 pares | 100% |
| Recorte / filtro con Cutadapt 5.2 | ITS3 R1, ITS4 R2; `-q 20,20`; sin `N`; mínimo 100 bp; exigir ambos primers | 120.066 pares | 98,5% |
| Unión con VSEARCH 2.31.0 | solapamiento mínimo 20 bp; máx. 5 diferencias; EE máximo 1 | 95.034 reads unidos | 78,0% |
| Pares no unidos, conservados | — | 25.032 pares | 20,5% |
| Variantes exactas desreplicadas | Igualdad de secuencia; no DADA2 | 7.363 variantes | — |
| Variantes de abundancia >=2 | Exclusión de singletons para el primer triage | 2.260 variantes / 89.931 reads | — |
| Filtro quimera *de novo* UCHIME3 | VSEARCH | 2.073 no quiméricas / 86.962 reads | 71,4% |

Los números de unión no suman exactamente 100% de la retención anterior porque se expresan contra distintos denominadores y porque las etapas de tamaño/abundancia no son pares de lectura.

## Pares no ensamblados: limitación explícita

VSEARCH etiquetó 24.012 de los 25.032 no ensamblados como `staggered`: el amplicón probablemente es más largo que la longitud útil de las lecturas. No son basura y no se borraron:

```text
data/merged/SRR38913145/SRR38913145.not_merged_R1.fastq
data/merged/SRR38913145/SRR38913145.not_merged_R2.fastq
```

Para no introducir un sesgo silencioso, el ranking actual solo cubre los 95.034 reads que sí formaron un consenso pareado. El análisis futuro debe procesar los no ensamblados como lecturas single-end orientadas o volver a los FASTQ con DADA2/ITSxpress según el protocolo del estudio.

## Referencia taxonómica usada

- **Base:** UNITE v10.0, release 19-02-2025.
- **Subconjunto:** Fungi, delimitación dinámica, sin singletons, archivos `developer` seleccionados por la receta oficial RESCRIPt/QIIME.
- **Secuencias:** 102.137 ITS; cada una tiene una anotación taxonómica correspondiente (0 IDs inconsistentes).
- **Licencia reportada por la API oficial de PlutoF para esta release:** CC BY 4.0.
- **Archivo fuente:** `sh_qiime_release_19.02.2025.tgz`.
- **SHA-256 del archivo fuente:** `9a4c185308790f3667f50198659969525f95860d08aaf156ec5f5d309b2723ea`.
- **SHA-256 FASTA extraído:** `834b9af8d9c07e69a2ce826954fdb7320eea6b28dd0213f3990cb76e644e0aff`.
- **SHA-256 taxonomía extraída:** `ff3094c66da87eedc442e7cc3f84517d4c4d4e0524318d579386f629048433fa`.

Consulta `DATA_PROVENANCE.md` para URLs y la cadena de extracción.

## Resultados del primer pase: MegaBLAST contra UNITE

MegaBLAST se eligió como primer pase rápido para coincidencias cercanas. Criterios del reporte:

- cobertura de query >=80%;
- conocida: identidad >=97%;
- divergente: 90–<97%;
- muy divergente: <90%;
- los cortes son triage, **no** límites universales de especie.

| Clasificación | Variantes exactas | Reads | Interpretación correcta |
|---|---:|---:|---|
| `COINCIDENCIA_CONOCIDA` | 1.375 | 65.854 | Coincidencia cercana con UNITE bajo este criterio |
| `CANDIDATA_DIVERGENTE` | 130 | 986 | Señal para revisión; no confirmación de especie |
| `CANDIDATA_MUY_DIVERGENTE` | 8 | 33 | Señal de prioridad técnica, primero descartar error/artefacto |
| `ALINEAMIENTO_PARCIAL` | 38 | 207 | No interpretar como novedad |
| `SIN_MATCH_CERCANO` | 522 | 19.882 | Sin coincidencia rápida; se sometieron a segunda pasada |

## Segunda pasada: `dc-megablast` de las 522 sin match rápido

La segunda búsqueda, más sensible, recuperó hits parciales para todas las 522 secuencias, pero **ninguna** logró >=80% de cobertura. Resultado: 522 `ALINEAMIENTO_PARCIAL` (19.882 reads).

Conclusión: no son candidatas de especie basadas en este análisis. Algunas podrían ser secuencias no fúngicas, regiones distintas, productos de PCR o linajes insuficientemente cubiertos. Requieren revisión metodológica, no una afirmación de novedad.

## Lista conservadora de revisión

Archivo: `results/SRR38913145_unite_v10_candidates_abundance_ge5.tsv`.

- 37 variantes candidatas con >=5 reads.
- 33: `REVISION` (90–<97% de identidad, cobertura >=80%).
- 4: `ALTA_REVISION` (<90%, cobertura 100%).

Las cuatro de alta revisión tienen longitud 281 bp, abundancias de 5–7 reads y mejor match con la hipótesis UNITE `SH1245244.10FU`, anotada como *Candida margitis*:

| Query | Reads | Identidad | Cobertura | Acción correcta |
|---|---:|---:|---:|---|
| `SRR38913145_unique_547` | 7 | 87,59% | 100% | Inspeccionar alineamiento y secuencias originales |
| `SRR38913145_unique_577` | 7 | 89,36% | 100% | Igual; buscar en replicados/controles |
| `SRR38913145_unique_744` | 5 | 87,54% | 100% | Igual; baja abundancia exige cautela |
| `SRR38913145_unique_806` | 5 | 89,32% | 100% | Igual; baja abundancia exige cautela |

Estas cuatro son **candidatas de revisión**, no “cuatro especies nuevas”: provienen de una sola muestra, su abundancia es baja, no hay controles y variantes similares pueden ser errores residuales o microvariación intraespecífica.

## Archivos de salida principales

| Archivo | Contenido |
|---|---|
| `results/SRR38913145_unite_v10_megablast_report.tsv` | Ranking base contra UNITE |
| `results/SRR38913145_unite_v10_annotated.tsv` | Ranking con abundancia y taxonomía UNITE |
| `results/SRR38913145_unite_v10_candidates_abundance_ge5.tsv` | 37 candidatas conservadoras de revisión |
| `results/SRR38913145_unite_v10_dc_megablast_nohits_report.tsv` | Segunda pasada de los no-hits rápidos |
| `logs/2026-07-31_*.log` | Salidas completas de los comandos ejecutados |

## Siguiente validación necesaria

1. Ejecutar denoising con **DADA2** sobre los FASTQ originales, incorporando perfiles de error y controles.
2. Procesar la fracción no ensamblada sin perder amplicones largos.
3. Obtener las demás muestras del mismo estudio y evaluar si las señales se replican.
4. Verificar contaminantes y controles negativos del estudio.
5. Para candidatas replicadas: revisar alineamientos, consultar NCBI/UNITE actualizado y usar loci adicionales o nueva secuenciación.
6. Solo con soporte independiente, metadatos, filogenia y una muestra/voucher se evalúa una descripción taxonómica formal.
