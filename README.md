# Policy Tester Interface

An AI-powered tool to red-team draft parole policies against lived experience personas. Built at the Justice AI Hackathon 2026.

> **All AI processing runs locally via [Ollama](https://ollama.com/) — no data leaves your machine.**

## What it does

This tool tests draft policy documents against realistic scenarios representing people going through the parole process. It uses a local LLM to identify:

- **Conflicts** — where policy requirements create impossible situations
- **Gaps** — what the policy doesn't address but needs to
- **Unintended consequences** — how the policy might create barriers to fair assessment
- **Strengths** — where the policy aligns well with needs

## Why it matters

Policies are often drafted without input from people who will be affected by them. This tool embeds lived experience perspectives into the policy review process, surfacing unintended consequences before policies are implemented.

For example, a standard curfew policy (7pm–7am) might seem reasonable, but when tested against Dev's scenario (a shift worker whose job requires rotating hours), the tool identifies that this policy forces people to choose between employment and compliance — exactly the kind of barrier that increases reoffending risk.

## The personas

The tool includes four personas representing different challenges:

| Persona | Category | Key Challenge |
|---------|----------|---------------|
| Sarah | Housing & Release Planning | Can't provide confirmed address due to approved premises waiting lists |
| Dev | Employment & Resettlement | Employer can't confirm shift patterns; curfew conflicts with work |
| Marcus | Digital Access | Limited computer access in prison; can't prepare for hearing |
| Jamal | Multiple Barriers | ADHD + literacy difficulties; struggles to evidence progress |

These are fictional composites inspired by documented systemic barriers — not real individuals.

---

## Quick start

### 1. Prerequisites

| Requirement | Version | Install |
|---|---|---|
| **Node.js** | 18 + | [nodejs.org](https://nodejs.org/) |
| **Python** | 3.12 + | [python.org](https://www.python.org/) |
| **Ollama** | latest | [ollama.com](https://ollama.com/) |

### 2. Install dependencies

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/parole-policy-tester.git
cd parole-policy-tester

# Frontend
npm install

# Backend
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows
pip install -r server/requirements.txt
```

### 3. Pull an Ollama model

```bash
ollama pull llama3
```

You can use any model Ollama supports — select it in the app's settings panel. Larger models (e.g. `llama3:70b`, `mixtral`) give richer analysis but are slower.

### 4. Start the three services

You need **three terminals** running at the same time:

```bash
# Terminal 1 — Ollama
ollama serve
```

```bash
# Terminal 2 — Python backend (port 8000)
source .venv/bin/activate
python -m uvicorn server.app:app --port 8000
```

```bash
# Terminal 3 — Vite dev server (port 5173)
npm run dev
```

### 5. Open the app

Go to **http://localhost:5173** in your browser.

The header shows a green "Ollama" badge when everything is connected. If it shows red, check that all three services are running.

### Using the tool

1. **Check the status** — the header badge should show green with the model name
2. **Load a policy** — click an example policy button, or paste your own draft text
3. **Choose personas** — tick/untick the personas you want to test against
4. **Click "Test Policy"** — analysis takes 15–60 seconds depending on model size
5. **Review results** — expand each finding card to see the full explanation and recommendation

---

## Technical architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                   │
│  - Policy text input                                        │
│  - Persona selection                                        │
│  - Results display with expandable cards                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ /api/* proxy (Vite dev server)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Backend (FastAPI)                     │
│  - Personas & example policies                              │
│  - Prompt engineering                                       │
│  - Ollama integration & JSON parsing                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (localhost only)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Ollama (local LLM)                        │
│  - Structured JSON output via /api/chat                     │
└─────────────────────────────────────────────────────────────┘
```

### Key code sections (for interview discussion)

**1. Persona structure** (`server/app.py`)
- Each persona has: id, name, category, scenario text, and derived challenge questions
- Scenarios are detailed enough to surface specific policy conflicts

**2. Prompt engineering** (`server/app.py` — `build_prompt()`)
- System prompt sets the model's role as a policy analyst
- User prompt combines policy text with formatted persona scenarios
- Output is structured as JSON for reliable parsing

**3. API integration** (`server/app.py` — `call_ollama()`)
- Calls local Ollama instance via its REST API (`/api/chat`)
- Uses `format: "json"` to request structured JSON output
- Extracts JSON from response for display

## Project structure

```
parole-policy-tester/
├── src/
│   ├── App.jsx          # React UI — fetches data from Python backend
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind CSS imports
├── server/
│   ├── app.py           # Python backend: personas, prompts, Ollama integration
│   └── requirements.txt # Python dependencies
├── index.html           # HTML template
├── package.json         # Frontend dependencies
├── vite.config.js       # Vite config with /api proxy to Python backend
├── tailwind.config.js   # Tailwind configuration
├── postcss.config.js    # PostCSS configuration
└── README.md            # This file
```

## Security & privacy

- **No cloud APIs** — all AI inference runs locally via Ollama; no data is sent to external services
- **No authentication** — the app is designed to run on `localhost` only and does not expose any login or user data
- **No persistent storage** — nothing is written to disk; results exist only in browser memory for the current session
- **No secrets in the repo** — there are no API keys, tokens, or credentials anywhere in the codebase
- See [SECURITY.md](SECURITY.md) for the full security policy

## Potential extensions

- **Larger models**: Use a more capable Ollama model for better analysis (e.g. `llama3:70b`, `mixtral`)
- **More personas**: Add scenarios for mental health, family ties, immigration status
- **Policy database**: Save and compare policy versions over time
- **User group validation**: Let affected communities validate and refine personas
- **Export reports**: Generate PDF reports for policy teams

## Built with

- [React 18](https://react.dev/) — UI framework
- [Vite 7](https://vitejs.dev/) — build tool & dev server
- [Tailwind CSS 3](https://tailwindcss.com/) — utility-first styling
- [FastAPI](https://fastapi.tiangolo.com/) — Python REST API backend
- [Ollama](https://ollama.com/) — local LLM inference
- [Lucide React](https://lucide.dev/) — icons

## Hackathon context

This was built at the Justice AI Hackathon 2026, exploring how AI can improve policy-making by embedding perspectives that are often excluded from the process. The parole system was chosen because:

1. Policies directly affect people's liberty
2. Those affected rarely have input into policy design
3. Unintended consequences can increase reoffending risk
4. Small policy changes can have large real-world impacts

## Contributing

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the list of contributors.

Contributions are welcome! Please open an issue or pull request.

## License

MIT
