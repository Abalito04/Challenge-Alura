# Medinova AI Agent

Asistente administrativo ficticio para demostrar RAG, LangChain, LangGraph y despliegue en OCI. El corpus está compuesto por documentos PDF de Clínica Medinova y no contiene datos reales.

## Estado actual

- Planificación y diagramas completos en [`docs/`](docs/).
- Seis documentos PDF ficticios y 30 páginas en [`source_documents/`](source_documents/).
- Pipeline RAG, citas, guardrails y flujo LangGraph implementados.
- Cohere, Gemini y OpenAI disponibles por configuración; Cohere queda activo por defecto para LLM y embeddings, con Gemini como fallback del LLM.
- Interfaz Streamlit implementada con asistente, trazabilidad técnica, carga protegida de PDFs y solicitudes pendientes.

## Seguridad

No agregues claves al repositorio. Copiá `.env.example` como `.env` y completá únicamente las claves de los proveedores que vayas a usar. Para OCI se utilizará Vault/Secret Management.

## Ejecución de esta fase

```powershell
python -m pip install -r requirements.txt
python -m scripts.ingest
python -m scripts.evaluate_retrieval
pytest
```

## Interfaz Streamlit

Con el entorno virtual activo y el índice creado:

```powershell
python -m streamlit run streamlit_app.py
```

La interfaz incluye el asistente RAG con citas y trazabilidad LangGraph, el inventario PDF, carga protegida de documentos y una demostración secundaria de solicitudes pendientes persistidas en CSV.

La ingesta real requiere la clave del proveedor configurado. Las pruebas usan embeddings determinísticos locales y no consumen APIs. Cada proveedor/modelo de embeddings usa una colección Chroma independiente, por lo que al cambiarlo hay que ejecutar nuevamente `python -m scripts.ingest`.
