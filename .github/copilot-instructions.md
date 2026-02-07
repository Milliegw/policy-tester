# Copilot Instructions

## Project Overview

This is the **Policy Tester Interface** — an AI-powered tool that red-teams draft government policies and guidelines against lived experience personas. It uses a local [Ollama](https://ollama.com/) instance for AI analysis. Built for the Justice AI Hackathon 2026.

The tool is domain-agnostic: it ships with parole policy personas as a worked example, but can test any policy area by swapping in different personas and example policies in `server/app.py`.

## Tech Stack

### Frontend (React)
- **React 18** (JavaScript/JSX — no TypeScript)
- **Vite 7** — dev server and build tool
- **Tailwind CSS 3** — utility-first styling
- **Lucide React** — icons

### Backend (Python)
- **FastAPI** — REST API server
- **Uvicorn** — ASGI server
- **Requests** — HTTP client for Ollama
- **Ollama** — local LLM inference via its REST API (`/api/chat`)

## Project Structure

```
src/
  App.jsx          # React UI — fetches data from Python backend
  main.jsx         # React entry point
  index.css        # Tailwind directives
server/
  app.py           # Python backend: personas, prompts, Ollama integration
  requirements.txt # Python dependencies
index.html         # HTML shell
vite.config.js     # Vite config with /api proxy to Python backend
```

### Architecture

The frontend is a thin React UI layer. All AI logic, personas, example policies, and prompt engineering live in the Python backend (`server/app.py`). Vite proxies `/api/*` requests to the FastAPI server during development.

```
Browser → Vite (localhost:5173) → /api/* proxy → FastAPI (localhost:8000) → Ollama (localhost:11434)
```

## Key Architecture Decisions

- **Python backend handles all AI logic** — Personas, prompt engineering, Ollama calls, and JSON parsing are all in `server/app.py`
- **React frontend is UI-only** — fetches personas and policies from the backend, displays results
- **Structured JSON output** — The Ollama request uses `format: "json"` and the system prompt instructs the model to return only valid JSON
- **Vite proxy** — `/api/*` requests are proxied to the Python backend to avoid CORS issues

## Coding Conventions

### Frontend (src/)
- Use **JSX** (`.jsx` files), not TypeScript
- Use **Tailwind CSS classes** for all styling — no separate CSS files beyond `index.css`
- Use **functional components** with React hooks (`useState`, `useEffect`)
- Use **ES module** syntax (`import`/`export`)
- Keep the GOV.UK-inspired blue colour: `bg-[#1d70b8]`

### Backend (server/)
- Use **Python 3.12+** with type hints
- Use **Pydantic** models for request/response validation
- Keep all personas and policies in `server/app.py` for simplicity

## Running the Project

```bash
# Prerequisites: Node.js 18+, Python 3.12+, Ollama running locally with a model pulled
ollama serve                                              # terminal 1
.venv/bin/python -m uvicorn server.app:app --port 8000    # terminal 2
npm run dev                                               # terminal 3 — opens at http://localhost:5173
```

## When Adding Features

- New **personas** go in the `PERSONAS` dict in `server/app.py`
- New **example policies** go in the `EXAMPLE_POLICIES` dict in `server/app.py`
- New **API endpoints** go in `server/app.py`
- New **UI components** go in `src/` as `.jsx` files
- The Ollama model is selectable via the settings panel in the header

## Security

- **All processing is local** — no data leaves the machine. See `SECURITY.md` for full details.
- **Never add external API calls** that transmit policy text off the machine
- **Never hard-code secrets** — use environment variables if needed
- **Validate all input** with Pydantic `Field` constraints on the backend
- **Ollama URL and model** are configurable via `OLLAMA_URL` and `OLLAMA_MODEL` environment variables
