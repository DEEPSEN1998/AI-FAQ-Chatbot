# Installation and Run Guide

## K8ight AI Chat Bot Assistant

A production-oriented company FAQ chatbot powered by NVIDIA NIM, ChromaDB RAG, FastAPI, and SQLite lead capture.

## Features

- Answers company questions using a knowledge base in `knowledge/`
- Uses NVIDIA NIM for both embeddings and chat responses
- Stores vectors locally in ChromaDB
- Displays every portfolio project in a structured table
- Captures consultation leads in SQLite
- Includes Docker configuration and automated tests

## Prerequisites

- Python 3.11 or newer
- An NVIDIA API key from [NVIDIA API Catalog](https://build.nvidia.com/)
- Optional: Docker Desktop for container deployment

## 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AI-FAQ-Chatbot.git
cd AI-FAQ-Chatbot
```

## 2. Create and activate a virtual environment

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

For tests and development tools, install:

```bash
pip install -r requirements-dev.txt
```

## 4. Configure NVIDIA NIM

Copy the template configuration file:

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Open `.env` and add your key:

```env
NVIDIA_API_KEY=nvapi-your-nvidia-api-key
```

Do not commit `.env` to GitHub. It is already ignored by `.gitignore`.

## 5. Add or update knowledge files

Place company documents in the `knowledge/` folder. Supported formats are:

- PDF (`.pdf`)
- Plain text (`.txt`)
- Markdown (`.md`)

Example:

```text
knowledge/
├── pdf/company.pdf
└── txt/company_details.txt
```

## 6. Create the ChromaDB knowledge index

Run this after adding, editing, or deleting any knowledge file:

```bash
python -m backend.ingest --reset
```

This command chunks the documents, generates NVIDIA NIM embeddings, and stores them in `data/chroma/`. A successful run prints `Indexed ... chunks into ChromaDB.`

## 7. Run the application

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

Do not open `frontend/index.html` directly as a `file:///` URL. The FastAPI server serves both the website and the API.

## 8. Run tests

```bash
pytest
```

## Docker deployment

1. Create and configure `.env` as described above.
2. Build the image and create the production vector index:

### Option A: Using Docker Compose
```bash
docker compose build
docker compose run --rm faq-assistant python -m backend.ingest --reset
docker compose up -d
```

### Option B: Using Standalone Docker CLI (Windows CMD)
```cmd
# 1. Run knowledge ingestion
docker run --rm -v "%cd%\data:/app/data" --env-file .env ai-faq-chatbot python -m backend.ingest --reset

# 2. Run the server container with port and data persistent volume
docker run -p 8000:8000 -v "%cd%\data:/app/data" --env-file .env ai-faq-chatbot
```

The persistent `data/` directory contains:

- `data/chroma/` — ChromaDB vectors
- `data/app.db` — captured leads

Back up this directory before deployments or server migrations.

## Production configuration

Before deployment, update these values in `.env`:

```env
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-domain.example
ALLOWED_HOSTS=your-domain.example
```

Place the application behind an HTTPS reverse proxy and configure rate limiting at the edge.

## Project structure

```text
backend/             FastAPI API, RAG, NVIDIA client, ingestion command
frontend/            Browser chat interface and lead form
knowledge/           Source documents for RAG
data/                Generated ChromaDB index and SQLite lead database
architecture.md      Detailed component and data-flow documentation
```

For technical architecture details, see [architecture.md](architecture.md).
