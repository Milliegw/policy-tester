"""
Policy Tester Backend — FastAPI server that handles Ollama AI analysis.

All personas, prompt engineering, and Ollama integration live here in Python.
The React frontend just sends the policy text + selected categories and displays results.

The included personas cover parole policy as a worked example, but the tool is
designed to test any government policy or guidelines — swap in different personas
and example policies for other domains.
"""

import json
import os
import re

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ============================================================
# PERSONAS - Lived experience scenarios for policy testing
# ============================================================
# These represent real challenges people face when interacting with government
# systems. Each persona has a scenario and specific policy challenges derived
# from it. The included set covers parole policy as a worked example — replace
# or extend them for other policy domains.

PERSONAS = {
    "housing": {
        "id": "sarah-housing",
        "name": "Sarah",
        "category": "Housing & Release Planning",
        "scenario": (
            "Sarah, 38, serving 8 years, first parole hearing. Completed all offending "
            "behavior programs. Previous address no longer available - partner moved on. "
            "Applied to approved premises but told there's a 6-month wait. Cannot provide "
            "confirmed address for parole application. Parole Board policy requires confirmed "
            "address before release can be considered."
        ),
        "challenges": [
            "How does the Parole Board assess applications when housing isn't available through no fault of the prisoner?",
            "What weight is given to completion of rehabilitation programs vs. housing circumstances?",
            "Who is responsible for the gap between Parole Board requirements and approved premises availability?",
        ],
    },
    "employment": {
        "id": "dev-employment",
        "name": "Dev",
        "category": "Employment & Resettlement Plans",
        "scenario": (
            "Dev, 29, serving 6 years, eligible for parole. Has secured provisional job offer "
            "at distribution centre with rotating shifts. Parole Board guidance requires detailed "
            "employment plan including working hours. Employer cannot confirm exact shift pattern "
            "until he starts. Standard parole conditions include 7pm-7am curfew. Dev's application "
            "delayed twice awaiting 'adequate employment detail'."
        ),
        "challenges": [
            "How does the Parole Board assess employment plans when employers can't provide advance detail?",
            "How are potential conflicts between standard conditions (curfew) and employment assessed pre-release?",
            "What happens when release is delayed due to circumstances outside prisoner's control?",
        ],
    },
    "digital": {
        "id": "marcus-digital",
        "name": "Marcus",
        "category": "Digital Access & Hearing Preparation",
        "scenario": (
            "Marcus, 52, serving 12 years, first parole hearing in 6 months. Parole dossier now "
            "available digitally only. Marcus has limited computer access in prison (1 hour per week, "
            "shared terminal). Cannot download or save documents. Struggles to prepare case. Solicitor "
            "receives documents late. Hearing approaches with inadequate preparation time."
        ),
        "challenges": [
            "How does digital-first parole dossier policy account for limited prison IT access?",
            "What support is provided for prisoners with low digital literacy to engage with their case?",
            "How is adequate preparation time measured when access is constrained?",
        ],
    },
    "multiple": {
        "id": "jamal-multiple",
        "name": "Jamal",
        "category": "Multiple Barriers & Risk Assessment",
        "scenario": (
            "Jamal, 44, serving 10 years, third parole application. Has ADHD and literacy "
            "difficulties - completed programs but took longer and needed adaptations. No fixed "
            "address available. Previous applications refused citing 'insufficient evidence of risk "
            "reduction' and 'inadequate resettlement plan'. Parole Board risk assessment framework "
            "uses written reports and verbal hearing performance as primary evidence. Jamal struggles "
            "to articulate progress in hearing format."
        ),
        "challenges": [
            "How does the Parole Board's risk assessment account for neurodivergent communication styles?",
            "What adjustments are available for people with literacy difficulties in evidencing their progress?",
            "When multiple barriers intersect (housing, disability, communication), how is 'adequate resettlement plan' fairly assessed?",
        ],
    },
    "domesticAbuse": {
    "id": "amara-domestic",
    "name": "Amara",
    "category": "Domestic Abuse Survivor",
    "scenario": (
        "Amara, 34, reported domestic abuse after 4 years. English is her second language. "
        "Police attended but perpetrator was not arrested. She was not told about the Victims' Code or her right to support services. "
        "Three months later, she received a letter saying 'no further action' with no explanation. She fears reporting again because of concerns about immigration status - perpetrator has threatened to have her deported. "
        "She has since fled to a refuge but has no updates on whether she can safely return to her area."
    ),
    "challenges": [
        "How does the Code ensure victims understand their rights when English is not their first language?",
        "What explanation must be given when cases are discontinued?",
        "How are victims with insecure immigration status protected from perpetrator manipulation?",
        "What ongoing safety information is provided after 'no further action' decisions?"
    ],
    "source": "Based on Women's Aid, Refuge, and Victims' Commissioner research on BAME survivors"
    },

    "sexualViolence": {
        "id": "kate-sexual-violence",
        "name": "Kate",
        "category": "Sexual Violence Survivor",
        "scenario": (
            "Kate, now 19, reported sexual assault when she was 15. She was granted special measures as a child, including giving evidence via video link and screens in court. "
            "Her case was adjourned 3 times. By the time her trial date arrived, she was 18 and some special measures were withdrawn because she was now legally an adult. "
            "During cross-examination she faced questions about her clothing and alcohol consumption. She was not warned this would happen. She now has PTSD and says she regrets ever reporting."
        ),
        "challenges": [
            "How does the Code protect special measures when delays push child victims into adulthood?",
            "What information must victims receive about cross-examination practices?",
            "How are victims prepared for defence tactics including rape myths?",
            "What mental health support is guaranteed during multi-year waits?"
        ],
        "source": "Based on Victim Support 'Suffering for Justice' report (2024) case studies"
    },

    "disabled": {
        "id": "marcus-disabled",
        "name": "Marcus",
        "category": "Disabled Victim",
        "scenario": (
            "Marcus, 42, is Deaf and was assaulted. When police arrived, no BSL interpreter was available. Officers took a written statement but Marcus couldn't fully communicate the details. "
            "He was not informed of his right to request communication support. The case went to court but the courtroom had no hearing loop and no interpreter was arranged. "
            "Marcus struggled to follow proceedings. He was not offered a Registered Intermediary despite his communication needs. Afterwards, he wasn't told about the verdict for two weeks."
        ),
        "challenges": [
            "How does the Code ensure communication support is provided from first report onwards?",
            "What triggers automatic assessment for Registered Intermediary support?",
            "How are accessible courtroom requirements enforced?",
            "What timeframes apply to informing disabled victims of case outcomes?"
        ],
        "source": "Based on Victims' Commissioner disabled victims literature review and 2023 survey findings"
    },

    "child": {
        "id": "jayden-child",
        "name": "Jayden",
        "category": "Child Victim (via parent)",
        "scenario": (
            "Jayden, 9, witnessed domestic violence against his mother. Police interviewed him at the scene in front of other officers. "
            "His mother received a leaflet about the Victims' Code but Jayden received nothing age-appropriate explaining what would happen next. "
            "He has nightmares and stopped attending school. When the case went to court, no one explained to him what a trial was or that he might need to give evidence. "
            "His mother has tried to access support but was told the waiting list for children's services is 6 months."
        ),
        "challenges": [
            "How should child victims be interviewed to minimise trauma?",
            "What child-friendly materials must be provided about the justice process?",
            "How are child victims' views heard without requiring them to give formal evidence?",
            "What support service waiting times are acceptable for child victims?"
        ],
        "source": "Based on Victims' Commissioner and NSPCC research on child victims in CJS"
    },

    "older": {
        "id": "dorothy-older",
        "name": "Dorothy",
        "category": "Older Victim",
        "scenario": (
            "Dorothy, 78, was defrauded of her life savings by a phone scammer. She reported to the police who logged it as Action Fraud. "
            "Eight months later, she has heard nothing. She doesn't use email and wasn't offered alternative contact methods. She called the police station but couldn't get through. "
            "She has no smartphone to download the victims' support app. She feels embarrassed about being scammed and hasn't told her family. "
            "She wasn't referred to any support services or told she could make a Victim Personal Statement."
        ),
        "challenges": [
            "How does the Code ensure updates reach victims who don't use digital communication?",
            "What proactive referrals to support services should older victims receive?",
            "How are fraud victims - often older people - kept informed when cases sit with Action Fraud?",
            "What timeframes for updates apply regardless of crime type?"
        ],
        "source": "Based on Victims' Commissioner 2023 survey data on older victims and Older People's Commissioner for Wales research"
    }
}

