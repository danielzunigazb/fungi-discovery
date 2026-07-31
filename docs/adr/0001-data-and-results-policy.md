# ADR 0001: datos grandes fuera de Git; manifiestos dentro de Git

- **Fecha:** 2026-07-31
- **Estado:** aceptada

## Contexto

FASTQ, referencias UNITE, bases BLAST, outputs y logs pueden ocupar desde MB a TB. Versionarlos directamente en Git hace clones lentos, rompe límites de hosting y no garantiza procedencia científica.

## Decisión

- `data/`, `results/`, `logs/` y `tools/` se ignoran en Git.
- `metadata/` conserva JSON/manifiestos pequeños con fuente, licencia, fecha, parámetros, tamaño y checksums.
- Las corridas se describen mediante scripts bajo `scripts/` y documentos de resultados bajo `docs/`.
- Los archivos grandes se recuperan desde fuentes públicas o almacenamiento externo con checksum.

## Consecuencias

- El repositorio es pequeño y clonable.
- Una reproducción completa requiere ejecutar setup y descargar datos explícitamente.
- Se debe actualizar manifiesto/documentación cada vez que cambia una entrada o referencia.
