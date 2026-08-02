# Document QA Assistant Frontend

A modern chat interface built with **Next.js 15**, **React 19**, and **TypeScript** for interacting with the Document QA Agent backend powered by **LangGraph**, **Google Gemini 3**, and **Retrieval-Augmented Generation (RAG)**.

---

## Features

- Modern AI chat interface
- Document question answering
- Conversation memory
- Session persistence
- Source references
- Web search indicator
- Copy-to-clipboard support
- Retry failed requests
- Backend health monitoring
- Responsive layout
- Smooth UI animations

---

## Tech Stack

- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide React
- Fetch API

---

## Project Structure

```text
app/
    App Router, pages, layouts, and global styles

components/
    chat/
    layout/
    status/
    ui/

hooks/
    Custom React hooks

services/
    Backend API client

types/
    Shared TypeScript interfaces

lib/
    Utility functions

public/
    Static assets
```

---

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file.

Example:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Run the Development Server

```bash
npm run dev
```

Application:

```
http://localhost:3000
```

---

## Backend Requirements

The frontend requires the backend API to be running.

Default backend URL:

```
http://localhost:8000
```

Make sure the backend CORS configuration allows requests from:

```
http://localhost:3000
```

---

## Main Features

### Chat Interface

- Multi-turn conversations
- Typing indicator
- Auto-scroll
- Enter to send
- Shift + Enter for new line

### Conversation Memory

The current session is stored in `localStorage`, allowing users to continue conversations after refreshing the page.

### Source References

Each response can display:

- Source document
- Chunk ID
- Similarity score

### Web Search Indicator

Responses indicate whether they were generated using:

- Retrieved document context
- Web search

### Health Monitoring

The application continuously monitors backend availability through the health endpoints.

Status indicators include:

- Online
- Degraded
- Offline

### Error Handling

The interface gracefully handles:

- Backend unavailable
- Network failures
- API errors
- Rate limits
- Retry requests

---

## Responsive Design

Optimized for:

- Desktop
- Tablet
- Mobile

Includes:

- Responsive sidebar
- Adaptive chat layout
- Mobile drawer navigation

---

## Build

Create a production build:

```bash
npm run build
```

Run the production server:

```bash
npm start
```

---

## Deployment

Recommended platforms:

- Vercel
- Netlify

Before deployment, configure the following environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url
```

---

## Backend Integration

The frontend communicates with the backend through the following endpoints:

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/chat` | Send chat messages |
| GET | `/health` | Check backend availability |
| GET | `/health/ready` | Check backend readiness |

---

## License

MIT License