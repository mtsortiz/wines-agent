# Wine Data Agent

Wine Data Agent es una aplicación de consulta sobre vinos construida con FastAPI y un agente conversacional basado en LangChain y Gemini. El proyecto permite interactuar con una base de datos SQLite local y con un almacén vectorial Chroma para responder preguntas sobre vinos a partir de sus atributos técnicos.

La idea central es simple: cargas un subconjunto del dataset de vinos, el sistema lo procesa y luego el agente puede buscar por `id`, `designation` o por criterios como país, puntos, precio, provincia, región y nombre del catador.

## Funcionalidades

- API REST con FastAPI para conversar con el agente.
- Agente con memoria de conversación por `thread_id`.
- Consultas sobre una base SQLite local con datos de vinos.
- Búsqueda por filtros técnicos mediante herramientas del agente.
- Persistencia de embeddings en Chroma para futuras extensiones de búsqueda semántica.

## Estructura del proyecto

- `src/main.py`: punto de entrada de la API.
- `src/api/routers/router.py`: endpoint de conversación.
- `src/api/schemas/schemas.py`: esquemas de request y response.
- `src/agent/agent.py`: configuración del agente y del modelo.
- `src/agent/tools.py`: herramientas para consultar la base de datos.
- `scripts/ingests.py`: carga inicial del dataset en SQLite y Chroma.
- `data/raw/`: dataset fuente en CSV.
- `data/processed/`: base SQLite generada y vector store Chroma.

## Requisitos

- Python 3.11 o superior.
- Una clave de API de Google Gemini en la variable de entorno `GOOGLE_API_KEY`.

## Instalación

1. Crear y activar el entorno virtual.
2. Instalar dependencias.

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -U pip
pip install -e .
```

## Configuración

Define la variable de entorno `GOOGLE_API_KEY` antes de ejecutar el proyecto.

En Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY="tu_clave_aqui"
```

En bash:

```bash
export GOOGLE_API_KEY="tu_clave_aqui"
```

## Carga de datos

El script de ingestión toma el archivo CSV ubicado en `data/raw/winemag-data-130k-v2-selected-columns.csv`, crea la base SQLite en `data/processed/wines_table.db` y genera el índice vectorial en `data/processed/chroma_db/`.

Ejecuta la carga inicial con:

```bash
python scripts/ingests.py
```

Notas importantes:

- La tabla SQLite se crea con el nombre `wines`.
- Las consultas del agente deben apuntar a `wines`, no a `wines_table`.

## Ejecución de la API

El servidor se expone desde `src.main:app`.

```bash
uvicorn src.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

## Endpoint principal

### `POST /api/conversation`

Envía una consulta al agente y, opcionalmente, un `thread_id` para continuar una conversación previa.

Ejemplo:

```json
{
	"query": "Busca vinos de Francia con más de 90 puntos",
	"thread_id": null
}
```

Respuesta esperada:

```json
{
	"answer": "...",
	"thread_id": "...",
	"sources": ["Tool: query_by_specs"]
}
```

## Ejemplos de uso

- Buscar por identificador: `id` del vino.
- Buscar por denominación: `designation`.
- Filtrar por criterios: `country`, `points`, `price`, `province`, `region_1`, `region_2` y `taster_name`.

## Funcionamiento interno

1. El cliente envía una pregunta al endpoint de conversación.
2. FastAPI delega la consulta al agente.
3. El agente decide si necesita usar una herramienta de consulta.
4. La herramienta accede a la base SQLite local y devuelve los datos encontrados.
5. La API responde con la salida generada y las herramientas utilizadas.

## Próximos pasos sugeridos

- Agregar ejemplos de requests con `curl` o Postman.
- Documentar el esquema completo de columnas del dataset.
- Exponer un frontend simple para conversar con el agente.
