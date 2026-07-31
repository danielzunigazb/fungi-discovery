# Pipeline y criterios de decisión

## Objetivo

Priorizar **candidatas de diversidad fúngica no resuelta** a partir de amplicones ITS ambientales públicos. El resultado es una lista de secuencias para validar; **no demuestra una especie nueva ni autoriza nombrarla**.

## Por qué ITS y no genomas completos

ITS (Internal Transcribed Spacer) es el marcador de ADN de uso más frecuente para identificar hongos. En datos ambientales permite detectar miles de variantes por muestra con mucho menos costo y almacenamiento que genomas completos.

Una señal ITS divergente necesita confirmación con datos independientes. Los límites de identidad no son universales: varían entre linajes y dependen de la región secuenciada, el alineamiento y la base de referencia.

## Flujo completo

```text
Muestra ambiental o FASTQ público
  └─ 1. Registrar procedencia, licencia, checksum y metadatos
      └─ 2. Inspeccionar calidad y confirmar primers/diseño
          └─ 3. Recortar primers/adaptadores (Cutadapt)
              └─ 4. Filtrar calidad, unir pares y producir ASVs
                  └─ 5. Eliminar quimeras y contaminantes
                      └─ 6. Comparar con referencias curadas (UNITE + NCBI)
                          └─ 7. Priorizar candidatas y revisar alineamientos
                              └─ 8. Replicar / secuenciar otros loci / filogenia
                                  └─ 9. Taxonomía formal y voucher, si aplica
```

## Estado de cada etapa para el piloto colombiano

| Etapa | Estado | Evidencia |
|---|---|---|
| Registro de procedencia | Hecha | `metadata/SRR38913145.json`, `docs/DATA_PROVENANCE.md` |
| Descarga de reads | Hecha | `data/raw/SRR38913145/` |
| Verificación de integridad | Hecha | MD5 coinciden con ENA; ver bitácora |
| Perfil básico de reads | Hecho | 121.873 pares de 301 bp; mediana Phred 38 |
| Confirmar todos los primers | Pendiente | R2 comienza con ITS4; falta fuente que confirme el forward y el protocolo |
| Recorte de primers | Bloqueado correctamente | No correr sin confirmar primer forward |
| ASVs / denoising | Pendiente | Requiere etapa anterior |
| Quimeras | Pendiente | Requiere ASVs |
| Taxonomía / candidatas | Pendiente | No afirmar resultados antes de controles |

## Herramientas y responsabilidad

| Herramienta | Paso | Qué hace | Qué no garantiza |
|---|---|---|---|
| Cutadapt | 3 | Encuentra y recorta primers/adaptadores | No corrige errores de secuenciación ni identifica especies |
| DADA2 / QIIME 2 | 4 | Filtra, modela errores y produce ASVs | No elimina toda contaminación ni confirma taxonomía |
| VSEARCH | 4–5 | Une pares, desreplica y detecta quimeras | Sus umbrales deben justificarse; una quimera puede escapar |
| BLAST+ | 6 | Busca alineamientos frente a una referencia | El mejor hit no es automáticamente una identificación |
| UNITE | 6 | Referencia ITS curada / species hypotheses | También tiene cobertura incompleta y versiones cambiantes |
| CLI `fungi-discovery` | 6–7 | Controla FASTA y crea reporte de prioridad | Es triage exploratorio, no clasificación final |

## Lógica de `fungi-discovery screen`

Entrada: FASTA de ASVs o consensos, **no FASTQ crudo**.

1. Descarta secuencias <150 bp, con >5% `N` o caracteres ADN no válidos.
2. Ejecuta `blastn` contra una referencia local.
3. Conserva el mejor hit por query.
4. Calcula:
   - **Identidad:** `pident` de BLAST.
   - **Cobertura query:** tramo de la query cubierto por el hit (`abs(qend - qstart) + 1`) dividido por longitud de la query × 100. Se usa el tramo query y no `length` de BLAST, porque este último puede incluir huecos.
5. Clasifica de forma exploratoria:

| Condición | Etiqueta | Acción |
|---|---|---|
| Cobertura <80% | `ALINEAMIENTO_PARCIAL` | No concluir; revisar región/alineamiento |
| Identidad >=97% y cobertura >=80% | `COINCIDENCIA_CONOCIDA` | Baja prioridad para novedad |
| Identidad 90–<97% y cobertura >=80% | `CANDIDATA_DIVERGENTE` | Revisar con UNITE + controles |
| Identidad <90% y cobertura >=80% | `CANDIDATA_MUY_DIVERGENTE` | Alta prioridad técnica; descartar artefactos primero |
| Sin hit | `SIN_MATCH_CERCANO` | Revisar contra referencias completas y ADN no fúngico |

Los cortes 97%, 90% y 80% son filtros de ordenamiento, no definición de especie.

## Validación mínima antes de comunicar una candidata

1. Está presente en réplicas biológicas/técnicas y ausente en controles negativos.
2. La secuencia tiene calidad suficiente, sin quimerismo y con primers eliminados.
3. ITS completo/parcial se comparó contra una versión documentada de UNITE y NCBI.
4. El alineamiento y cobertura fueron inspeccionados, no solo un porcentaje.
5. Se evaluó contaminación, asignación no fúngica y artefactos de PCR.
6. Se confirmó con nueva extracción/secuenciación o muestra independiente.
7. Si se pretende describir formalmente: filogenia multilocus apropiada para el clado, metadatos, colaborador experto y espécimen voucher.

## Reproducibilidad

Cada ejecución que cambie datos debe registrar en `docs/WORKLOG.md`:

- Fecha/hora UTC.
- Comando exacto y versiones.
- Archivo de entrada, checksum y número de reads/secuencias.
- Parámetros y razón de cada umbral.
- Archivo de salida, checksum y conteos.
- Errores o decisiones de exclusión.
