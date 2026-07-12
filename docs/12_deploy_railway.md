# Deploy en Railway

## Objetivo

Railway reemplaza a OCI como destino de despliegue para la demo pública de Medinova AI Agent. El objetivo es reducir fricción operativa y enfocar la presentación en RAG, LangChain, LangGraph, Cohere/Gemini y la interfaz Streamlit.

## Decisión técnica

- **Plataforma:** Railway.
- **Runtime:** Python + Streamlit.
- **Start command:** `python -m scripts.railway_start`.
- **Persistencia recomendada:** volumen montado en `/app/data`.
- **LLM principal:** Cohere `command-a-03-2025`.
- **Fallback LLM:** Gemini `gemini-2.5-flash`.
- **Embeddings:** Cohere `embed-v4.0`.

Railway permite definir configuración junto al código mediante `railway.toml` o `railway.json`; el archivo del repositorio define builder, comando de inicio, healthcheck y política de reinicio. Según la documentación oficial, estas configuraciones de código se combinan con los ajustes del dashboard en cada despliegue.

## Archivos agregados

| Archivo | Uso |
|---|---|
| `railway.json` | Configuración de build/deploy para Railway. |
| `scripts/railway_start.py` | Prepara carpetas persistentes, genera índice Chroma si falta y arranca Streamlit en el puerto asignado por Railway. |
| `.dockerignore` | Evita enviar secretos, cachés, entornos virtuales y datos generados al build. |

## Variables de entorno

Configurar estas variables en Railway, no en el repositorio:

```env
LLM_PROVIDER=cohere
LLM_MODEL=command-a-03-2025
LLM_FALLBACK_PROVIDER=gemini
LLM_FALLBACK_MODEL=gemini-2.5-flash
EMBEDDINGS_PROVIDER=cohere
EMBEDDINGS_MODEL=embed-v4.0
COHERE_API_KEY=tu_clave_de_cohere
GEMINI_API_KEY=tu_clave_de_gemini
DOCUMENT_UPLOAD_PASSWORD=una_contraseña_para_carga_pdf
```

Opcional:

```env
SKIP_STARTUP_INGEST=1
```

Usar `SKIP_STARTUP_INGEST=1` solo si ya existe un índice Chroma válido en el volumen y no se desea reintentar la ingesta al iniciar.

## Persistencia

Crear un volumen en Railway y montarlo en:

```text
/app/data
```

Esto conserva:

- índice Chroma: `data/chroma/`;
- historial de chat: `data/chat_history.json`;
- solicitudes pendientes: `data/turnos_solicitudes.csv`.

Railway documenta que los volúmenes permiten persistir datos de servicios y que, si una app escribe en una ruta relativa como `./data`, el volumen debe montarse incluyendo la ruta de la aplicación, por ejemplo `/app/data`. También indica que los volúmenes se montan al iniciar el contenedor, no durante el build ni durante pre-deploy; por eso la ingesta se hace dentro del comando de inicio.

## Pasos de despliegue

1. Subir el repositorio a GitHub.
2. Crear un proyecto en Railway desde ese repositorio.
3. Configurar las variables de entorno listadas arriba.
4. Crear un volumen y montarlo en `/app/data`.
5. Ejecutar deploy.
6. Abrir la URL pública generada por Railway.
7. Probar:
   - saludo conversacional;
   - consulta de especialidades;
   - consulta con fuentes PDF;
   - solicitud de turno pendiente;
   - carga protegida de PDF;
   - reinicio del servicio manteniendo `data/`.

## Validaciones esperadas

- La app responde en `/_stcore/health`.
- En el primer inicio, si no hay índice persistido, el log muestra `Startup ingest completed`.
- En reinicios posteriores, el log muestra que encontró la colección Chroma existente.
- Las respuestas documentales muestran fuentes.
- Las consultas fuera del dominio no fuerzan uso innecesario del LLM.

## Decisiones pendientes

- Dominio personalizado: por ahora puede usarse el dominio público de Railway.
- Persistencia de PDFs cargados por interfaz: la demo actual persiste el índice y datos operativos en `/app/data`; si se requiere conservar también cada PDF subido entre redeploys, conviene mover las cargas a una carpeta persistente dedicada.
- Costos/cuotas: controlar uso de Cohere/Gemini desde los dashboards de cada proveedor y desde métricas/logs de Railway.

## Fuentes

- Railway Config as Code: https://docs.railway.com/config-as-code/reference
- Railway Volumes: https://docs.railway.com/volumes
