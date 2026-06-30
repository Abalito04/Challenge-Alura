# Medinova AI Agent

Asistente administrativo ficticio para demostrar RAG, LangChain, LangGraph y despliegue en OCI. El corpus está compuesto por documentos PDF de Clínica Medinova y no contiene datos reales.

## Estado actual

- Planificación y diagramas completos en [`docs/`](docs/).
- Cinco documentos PDF ficticios en [`source_documents/`](source_documents/).
- Pipeline de ingesta, chunking e indexación Chroma implementado y probado offline.
- Interfaz, generación RAG, flujo LangGraph, turnos y deploy todavía no implementados.

## Seguridad

No agregues claves al repositorio. Copiá `.env.example` como `.env` y completá la clave únicamente en tu entorno local. Para OCI se utilizará Vault/Secret Management.

## Ejecución de esta fase

```powershell
python -m pip install -r requirements.txt
python -m scripts.ingest
python -m scripts.evaluate_retrieval
pytest
```

La ingesta real con Gemini requiere `GEMINI_API_KEY`. Las pruebas usan embeddings determinísticos locales y no consumen APIs. La línea base offline actual carga 25 páginas, produce 50 chunks y obtiene 10/14 aciertos de fuente en Recall@5; la evaluación definitiva se realizará con `gemini-embedding-001`.