# ============================================================
# EXAMPLE POLICIES - Draft policies for testing
# ============================================================

EXAMPLE_POLICIES = {
    "housing": {
        "title": "Housing Requirements Policy",
        "text": (
            "DRAFT POLICY: Parole Board Housing Requirements\n\n"
            "All parole applicants must provide a confirmed release address at least 28 days "
            "before their hearing date.\n\n"
            "The address must be verified as suitable by the probation service before the hearing "
            "can proceed.\n\n"
            "Applicants without a confirmed address will have their hearing deferred until suitable "
            "accommodation is secured.\n\n"
            "Approved premises applications should be submitted at least 12 weeks before the "
            "anticipated hearing date.\n\n"
            "The Parole Board will not consider release to temporary or emergency accommodation "
            "except in exceptional circumstances."
        ),
    },
    "curfew": {
        "title": "Standard Curfew Conditions",
        "text": (
            "DRAFT POLICY: Standard Curfew Conditions for Parole Licence\n\n"
            "All persons released on parole must comply with a 7pm-7am curfew for the first "
            "6 months of their licence period.\n\n"
            "Exceptions may be requested in writing with 48 hours notice to the supervising officer.\n\n"
            "Approval for curfew variations is subject to risk assessment and will be communicated "
            "within 5 working days.\n\n"
            "Breach of curfew conditions may result in recall to custody.\n\n"
            "The Parole Board will assess employment plans in the context of these standard conditions."
        ),
    },
    "digital": {
        "title": "Digital Parole Dossier Access",
        "text": (
            "DRAFT POLICY: Digital Access to Parole Dossiers\n\n"
            "All parole dossiers will be made available through the digital portal system.\n\n"
            "Prisoners will be notified when their dossier is available and must access it through "
            "prison computer facilities.\n\n"
            "IT support sessions are available on request, subject to prison resources and scheduling.\n\n"
            "Paper copies will only be provided in exceptional circumstances with prior approval "
            "from the Parole Board secretariat.\n\n"
            "Prisoners are expected to review their dossier and submit any representations within "
            "21 days of notification."
        ),
    },
    "victims_code": {
    "title": "Draft Victims' Code: Communication Standards",
    "text": (
        "DRAFT POLICY: Victims' Code - Right to Information\n\n"
        "Victims have the right to receive information about their case.\n\n"
        "Police must provide an initial update within 5 working days of reporting a crime.\n\n"
        "If there is no significant development, victims should receive an update at least every 28 days.\n\n"
        "When a decision is made to discontinue a case, victims must be informed within 5 working days.\n\n"
        "Victims aged 12 and above may receive direct contact from police and probation alongside their parent or guardian.\n\n"
        "Information will be provided digitally via the Victim Information Portal unless the victim requests an alternative format.\n\n"
        "Translation services are available on request.\n\n"
        "Child victims will be provided with age-appropriate information materials."
        ),
    },
}

# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
MAX_RESPONSE_BYTES = 512_000  # 500 KB — reject abnormally large LLM responses

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="Policy Tester API")


# ---- Request / Response models ----

class TestPolicyRequest(BaseModel):
    policy_text: str = Field(..., min_length=1, max_length=50_000)
    categories: list[str] = Field(..., min_length=1)
    model: str | None = Field(default=None, max_length=200)


class StatusResponse(BaseModel):
    connected: bool
    models: list[str]
    default_model: str


# ---- Helper functions ----

def build_prompt(policy_text: str, categories: list[str]) -> tuple[str, str]:
    """Build the system and user prompts for the Ollama call."""

    selected_personas = [PERSONAS[cat] for cat in categories if cat in PERSONAS]
    if not selected_personas:
        raise ValueError("No valid categories selected")

    personas_text = "\n\n---\n\n".join(
        f"{p['name']} - {p['category']}:\n{p['scenario']}\n\n"
        f"Key challenges:\n" + "\n".join(f"- {c}" for c in p["challenges"])
        for p in selected_personas
    )

    system_prompt = (
        "You are a policy analyst testing draft government policies and guidelines "
        "against lived experience scenarios from people who will be affected by them.\n\n"
        "Your role is to identify:\n"
        "- CONFLICTS: Where policy requirements create impossible situations or clash with real-world constraints\n"
        "- GAPS: What the policy doesn't address but needs to\n"
        "- UNINTENDED_CONSEQUENCES: How the policy might create barriers or cause harm to the people affected\n"
        "- STRENGTHS: Where the policy aligns well with needs and fair process\n\n"
        "Be specific, cite the persona scenarios, and provide actionable recommendations.\n"
        "You MUST respond with ONLY valid JSON, no other text."
    )

    user_prompt = (
        f"Policy to test:\n{policy_text}\n\n"
        f"Test this policy against these lived experience scenarios:\n\n{personas_text}\n\n"
        "Analyze how this policy would impact each person. "
        "For each persona, identify any conflicts, gaps, unintended consequences, or strengths.\n\n"
        'Respond with ONLY this JSON format, no other text:\n'
        '{\n'
        '  "results": [\n'
        '    {\n'
        '      "persona": "persona name",\n'
        '      "category": "category name",\n'
        '      "status": "CONFLICT" | "GAP" | "UNINTENDED_CONSEQUENCE" | "STRENGTH",\n'
        '      "issue": "brief one-line issue description",\n'
        '      "explanation": "detailed explanation of the problem or strength",\n'
        '      "recommendation": "specific actionable recommendation for policy revision"\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    return system_prompt, user_prompt


def call_ollama(system_prompt: str, user_prompt: str, model: str) -> list[dict]:
    """Send prompts to Ollama and parse the JSON response."""

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        },
        timeout=300,  # LLMs can be slow
    )
    response.raise_for_status()

    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("Ollama response exceeded size limit")

    data = response.json()
    content = data.get("message", {}).get("content", "")

    # Parse JSON from response (model might wrap it in extra text)
    json_match = re.search(r"\{[\s\S]*\}", content)
    if not json_match:
        raise ValueError(f"Could not parse JSON from model response: {content[:200]}")

    parsed = json.loads(json_match.group())
    return parsed.get("results", [])


