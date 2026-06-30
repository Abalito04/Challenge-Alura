# Riesgos y registro de decisiones

## Decisiones confirmadas

| ID | Decisión | Motivo |
|---|---|---|
| ADR-001 | Dominio: clínica/consultorio ficticio | definido por el usuario |
| ADR-002 | Prioridad: RAG + LangChain + LangGraph + OCI | objetivo principal del challenge |
| ADR-003 | Turnos son secundarios | evita diluir la demostración técnica |
| ADR-004 | No usar datos reales | seguridad y alcance académico |
| ADR-005 | No implementar durante esta etapa | planificación primero |
| ADR-006 | Proyecto: Medinova AI Agent; clínica: Medinova | definido por el usuario |
| ADR-007 | Audiencia: pacientes y personal | definido por el usuario |
| ADR-008 | Corpus fuente en PDF | definido por el usuario |
| ADR-010 | Proveedor de IA: Gemini | definido por el usuario |
| ADR-013 | Turnos: solicitud pendiente + panel básico | diferencial secundario confirmado |
| ADR-014 | Persistencia de turnos: CSV | simplicidad solicitada para el MVP |
| ADR-021 | Las API keys no se hardcodean | seguridad y posibilidad de rotación |
| ADR-022 | Secretos locales en `.env` ignorado | separa configuración y código |
| ADR-023 | Gemini API key en OCI Vault | almacenamiento centralizado y cifrado para deploy |
| ADR-024 | Acceso desde OCI mediante instance principal | evita credenciales OCI estáticas dentro de la VM |
| ADR-011 | Interfaz: Streamlit | mantiene chat, carga futura y panel en Python |
| ADR-012 | Vector store: Chroma local persistente | suficiente para el MVP y fácil de inspeccionar |
| ADR-018 | Chat: `gemini-3.5-flash`; fallback `gemini-2.5-flash` | modelos Flash estables y configurables |
| ADR-019 | Embeddings: `gemini-embedding-001` | el pipeline extrae texto de los PDF antes de vectorizar |
| ADR-025 | Corpus inicial: cinco PDF institucionales versión 2.0, cinco páginas cada uno | suficiente profundidad para evaluar chunking y retrieval sin introducir relleno |

## Decisiones pendientes (bloqueantes)

| ID | Decisión | Opciones | Recomendación provisional | Impacto |
|---|---|---|---|---|
| ADR-009 | Corpus | fijo / carga por usuario | fijo para MVP | seguridad y reproducibilidad |
| ADR-015 | OCI | Compute / Container Instances | Compute VM | deploy y evidencia |
| ADR-016 | Sistema/forma/TLS | Ubuntu u Oracle Linux; Ampere o x86; proxy o puerto directo | resolver según cuota/región | compatibilidad/costo/seguridad |
| ADR-017 | Seguridad clínica | reglas + clasificador / solo LLM | enfoque híbrido | falsos negativos/costo |
| ADR-020 | Carga de PDF | control visible futuro / habilitada en MVP | reservar UI, habilitar después | seguridad y reindexado |

## Riesgos

| Riesgo | Prob. | Impacto | Mitigación / señal |
|---|---:|---:|---|
| Corpus insuficiente o contradictorio | alta | alta | revisión editorial, versionado y preguntas doradas |
| Recuperación irrelevante | media | alta | evaluar retrieval antes de generación; ajustar chunks/k |
| Alucinación pese al contexto | media | alta | contrato estricto, citas, suficiencia y evaluación |
| Pregunta clínica mal clasificada | media | crítica | reglas de alta cobertura, set adversarial y ruta conservadora |
| Modelo/embedding cambia de nombre | media | media | confirmar documentación vigente al implementar y abstraer proveedor |
| Índice incompatible tras cambios | media | media | manifiesto con hash/modelo/splitter y reconstrucción |
| Filtrado accidental de datos reales | baja | crítica | datos sintéticos, minimización y revisión antes de enviar |
| CSV de turnos se corrompe con concurrencia | media | media | escritor único, archivo temporal + reemplazo atómico y pruebas de escrituras cercanas; reevaluar almacenamiento solo si el alcance crece |
| Recursos OCI/arquitectura sin cuota | media | alta | verificar región/cuota temprano y tener alternativa |
| Puerto público sin TLS | media | alta | proxy TLS o demo temporal controlada |
| API key expuesta en Git, logs o capturas | baja | crítica | `.env` ignorado, Vault, redacción de logs, secret scanning y rotación |
| Política IAM demasiado amplia | media | alta | dynamic group acotado y permiso de solo lectura al secreto necesario |
| ARM incompatible con dependencia | baja/media | media | validar wheels o elegir x86 |
| La feature de turnos domina la demo | media | alta | limitar guion y backlog; RAG ocupa la mayor parte |

## Criterio para cerrar decisiones

Una ADR pasa a “confirmada” solo con respuesta del usuario. Luego se registrarán fecha, alternativa elegida y consecuencias; no se reescribirá el pasado para ocultar cambios.
