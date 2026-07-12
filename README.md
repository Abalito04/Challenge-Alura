# Medinova AI Agent

https://medinova.up.railway.app/
https://www.youtube.com/watch?v=ANAVstZ6Yog

Asistente administrativo para demostrar RAG, LangChain, LangGraph y despliegue en Railway. El corpus está compuesto por documentos PDF de Clínica Medinova creados para la demo y no contiene datos reales.

## Estado actual

- Planificación y diagramas completos en [`docs/`](docs/).
- Seis documentos PDF ficticios y 30 páginas en [`source_documents/`](source_documents/).
- Pipeline RAG, citas, guardrails y flujo LangGraph implementados.
- Cohere, Gemini y OpenAI disponibles por configuración; Cohere queda activo por defecto para LLM y embeddings, con Gemini como fallback del LLM.
- Interfaz Streamlit implementada con asistente, trazabilidad técnica, carga protegida de PDFs y solicitudes pendientes.
- Deploy preparado para Railway mediante `railway.json` y `scripts/railway_start.py`.

## Seguridad

No agregues claves al repositorio. Copiá `.env.example` como `.env` y completá únicamente las claves de los proveedores que vayas a usar. En Railway, las claves se cargan como variables de entorno del servicio.

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

## Deploy en Railway

El repositorio incluye configuración de Railway:

- `railway.json`: define builder, start command, healthcheck y reinicio.
- `scripts/railway_start.py`: crea carpetas de datos, genera el índice Chroma si no existe y arranca Streamlit usando el `PORT` de Railway.

Variables mínimas en Railway:

```env
LLM_PROVIDER=cohere
LLM_MODEL=command-a-03-2025
LLM_FALLBACK_PROVIDER=gemini
LLM_FALLBACK_MODEL=gemini-2.5-flash
EMBEDDINGS_PROVIDER=cohere
EMBEDDINGS_MODEL=embed-v4.0
COHERE_API_KEY=tu_clave
GEMINI_API_KEY=tu_clave
DOCUMENT_UPLOAD_PASSWORD=tu_contraseña
```

Para persistir Chroma, historial y solicitudes, crear un volumen en Railway montado en `/app/data`.

Guía completa: [`docs/12_deploy_railway.md`](docs/12_deploy_railway.md).
