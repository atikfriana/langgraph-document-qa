# Document QA Agent Backend

A production-oriented AI backend built with **FastAPI**, **LangGraph**, and **Google Gemini 3** that answers questions from a document using **Retrieval-Augmented Generation (RAG)** and automatically performs web search only when the document cannot answer the user's question.

---

## Features

- Google Gemini 3 (`gemini-3-flash-preview`)
- LangGraph multi-node workflow
- Retrieval-Augmented Generation (RAG)
- FAISS vector database
- Autonomous Tavily Web Search
- Conversation memory using LangGraph Checkpointing
- FastAPI REST API
- Source references for every response
- Health and readiness endpoints
- Offline unit testing

---

## Tech Stack

- Python 3.10+
- FastAPI
- LangGraph 1.x
- LangChain 1.x
- Google Gemini 3
- Google Generative AI Embeddings
- FAISS
- Tavily Search
- Pydantic v2

---

## Architecture

```text
User Question
      │
      ▼
Retrieve Document
      │
      ▼
Decide Tool
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Generate  Web Search
             │
             ▼
         Generate
             │
             ▼
      Final Response
```

The LangGraph workflow automatically determines whether the retrieved document contains enough information. If not, it invokes the Tavily web search tool before generating the final answer.

---

## Project Structure

```text
app/
├── api/              FastAPI routes and dependency injection
├── core/             Configuration, logging, exceptions
├── graph/            LangGraph workflow, nodes, edges, prompts
├── llm/              Gemini model client
├── memory/           Session management and checkpointing
├── retrieval/        Document loading, embeddings, FAISS
├── tools/            Web search tool
└── models.py         Shared domain models

data/
    Sample document and evaluation assets

docs/
    Local setup and deployment guides

scripts/
    Document ingestion scripts

tests/
    Unit and integration tests
```

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy:

```text
.env.example
```

to

```text
.env
```

Required variables:

```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

CHAT_MODEL_NAME=gemini-3-flash-preview

EMBEDDING_MODEL_NAME=models/gemini-embedding-001
```

Optional:

```env
TAVILY_API_KEY=YOUR_TAVILY_API_KEY
```

### 3. Build the Vector Database

```bash
python scripts/run_ingest.py
```

### 4. Start the API

```bash
uvicorn app.api.main:app --reload
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/chat` | Send a message to the AI agent |
| GET | `/health` | Liveness check |
| GET | `/health/ready` | Readiness check |

---

## Example Request

```json
{
  "message": "Summarize this document."
}
```

---

## Example Response

```json
{
  "session_id": "...",
  "response": "...",
  "tool_used": false,
  "sources": [
    {
      "source": "sample_document.pdf",
      "chunk_id": "chunk_1",
      "score": 0.92
    }
  ]
}
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `CHAT_MODEL_NAME` | Yes | Gemini chat model |
| `EMBEDDING_MODEL_NAME` | Yes | Gemini embedding model |
| `TAVILY_API_KEY` | Optional | Enables web search |
| `DATA_DIR` | Optional | Document directory |
| `VECTOR_STORE_DIR` | Optional | FAISS storage |

---

## Testing

Run all tests:

```bash
pytest
```

The project includes unit and integration tests using mocked components, allowing tests to run without external API calls.

---

## Deployment

Recommended platforms:

- Render
- Railway
- Docker

Configure all required environment variables in your deployment platform before starting the application.

---

## Roadmap

- PDF upload support
- Multi-document retrieval
- Streaming responses
- Authentication
- Cloud vector database
- User management

---

## License

MIT License