# ---- API endpoints ----

@app.get("/api/status")
def get_status() -> StatusResponse:
    """Check Ollama connection and list available models."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return StatusResponse(
            connected=True,
            models=models,
            default_model=models[0] if models else DEFAULT_MODEL,
        )
    except Exception:
        return StatusResponse(connected=False, models=[], default_model=DEFAULT_MODEL)


@app.get("/api/personas")
def get_personas() -> dict:
    """Return all personas so the frontend can display them."""
    return PERSONAS


@app.get("/api/example-policies")
def get_example_policies() -> dict:
    """Return all example policies."""
    return EXAMPLE_POLICIES


@app.post("/api/test-policy")
def test_policy(request: TestPolicyRequest) -> dict:
    """Test a policy against selected personas using Ollama."""

    if not request.policy_text.strip():
        raise HTTPException(status_code=400, detail="Policy text is required")

    if not request.categories:
        raise HTTPException(status_code=400, detail="At least one category is required")

    invalid = [c for c in request.categories if c not in PERSONAS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid categories: {invalid}")

    model = request.model or DEFAULT_MODEL

    try:
        system_prompt, user_prompt = build_prompt(request.policy_text, request.categories)
        results = call_ollama(system_prompt, user_prompt, model)
        return {"results": results}
    except requests.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to Ollama. Is it running?")
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Ollama request timed out")
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
