# Seguridad y manejo responsable

## Secretos

Nunca guardes en Git:

- API keys de NCBI, cloud o cualquier proveedor;
- correos personales usados por E-utilities;
- tokens, cookies, `.env` o credenciales de laboratorio;
- ubicaciones precisas sensibles de especies/colecciones sin autorización.

Usa variables locales:

```bash
export NCBI_EMAIL='tu_correo@dominio.com'
export NCBI_API_KEY='opcional-y-secreto'
```

Si expones una credencial, revócala y rota la clave antes de informar el incidente.

## Vulnerabilidades de software

No publiques credenciales ni muestras privadas en un issue. Para una vulnerabilidad que permita ejecución no autorizada, exfiltración o corrupción de resultados, contacta al mantenedor del repositorio de forma privada y adjunta pasos mínimos para reproducirla.

## Bioseguridad y ética

El software opera sobre secuencias; no sustituye permisos, bioseguridad, protocolos de muestreo ni evaluación experta. No recolectes, cultives, transportes ni liberes organismos desconocidos sin permisos y supervisión adecuados. Respeta licencias de datasets, consentimiento, áreas protegidas, conocimientos tradicionales y metadatos sensibles.

## Integridad científica

- No presentes resultados de `screen` como descubrimientos confirmados.
- Conserva inputs, checksums, versiones y parámetros.
- Declara límites, réplicas ausentes, controles ausentes y datos excluidos.
- Corrige públicamente un reporte si una referencia, algoritmo o error de pipeline cambia la interpretación.
