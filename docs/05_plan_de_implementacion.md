# Plan de implementación

Este documento planifica; no autoriza código. Cada fase tiene una puerta de salida verificable.

## Fase -1 — Definiciones y corpus

- Nombre confirmado: Medinova AI Agent para Clínica Medinova.
- Audiencia mixta, corpus PDF y solicitud pendiente con panel básico confirmados.
- Gemini, Streamlit, Chroma local, PDF y CSV confirmados. OCI queda como aprendizaje guiado antes de fijar la modalidad.
- Crear después el corpus ficticio y su set de preguntas.

**Salida:** decisiones críticas aceptadas y corpus revisado. Completada el 30/06/2026 con cinco PDF ficticios versión 2.0, cinco páginas cada uno, en `source_documents/`.

## Fase 0 — Diseño (actual)

- Completar los once documentos de `docs/`.
- Diagramar arquitectura, ingesta, consulta, grafo y despliegue.
- Registrar supuestos, riesgos y criterios de éxito.

**Salida:** documentación coherente, sin código funcional.

## Fase 1 — Base reproducible

- Estructura, entorno, dependencias fijadas y configuración segura.
- Contratos de estado, documentos, citas y proveedores.
- `.env.example` sin valores; `.env` local excluido del repositorio.
- Pruebas mínimas de configuración.

**Salida:** aplicación vacía instalable y comprobable.

## Fase 2 — Ingesta y retrieval LangChain

- Loaders aprobados, normalización, chunks y metadatos.
- Embeddings e índice versionado.
- Evaluación de retrieval con preguntas y fuentes esperadas.

**Salida:** recuperación medible antes de agregar generación.

## Fase 3 — RAG fundamentado

- Prompt, generación, citas e insuficiencia.
- Proveedor intercambiable.
- Evaluación de fidelidad y regresión.

**Salida:** respuestas reproducibles con evidencia.

## Fase 4 — LangGraph y seguridad

- Estado tipado, nodos y rutas.
- Guardrail de preguntas clínicas y fallos controlados.
- Trazas de ruta y pruebas por transición.

**Salida:** cada intención termina en la ruta esperada.

## Fase 5 — Interfaz y turnos secundarios

- Interfaz simple centrada en mostrar fuentes.
- Solicitud pendiente en CSV y vista administrativa mínima.
- Dejar previsto un control de carga de PDF para una actualización futura, sin habilitar todavía reindexación dinámica.

**Salida:** demo clara sin convertir el proyecto en agenda médica.

## Fase 6 — Calidad y seguridad

- Unitarias, integración, RAG, grafo, abuso y rendimiento.
- Revisión de secretos, logs y datos ficticios.

**Salida:** matriz de pruebas ejecutada y evidencia guardada.

## Fase 7 — OCI

- Infraestructura elegida, despliegue, health check, logs y reinicio.
- Gemini API key almacenada en OCI Vault y acceso mediante identidad de instancia con mínimo privilegio.
- Evidencia pública o capturas reproducibles.

**Salida:** aplicación accesible y guía validada.

## Fase 8 — Entrega

- README final, arquitectura real, resultados de evaluación y demo.
- Registrar diferencias entre diseño y solución final.

**Salida:** repositorio evaluable por un tercero.
