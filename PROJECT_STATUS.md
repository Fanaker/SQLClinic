# Estado — SQL Clinic v1.0.0

- Incluido: base sintética reproducible, cuatro escenarios de tuning, métricas de ejecución medidas, planes SQLite antes/después, UI de cinco vistas, scripts PostgreSQL y Docker opcionales.
- Verificado: `python -m pytest -q` (4 pruebas), chequeo JS, 5 capturas renderizadas sin errores de JavaScript, benchmarking sobre 50.000 pedidos y 99.766 ítems.
- Capturas: frontend renderizado en Chromium con las respuestas verificadas de la API (navegación directa a localhost bloqueada por el sandbox de captura).
- No verificado: ejecución real de PostgreSQL y Docker; no se afirma que las métricas SQLite se reproduzcan allí.
- Limitación: benchmarking simple, no sustituto de un estudio de rendimiento estadístico formal.
