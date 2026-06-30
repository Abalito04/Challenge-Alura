# Backlog de tareas

## Convenciones

- P0 bloquea el corazón técnico; P1 es necesaria para el MVP; P2 es diferencial.
- Las dependencias se expresan por identificador.

## Terminado

- [x] DOC-01 (P0): leer documento rector completo.
- [x] DOC-02 (P0): crear planificación y diagramas iniciales en `docs/`.

## Decisiones resueltas

- [x] DEC-01 (P0): Medinova AI Agent, Clínica Medinova y audiencia mixta.
- [x] DEC-02 (P0): documentos fuente PDF.
- [x] DEC-03 (P0): proveedor Gemini.
- [x] DEC-05 (P1): solicitud pendiente + panel básico en CSV.
- [x] DEC-04 (P0): Streamlit y Chroma local persistente.
- [x] DEC-06 (P0): `gemini-3.5-flash` principal, 2.5 fallback y `gemini-embedding-001`.
- [x] SRC-01 (P0): cinco documentos PDF ficticios versión 2.0, 25 páginas totales, renderizados y revisados.

## Bloqueado por decisión o aprendizaje

- [ ] DEC-07 (P1): aprender fundamentos de OCI y luego elegir modalidad de despliegue.
- [ ] DEC-08 (P1): definir cuándo habilitar la carga/reindexación de PDF desde la interfaz.

## Pendiente — núcleo técnico

- [ ] EVAL-01 (P0, depende SRC-01): convertir la matriz inicial en dataset ejecutable.
- [ ] SET-01 (P0, depende DEC-03/04): estructura y configuración reproducible.
- [ ] ING-01 (P0, depende SET-01/SRC-01): loaders y normalización.
- [ ] ING-02 (P0, depende ING-01): chunking con metadatos y versionado.
- [ ] RET-01 (P0, depende ING-02): embeddings, índice y retriever.
- [ ] RET-02 (P0, depende RET-01/EVAL-01): medir recall/precision de recuperación.
- [ ] RAG-01 (P0, depende RET-02): generación restringida y citas.
- [ ] RAG-02 (P0, depende RAG-01): suficiencia y respuesta parcial/sin contexto.
- [ ] GRF-01 (P0, depende RAG-01): estado y nodos LangGraph.
- [ ] SAFE-01 (P0, depende GRF-01/EVAL-01): rutas clínicas seguras.
- [ ] TEST-01 (P0, depende RAG-02/SAFE-01): regresión RAG y grafo.

## Pendiente — producto y despliegue

- [ ] UI-01 (P1, depende DEC-04/RAG-02): consulta y visualización de fuentes.
- [ ] APPT-01 (P2, depende SET-01): solicitud de turno aislada con CSV.
- [ ] APPT-02 (P2, depende APPT-01): vista administrativa mínima.
- [ ] OCI-01 (P1, depende DEC-04/TEST-01): preparar despliegue.
- [ ] OCI-02 (P1, depende OCI-01): desplegar, verificar y capturar evidencia.
- [ ] DEMO-01 (P1, depende OCI-02): ejecutar guion final.
- [ ] DOC-03 (P1, depende DEMO-01): README y resultados finales.

## Fuera del MVP

- [ ] Calendario y confirmación automática de turnos.
- [ ] Historias clínicas, diagnóstico o tratamientos.
- [ ] Login real e integraciones con WhatsApp, obras sociales o calendarios.
- [ ] Datos reales de pacientes.
