# Flujo del agente

## Objetivo

Controlar cada consulta mediante LangGraph antes de invocar el RAG. La salida debe ser trazable: intención, ruta, documentos recuperados y causa de rechazo o insuficiencia.

## Secuencia principal

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Interfaz
    participant G as LangGraph
    participant S as Seguridad
    participant R as Retriever LangChain
    participant M as LLM
    U->>UI: pregunta
    UI->>G: entrada validada
    G->>G: clasificar intención
    alt consulta documental
        G->>S: validar dominio
        alt permitida
            G->>R: recuperar chunks con metadatos
            R-->>G: contexto + scores + fuentes
            alt evidencia suficiente
                G->>M: pregunta + contexto + contrato de respuesta
                M-->>G: respuesta fundamentada
                G-->>UI: respuesta + fuentes
            else evidencia insuficiente
                G-->>UI: no hay información suficiente
            end
        else clínica/peligrosa
            G-->>UI: rechazo seguro
        end
    else solicitud de turno opcional
        G->>G: validar datos administrativos mínimos
        G-->>UI: solicitud pendiente o campos faltantes
    end
    UI-->>U: resultado
```

## Estado conceptual

| Campo | Uso |
|---|---|
| `user_input` | texto original |
| `intent` | documental, clínica, turno, inválida |
| `safety_status` | permitida, rechazada, revisar |
| `retrieved_docs` | chunks y metadatos |
| `retrieval_evidence` | scores y reglas de suficiencia |
| `answer` | respuesta final |
| `citations` | documento, sección/página y chunk |
| `appointment_payload` | solo para la ruta secundaria |
| `errors` | fallos controlados y trazables |

## Contrato de respuesta RAG

- Usar exclusivamente el contexto recuperado.
- Distinguir respuesta total, parcial e insuficiente.
- Citar documento y localizador legible.
- No revelar prompts, claves o metadatos internos sensibles.
- No diagnosticar, recomendar medicamentos ni interpretar síntomas.
- Ante riesgo clínico, recomendar consulta profesional; la redacción de urgencia exacta queda pendiente de definición.

## Reducción de alucinaciones

Se combinarán filtros de dominio, retrieval con metadatos, umbral de suficiencia, prompt estricto, citas verificables y pruebas de groundedness. Un score vectorial aislado no se tratará como certeza: el criterio final debe validarse empíricamente con el corpus y el set de evaluación.
