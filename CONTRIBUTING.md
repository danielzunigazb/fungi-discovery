# Contribuir

Gracias por contribuir. Este proyecto combina software y evidencia biológica: un cambio que pasa tests aún puede ser científicamente incorrecto si pierde trazabilidad.

## Setup

```bash
uv sync --extra dev --extra preprocess
make check
```

Para BLAST+ y VSEARCH, sigue [`docs/SETUP.md`](docs/SETUP.md). Los tests no requieren esos binarios, red ni los datasets grandes.

## Flujo de trabajo

1. Crea una rama descriptiva: `feat/unite-manifest`, `fix/query-coverage`.
2. Mantén un cambio pequeño y reproducible.
3. Añade/actualiza tests.
4. Ejecuta antes de abrir PR:

   ```bash
   make format
   make check
   make build
   ```

5. Explica en el PR: objetivo, datos afectados, parámetros modificados, riesgo científico y evidencia de validación.

## Reglas de código

- Python >=3.14, `src/` layout, tipado en funciones públicas.
- Formato y linter: Ruff. No introduzcas `# noqa` sin explicación.
- No accedas a internet desde tests.
- No ejecutes BLAST, Cutadapt o VSEARCH reales en CI unitario; móckealos.
- No reduzcas cobertura para ocultar huecos: añade pruebas.
- No incluyas secretos, correos personales, tokens o API keys.

## Reglas de datos y resultados

- No subas `data/`, `results/`, `logs/` ni `tools/` al repositorio; son pesados o regenerables.
- Añade un manifiesto pequeño bajo `metadata/` para cada dataset: URL/DOI, licencia, fecha, checksum, criterio de selección y versión.
- Documenta cambios de referencia, primers, umbrales o filtros en `docs/WORKLOG.md`.
- Una etiqueta `CANDIDATA_*` no se puede cambiar en documentos a “especie nueva”. Usa “candidata de revisión” hasta completar validación independiente.

## Reportar errores científicos o de software

Abre un issue con:

- versión/commit y sistema operativo;
- comando reproducible;
- input mínimo sintético, sin datos sensibles;
- resultado esperado y obtenido;
- si afecta inferencia biológica, el posible sesgo y la referencia involucrada.
