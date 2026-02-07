# Security Policy

## Overview

The Policy Tester Interface is designed to run **entirely on localhost**. All AI inference is handled by a local [Ollama](https://ollama.com/) instance — no policy text or analysis results are sent to any external service.

## Architecture & threat model

| Component | Listens on | Exposed to internet? |
|---|---|---|
| Vite dev server | `localhost:5173` | No |
| FastAPI backend | `localhost:8000` | No |
| Ollama | `localhost:11434` | No |

The application has **no authentication, no user accounts, and no persistent storage**. It is intended for local, single-user use during policy workshops or individual analysis.

### What this means

- **Policy text you enter stays on your machine.** It is sent from the browser to the local FastAPI server, then to Ollama — all over `localhost`.
- **Results are held in browser memory only** and are lost when you close or refresh the tab.
- **No telemetry or analytics** are collected.

## Security considerations for contributors

### Do NOT

- Add external API calls that transmit policy text or results off the machine
- Add authentication or user management without a full threat model review
- Hard-code secrets, API keys, or tokens anywhere in the codebase
- Add persistent storage of policy text or results without considering data protection implications
- Expose any service on `0.0.0.0` — all services must bind to `localhost` only

### Do

- Keep all AI processing local via Ollama
- Validate and sanitise all user input on the backend (FastAPI/Pydantic)
- Pin dependency versions in `requirements.txt` and `package.json`
- Run `npm audit` and `pip audit` periodically to check for known vulnerabilities

## Input validation

- **Frontend**: Basic checks before sending requests (non-empty policy text, at least one category selected)
- **Backend**: Pydantic model validation on all API requests; invalid categories are rejected with a 400 error; empty policy text is rejected

## Dependency security

| Ecosystem | Lock file | Audit command |
|---|---|---|
| Node.js | `package-lock.json` | `npm audit` |
| Python | `requirements.txt` | `pip audit` (install via `pip install pip-audit`) |

## Known limitations

1. **No rate limiting** — the FastAPI server does not limit request frequency. This is acceptable for localhost use but would need to be addressed before any network deployment.
2. **No HTTPS** — all traffic is over plain HTTP on localhost. Do not expose these services to a network without adding TLS.
3. **No Content Security Policy** — the Vite dev server does not set CSP headers. The production build should add appropriate headers if deployed.
4. **LLM output is not sanitised for XSS** — model responses are rendered as text in React (which escapes HTML by default), but if the rendering changes to use `dangerouslySetInnerHTML`, output sanitisation would be required.

## Reporting a vulnerability

If you find a security issue, please open a GitHub issue or contact the maintainers directly. This is a hackathon project and does not have a formal security response process.
