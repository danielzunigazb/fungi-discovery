# ADR 0002: las etiquetas del software son triage, no designaciones taxonómicas

- **Fecha:** 2026-07-31
- **Estado:** aceptada

## Contexto

Una secuencia ITS distante de una referencia puede ser una especie no documentada, pero también un artefacto de PCR, error de lectura, quimera, contaminación, región parcial, taxonomía desactualizada o variación intraespecífica.

## Decisión

Las salidas `CANDIDATA_DIVERGENTE`, `CANDIDATA_MUY_DIVERGENTE` y prioridades derivadas se describen siempre como **candidatas de revisión**. Ninguna documentación, CLI ni reporte las llama “especie nueva”.

Una afirmación taxonómica formal queda fuera del alcance de este software y requiere controles, replicación, alineamientos inspeccionados, referencia curada, evidencia adicional/filogenia y requisitos de nomenclatura aplicables.

## Consecuencias

- El código usa un lenguaje científicamente conservador.
- Las pruebas validan clasificación mecánica, no una verdad biológica.
- Resultados con baja abundancia o sin réplicas se priorizan para validación, no para comunicación pública como descubrimientos.
