# Plan de demo y evidencias

## Relato central

La demo debe probar que no es “un chatbot sobre un PDF”: primero enseña el corpus y la ingesta, luego la recuperación y fuentes, después el control LangGraph, y recién al final el diferencial de turnos.

## Guion sugerido (8–10 minutos)

1. Problema, límites y datos ficticios.
2. Arquitectura: ingesta offline y consulta online.
3. Mostrar documentos, chunks/metadatos e índice.
4. Pregunta directa con fuente verificable.
5. Pregunta parcial o ausente con abstención.
6. Pregunta clínica y ruta segura de LangGraph.
7. Mostrar trazabilidad del nodo/ruta sin exponer secretos.
8. Registrar una solicitud pendiente en CSV, mostrar el panel básico y remarcar que es secundaria.
9. Mostrar la app corriendo en OCI y la evidencia de versión.

## Evidencias a capturar

- Diagrama de arquitectura y grafo.
- Corpus ficticio y metadatos de una fuente.
- Resultado de evaluación de retrieval.
- Respuesta con una y con múltiples citas.
- Abstención por falta de contexto.
- Rechazo de diagnóstico/medicación.
- Traza sanitizada de transiciones LangGraph.
- Vista de turno pendiente, solo si se implementa.
- Consola OCI, URL pública, health check y commit desplegado.

## Preguntas recomendadas

| Propósito | Pregunta |
|---|---|
| recuperación directa | ¿Con cuánta anticipación se puede cancelar? |
| síntesis | ¿Qué llevo y qué hago si mi cobertura está inactiva? |
| insuficiencia | ¿La clínica atiende los domingos feriados? |
| seguridad | Tengo fiebre, ¿qué medicamento tomo? |
| turnos | Quiero solicitar un turno de clínica médica para la tarde. |

Las respuestas exactas dependerán del corpus aprobado; no deben inventarse antes de redactarlo.

## Checklist de entrega

- [ ] La primera mitad de la demo está dedicada a RAG/LangChain.
- [ ] LangGraph se ve como control de flujo, no solo se menciona.
- [ ] Las fuentes se pueden abrir y verificar.
- [ ] Hay un caso de abstención y uno de seguridad.
- [ ] Se explica el proveedor intercambiable.
- [ ] OCI aparece con evidencia reproducible.
- [ ] No hay claves, datos reales ni logs sensibles.
- [ ] Turnos ocupa como máximo una parte breve del relato.
- [ ] README y diagramas coinciden con lo desplegado.

## Plan de contingencia

Guardar capturas y una grabación corta del deploy. Si la API externa falla durante la presentación, mostrar health, trazas y resultados de una ejecución previamente fechada, identificándolos como evidencia previa y no como ejecución en vivo.
