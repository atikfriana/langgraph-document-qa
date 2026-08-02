# Deployment Guide

This guide covers running the Document Q&A Agent with Docker, and the
configuration considerations for a production deployment.

## Prerequisites

- Docker and Docker Compose
- A Google Gemini API key
- (Optional) A Tavily API key for the web search tool

## 1. Configure environment

```bash
cp .env.example .env
```

Set `GOOGLE_API_KEY` (required) and `TAVILY_API_KEY` (optional) in `.env`.
Docker Compose loads this file via `env_file:` for both services defined in
`docker-compose.yml`.

**Never commit `.env`.** Confirm `.gitignore` excludes it before pushing
anywhere.

## 2. Build the image

```bash
docker compose build
```

This builds a multi-stage image: dependencies are compiled in a `builder`
stage, then copied into a slim `runtime` stage that runs as a non-root user
(`appuser`) on port `8000`.

## 3. Run ingestion inside the container

The vector index must be built before the API can serve `/chat` requests.
`docker-compose.yml` defines a dedicated one-off `ingest` service for this
(under the `ingest` Compose profile) so it doesn't run automatically on
every `up`:

```bash
docker compose --profile ingest run --rm ingest
```

This mounts the same `vector_db_data` named volume that the main service
uses, so the index persists and is immediately visible to the API
container.

## 4. Start the API

```bash
docker compose up -d doc-qa-agent
```

The service exposes port `8000` (configurable via `API_PORT` in `.env`).
A Docker `HEALTHCHECK` is defined against `/health`, and Compose is
configured with `restart: unless-stopped`.

Verify:

```bash
curl http://localhost:8000/health/ready
```

## 5. Re-running ingestion after a document or embedding-model change

If `data/sample_document.pdf` changes, or you swap in your own document, or
you change `EMBEDDING_MODEL_NAME`, re-run the ingestion step (Step 3) and
then restart the API container so it picks up the refreshed index:

```bash
docker compose --profile ingest run --rm ingest
docker compose restart doc-qa-agent
```

The app validates the persisted index's vector dimension against the
currently configured embedding model at startup and will fail fast with a
clear `VectorStoreDimensionMismatchError` if you forget this step after
changing the embedding model.

## Production configuration notes

These are configuration decisions to revisit before exposing this service
publicly — the defaults in `.env.example` are tuned for local development,
not production:

- **CORS**: `.env.example` defaults `CORS_ALLOW_ORIGINS=["*"]`. Combined
  with `allow_credentials=True` (set in `app/api/main.py`), browsers will
  reject credentialed cross-origin requests against a wildcard origin.
  Replace `CORS_ALLOW_ORIGINS` with an explicit list of allowed origins for
  any real deployment.
- **Secrets**: `docker-compose.yml` loads `.env` via `env_file:` for
  simplicity. In a real production environment, source `GOOGLE_API_KEY` and
  `TAVILY_API_KEY` from a secrets manager (e.g. AWS Secrets Manager, GCP
  Secret Manager, Docker/Kubernetes secrets) instead of a plaintext file
  baked into the deployment.
- **Authentication**: `/chat` currently has no authentication layer. Add an
  API key or bearer-token dependency before deploying anywhere reachable
  from the public internet.
- **Rate limiting**: There is currently no rate limiting on `/chat`. Since
  each request costs at least one (and up to two, if the tool is called)
  Gemini completions plus one embedding call, unrestricted access is a
  direct cost exposure.
- **Checkpointer backend**: `CHECKPOINTER_BACKEND=memory` (the default)
  loses all conversation history on restart and does not share state across
  multiple replicas. Setting `CHECKPOINTER_BACKEND=sqlite` uses a
  **synchronous** `SqliteSaver`; LangGraph offloads its sync calls to a
  thread pool when the graph is invoked via `ainvoke`, so it works, but it
  is not optimized for high-concurrency workloads. For a horizontally
  scaled deployment (more than one API replica) or high request volume, a
  proper async, shared backend (e.g. `langgraph-checkpoint-postgres`) is
  the recommended next step — this is a future extension, not currently
  implemented.
- **Logging**: `LOG_JSON=true` is the production default (set in
  `.env.example`) — logs are emitted as single-line JSON to stdout, ready
  for collection by a log aggregator (CloudWatch, Datadog, ELK, etc.).

## Scaling considerations

- The FAISS index is loaded into memory once per process at startup (see
  `app/api/main.py`'s `lifespan`). Each replica loads its own copy from the
  shared `vector_db_data` volume/image layer — this scales horizontally for
  read traffic without any additional coordination, since the index is
  read-only at serving time.
- Conversation memory does **not** currently scale horizontally with the
  default or `sqlite` checkpointer backends — see the note above.