# Company FAQ Assistant

A small production-oriented FAQ assistant built with **FastAPI**, **NVIDIA NIM**, **ChromaDB**, and **SQLite**. It answers questions only from files in `knowledge/` and captures consultation requests in a separate lead database.

There is no Ollama integration, local LLM, local embedding model, model selector, semantic answer cache, or hidden provider routing. NVIDIA NIM provides both chat completions and embeddings.

## Quick start

1. Create an NVIDIA API key in the [NVIDIA API Catalog](https://build.nvidia.com/), then copy `.env.example` to `.env` and set `NVIDIA_API_KEY`.

2. Create a virtual environment, install dependencies, and index the knowledge base.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   # Edit .env and add NVIDIA_API_KEY
   python -m backend.ingest --reset
   ```

3. Start the app and open http://localhost:8000.

   ```powershell
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

Do not use `file:///.../frontend/index.html` as the normal way to run the app: that is only a browser file preview and has no API server. The JavaScript does redirect file previews to port 8000 for development, but FastAPI still needs to be running first.

For the offline unit tests, install the development tools and run `pytest`:

```powershell
pip install -r requirements-dev.txt
pytest
```

## Day-to-day knowledge-base updates

Put `.pdf`, `.txt`, or `.md` files anywhere beneath `knowledge/`. After changing files, run:

```powershell
python -m backend.ingest --reset
```

The reset is important: it removes chunks for files that were deleted or changed. It makes NVIDIA embedding calls, so it is intentionally a manual deployment step rather than an action on every server start.

If `/api/chat` returns HTTP 503 after a fresh install, make sure `NVIDIA_API_KEY` is set in `.env`, then run the indexing command above. A successful run prints `Indexed ... chunks into ChromaDB.`

## Production deployment

Set `ENVIRONMENT=production`, `ALLOWED_ORIGINS=https://your-domain.example`, and `ALLOWED_HOSTS=your-domain.example` in `.env`. Keep the NVIDIA key only in your deployment secret store—never in browser JavaScript or Git.

```bash
docker compose build
docker compose run --rm faq-assistant python -m backend.ingest --reset
docker compose up -d
```

Put the container behind an HTTPS reverse proxy. The mounted `data/` directory contains the persistent Chroma index (`data/chroma/`) and lead records (`data/app.db`); back it up before releases. SQLite is ideal for a single application container. For multiple replicas, replace `backend/app/database.py` with PostgreSQL and use a shared Chroma-compatible vector store.

## API

- `GET /health` – lightweight health check.
- `POST /api/chat` – accepts `{ "message": "..." }`, returns the grounded answer and friendly sources.
- `POST /api/leads` – accepts `name`, `email`, and optional `company` and `message`; stores a lead in SQLite.

Input sizes, email format, SQL parameters, host checks, CORS configuration, security headers, and non-secret error handling are built into the app. Add a shared rate limiter / WAF at the reverse proxy before exposing a high-traffic public endpoint.

See [architecture.md](architecture.md) for the complete flow and file-by-file guide.
For GitHub setup and deployment instructions, see [INSTALLATION.md](INSTALLATION.md).
