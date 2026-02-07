# Policy Tester Interface

An AI-powered tool that red-teams draft government policies and guidelines against lived experience personas. Paste any policy — housing, benefits, healthcare, justice, education, immigration — and the tool surfaces conflicts, gaps, and unintended consequences before real people are affected.

Built at the Justice AI Hackathon 2026.

> **All AI processing runs locally via [Ollama](https://ollama.com/) — no data leaves your machine.**

## What it does

You give the tool a draft policy document and a set of personas representing people who will be affected by it. A local LLM analyses the policy through each persona's lens and returns structured findings:

- **Conflicts** — where policy requirements create impossible situations
- **Gaps** — what the policy doesn't address but needs to
- **Unintended consequences** — how the policy might create barriers or harm
- **Strengths** — where the policy aligns well with people's real needs

## Why it matters

Policies are often drafted without input from the people who will be affected by them. This tool embeds lived experience perspectives into the review process, surfacing unintended consequences before policies are implemented.

For example, a standard curfew condition (7pm–7am) might seem reasonable, but when tested against a shift worker's scenario, the tool identifies that it forces people to choose between employment and compliance — exactly the kind of barrier that leads to worse outcomes.

The tool ships with **parole policy personas** as a worked example, but the approach works for any domain where policy interacts with people's lives.

## Included example: parole policy personas

The tool ships with four personas representing different challenges faced during the parole process. These serve as a ready-to-use demonstration and can be replaced or extended for any policy domain.

| Persona | Category | Key Challenge |
|---------|----------|---------------|
| Sarah | Housing & Release Planning | Can't provide confirmed address due to approved premises waiting lists |
| Dev | Employment & Resettlement | Employer can't confirm shift patterns; curfew conflicts with work |
| Marcus | Digital Access | Limited computer access in prison; can't prepare for hearing |
| Jamal | Multiple Barriers | ADHD + literacy difficulties; struggles to evidence progress |

These are fictional composites inspired by documented systemic barriers — not real individuals.

### Adapting to other policy domains

To test a different kind of policy, replace the personas and example policies in `server/app.py`. For instance:

- **Benefits policy** — personas representing carers, people with fluctuating conditions, gig workers
- **Healthcare access** — personas representing rural residents, non-English speakers, shift workers
- **Education** — personas representing mature students, parents, people with disabilities
- **Immigration** — personas representing asylum seekers, visa workers, undocumented individuals

The prompt engineering in `build_prompt()` is domain-agnostic — it will adapt its analysis to whatever personas and policy text you provide.

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
git clone https://github.com/Milliegw/policy-tester.git
cd policy-tester

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
- Personas are domain-agnostic — swap them out for any policy area

**2. Prompt engineering** (`server/app.py` — `build_prompt()`)
- System prompt sets the model's role as a policy analyst
- User prompt combines policy text with formatted persona scenarios
- The prompt adapts to whatever persona content is provided
- Output is structured as JSON for reliable parsing

**3. API integration** (`server/app.py` — `call_ollama()`)
- Calls local Ollama instance via its REST API (`/api/chat`)
- Uses `format: "json"` to request structured JSON output
- Extracts JSON from response for display

## Project structure

```
policy-tester/
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
├── SECURITY.md          # Security policy
├── CONTRIBUTORS.md      # Contributors list
└── README.md            # This file
```

## Security & privacy

- **No cloud APIs** — all AI inference runs locally via Ollama; no data is sent to external services
- **No authentication** — the app is designed to run on `localhost` only and does not expose any login or user data
- **No persistent storage** — nothing is written to disk; results exist only in browser memory for the current session
- **No secrets in the repo** — there are no API keys, tokens, or credentials anywhere in the codebase
- See [SECURITY.md](SECURITY.md) for the full security policy

## Potential extensions

- **More policy domains**: Add persona sets for benefits, healthcare, education, immigration
- **Larger models**: Use a more capable Ollama model for better analysis (e.g. `llama3:70b`, `mixtral`)
- **Policy database**: Save and compare policy versions over time
- **User group validation**: Let affected communities validate and refine personas
- **Export reports**: Generate PDF reports for policy teams
- **Persona editor**: Let users create and save custom personas in the UI

## Built with

- [React 18](https://react.dev/) — UI framework
- [Vite 7](https://vitejs.dev/) — build tool & dev server
- [Tailwind CSS 3](https://tailwindcss.com/) — utility-first styling
- [FastAPI](https://fastapi.tiangolo.com/) — Python REST API backend
- [Ollama](https://ollama.com/) — local LLM inference
- [Lucide React](https://lucide.dev/) — icons

## Hackathon context

This was built at the Justice AI Hackathon 2026, exploring how AI can improve policy-making by embedding perspectives that are often excluded from the process. The parole system was chosen as the initial worked example because:

1. Policies directly affect people's liberty
2. Those affected rarely have input into policy design
3. Unintended consequences can increase reoffending risk
4. Small policy changes can have large real-world impacts

The same approach applies to any area of government policy where the people affected have limited voice in the drafting process.

## Contributing

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the list of contributors.

Contributions are welcome! Please open an issue or pull request.

## License

MIT
