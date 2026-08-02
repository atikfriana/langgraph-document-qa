# 🤖 Document QA Agent

An end-to-end AI-powered **Document Question Answering** system built with **LangGraph**, **Google Gemini 3**, **Retrieval-Augmented Generation (RAG)**, **FAISS**, and **Tavily Web Search**.

The application answers questions from a document, maintains multi-turn conversation memory, and autonomously decides whether to answer using retrieved document context or perform a web search.

---

## Features

- Retrieval-Augmented Generation (RAG)
- Google Gemini 3 (`gemini-3-flash-preview`)
- Conversation Memory with LangGraph Checkpointing
- FAISS Vector Database
- Autonomous Tavily Web Search
- FastAPI REST API
- Modern Next.js Chat Interface
- Source References
- Responsive User Interface
- Health Monitoring

---

## System Architecture

```text
                  Next.js Frontend
                         │
                         ▼
                  FastAPI Backend
                         │
                         ▼
                 LangGraph Workflow
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
 Document Retrieval                Web Search Tool
      (FAISS)                         (Tavily)
        │                                 │
        └────────────────┬────────────────┘
                         ▼
                  Google Gemini 3
                         │
                         ▼
                  Final AI Response
```

---

## LangGraph Workflow

```text
                User Question
                      │
                      ▼
                 retrieve
                      │
                      ▼
                decide_tool
                 │         │
         No Tool │         │ Tool Needed
                 ▼         ▼
            generate   tool_exec
                 │         │
                 └────┬────┘
                      ▼
                 generate
                      │
                      ▼
               Assistant Reply
```

The agent first retrieves relevant document chunks. If the retrieved context is insufficient, it automatically invokes the web search tool before generating the final answer.

---

## 🛠 Tech Stack

### Backend

- FastAPI
- LangGraph 1.x
- LangChain 1.x
- Google Gemini 3
- Google Generative AI Embeddings
- FAISS
- Tavily Search
- Pydantic v2

### Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide React

---

## 📂 Project Structure

```text
doc-qa-agent/
│
├── doc-qa-agent-backend/
│   ├── app/
│   ├── data/
│   ├── docs/
│   ├── scripts/
│   ├── tests/
│   └── README.md
│
├── doc-qa-agent-frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── README.md
│
└── README.md
```

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/doc-qa-agent.git

cd doc-qa-agent
```

### Backend

```bash
cd doc-qa-agent-backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Configure the required environment variables:

```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
TAVILY_API_KEY=YOUR_TAVILY_API_KEY

CHAT_MODEL_NAME=gemini-3-flash-preview
EMBEDDING_MODEL_NAME=models/gemini-embedding-001
```

Build the vector database:

```bash
python scripts/run_ingest.py
```

Start the backend:

```bash
uvicorn app.api.main:app --reload
```

API Documentation:

```
http://localhost:8000/docs
```

---

### Frontend

```bash
cd ../doc-qa-agent-frontend

npm install
```

Create:

```text
.env.local
```

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Run the development server:

```bash
npm run dev
```

Frontend:

```
http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/chat` | Send a message to the AI agent |
| GET | `/health` | Liveness check |
| GET | `/health/ready` | Readiness check |

---

## Screenshots

Screenshots will be added after deployment.

```
docs/images/chat.png
docs/images/web-search.png
docs/images/mobile.png
```

---

## Deployment

### Backend

- Render
- Railway
- Docker

### Frontend

- Vercel
- Netlify

---

## Roadmap

- PDF Upload Support
- Multi-document Retrieval
- Streaming Responses
- Authentication
- Cloud Vector Database
- User Accounts
- Conversation History

---

## 📄 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

**Atika Fitria Arifiana**

Information Technology — Universitas Brawijaya

2026