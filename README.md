# RiskAlign‑AI
**Explainable, Compliance‑Driven Cyber Risk Decision Intelligence — with MCP interoperability**

[![Status](https://img.shields.io/badge/status-MVP%2B-blue)]()
[![CI](https://img.shields.io/badge/ci-github--actions-lightgrey)]()
[![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20MCP%20%7C%20OpenAI-green)]()
[![License](https://img.shields.io/badge/license-Proprietary%20Portfolio-red)]()

RiskAlign‑AI turns raw vulnerability data into **actionable, business‑aligned decisions**. It blends:
- **Optimization** (what to fix first for maximum risk reduction per hour),
- **Governance** (instant mapping to **NIST / ISO / CIS** controls), and
- **Explainability** (clear narratives & contribution heatmaps for engineers, CISOs, and boards).

Every capability is also exposed as **MCP tools**, so your security copilots and agents can plug in with zero custom glue.

---

## ✨ Highlights
- **Risk‑to‑Cost Optimizer** — Prioritized remediation *waves* balancing risk reduction vs. effort/SLA.
- **Compliance Mapper** — CVE → control coverage for **NIST 800‑53, ISO 27001, CIS Controls**.
- **Explainable Narratives** — Plain‑English risk stories and contribution heatmaps (CVSS/EPSS/KEV/context/rules).
- **Business Impact Analytics** — Breach‑cost estimates ($) and compliance‑gain (%).
- **Executive Summary Generator** — One‑page, C‑suite‑ready HTML/PDF summary.
- **Adaptive Prioritization** — Lightweight learning from analyst feedback (no heavy training required).
- **Natural‑Language Copilot** — “Quick wins under 10 hours?” → actionable answers via intent routing.
- **MCP Interop** — Tools callable from MCP‑aware clients (Claude Desktop, VS Code agents, etc.).

---

## 🧭 Why Now
- **2025 reality:** AI‑assisted attacks are up, regulation and board scrutiny are rising, and teams need *decisions*, not dashboards.
- RiskAlign‑AI focuses on **decision intelligence**: optimize actions, align with controls, explain the “why” — and integrate with the AI ecosystem via MCP.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────── UI / UX ───────────────────────────────┐
│ React (Vite)                                                          │
│  • Plan (waves)   • Compliance   • Narratives   • Copilot (NL query)  │
└───────────────────────────────▲───────────────▲───────────────────────┘
                                │               │
                     REST / JSON│               │MCP (tools)
                                │               │
┌───────────────────────────────┴───────────────┴───────────────────────┐
│ FastAPI Backend                                                     │▕ │
│  • scoring.py  → score_compute() + explain()                        │▕ │
│  • optimizer.py→ optimize_plan() (greedy/OR‑Tools ready)            │▕ │
│  • impact.py   → breach $ & compliance %                            │▕ │
│  • mapping.py  → CVE → controls                                     │▕ │
│  • nl_router.py→ natural‑language intent → tools                    │▕ │
│  • feedback.py → adaptive weight nudges                             │▕ │
│  • templates/  → executive summary HTML                             │▕ │
└───────────────────────────────▲───────────────────────────────────────┘
                                │
                                │
┌───────────────────────────────┴───────────────────────────────────────┐
│               MCP Server (same process or sidecar)                    │
│  Tools:                                                               │
│   • optimize_plan(findings, constraints?) -> plan                     │
│   • score_compute(findings, config?) -> scored_findings[]             │
│   • map_to_controls(cves[], standard, version?) -> mappings           │
│   • explain_finding(finding_id) -> breakdown                          │
│   • impact_estimate(findings) -> {breach_$, compliance_%}             │
│   • nl_query(query) -> routed_result                                  │
│   • feedback_submit(finding_id, action) -> ack                        │
│   • summary_generate(scope) -> html                                   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**, **Node.js 18+**
- OpenAI API key (for summaries/narratives) — optional to boot the UI
- (Optional) MCP‑aware client if you want to call tools directly

### 1) Clone
```bash
git clone https://github.com/<your-username>/riskalign-ai.git
cd riskalign-ai
```

### 2) Backend
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

### 3) Frontend
```bash
cd ../client
npm install
npm run dev
```
Open `http://localhost:5173`

> **Tip:** The workspace auto-loads `server/data/sample_findings.json`. Adjust the wave capacity in the header to see plan/compliance/narrative views update instantly.

---

## ⚙️ Configuration (MVP defaults)
- `server/config/scoring.json` — weights & rule DSL (add/mult/min_priority)
- `server/config/controls_cis.json` — CVE → CIS mappings (extendable to NIST/ISO)
- `server/data/sample_findings.json` — demo dataset (5–10 findings)

**Priority Buckets (default):**
- 9.0–10.0 = Critical, 7.0–8.99 = High, 4.0–6.99 = Medium, else Low

**Signals used:** CVSS base, **EPSS**, **KEV**, vendor index (if present)
**Context used:** asset criticality, exposure, data sensitivity, SLA/effort

---

## 🤖 AI Modes (Local vs Online)
- **Default = Local (Ollama):** the backend uses a local Ollama service for narratives/explanations. Launch Ollama and pull the model once:

  ```bash
  ollama pull llama3:8b
  ollama run llama3:8b --keep-alive
  ```

- **Online (OpenAI):** set `OPENAI_API_KEY` and switch via the UI dropdown (header → “AI mode”). The client persists the choice and sends `X-AI-Provider` on every API call.
- **Per-tenant override:** POST a config with an admin key to save `config/namespaces/<namespace>/ai.json`.

  ```bash
  curl -X POST "http://localhost:8000/api/ai/config" \
    -H "Content-Type: application/json" \
    -H "X-Admin-Key: <your-admin-key>" \
    -H "X-Namespace: demo" \
    -d '{"ai_provider":"online"}'
  ```

- **Env toggles:** `.env.example` lists `AI_PROVIDER_DEFAULT`, base URLs/models, and feature flags (`AI_NARRATIVE_ENABLED`, `AI_SCORING_ENABLED`).

If the selected provider is unavailable the UI surfaces a toast with guidance to switch modes.

---

## 🔌 API Surface (REST)
- `GET /health` → lightweight readiness probe
- `GET /api/findings/sample` → sample dataset used by the UI
- `POST /api/score/compute` → final scores + contributions + effort totals
- `POST /api/optimize/plan` → remediation waves by risk/effort ratio
- `POST /api/map/controls` → CVE → control mappings (CIS/NIST/ISO)
- `POST /api/impact/estimate` → readiness %, risk curve, and compliance boost
- `POST /api/summary/generate` → one-page HTML summary
- `POST /api/nl/query` → natural-language intent → tool calls
- `POST /api/feedback/submit` → log analyst feedback for adaptive weights
- `GET /api/feedback/recent` → retrieve the latest analyst responses

---

## 🧪 Demo Flow (5 minutes)
1. **Upload** `sample_findings.json` → see scores & priorities.
2. Open **Plan** tab → Wave 1 with hours & expected risk reduction.
3. Open **Compliance** → control coverage & top gaps.
4. Click **Generate Summary** → copy HTML/PDF for execs.
5. Ask **Copilot**: “Which quick wins under 10h improve CIS coverage most?”
6. Hit **Agree/Disagree** on an item → watch weights nudge subtly (logged).

---

## 🧩 Roadmap (public)
**Near‑term**
- Threat‑intel fusion (CISA KEV/exploit feeds) for live exploitability boosts.
- Attack‑path visuals (MITRE ATT&CK) for contextual risk.
- Persona‑aware narratives (Board / CISO / Engineer).

**Mid‑term**
- SBOM & license risk (SPDX/CycloneDX) — software supply chain view.
- Audit‑pack generator (evidence binder + checksum).

**Long‑term**
- Predictive risk forecasting (Monte Carlo) & budget planning.
- SIEM/SOAR connectors for closed‑loop remediation.

---

## 🔐 Security & Privacy Notes
- No production secrets required for MVP; summaries can be disabled.
- Keep client data local by default; MCP calls remain deterministic JSON I/O.
- Add your DLP/PII redaction layer before ingesting sensitive datasets.

---

## 📣 Positioning (for recruiters & stakeholders)
- **Decision intelligence over dashboards:** optimizes *actions* not just *scores*.
- **Compliance‑first mapping** to industry frameworks.
- **Explainability by design:** contribution heatmaps & narratives.
- **Ecosystem‑ready:** MCP tools for copilots and agent workflows.

> *“RiskAlign‑AI helps teams explain **what to fix, why it matters, and how it improves governance** — in minutes.”*

---

## 🤝 Contributing
PRs welcome for: new control mappings, rule examples, sample datasets, charts.  
Please open an issue first to align on scope.

---

## ⚠️ License & Usage Notice
This repository is released under a **Proprietary Portfolio License**.
It is provided for **demonstration and portfolio purposes only**.

- ❌ You may **not** use, copy, modify, or distribute this code.
- ❌ You may **not** incorporate it into production systems or commercial projects.
- ✅ You may **view** and **reference** the repository as an example of the author’s work.

For any other usage, **explicit written consent** from the author is required.

---

## 🧾 Credits
Built with **FastAPI • React • Model Context Protocol • OpenAI**  
© 2025 Vamsi Kalyan Reddy Mure. All rights reserved.
### `POST /api/score/compute`

  Compute weighted risk scores for a batch of findings. The endpoint blends CVSS, EPSS, machine vulnerability importance (MVI),
  KEV boosts, and context multipliers from `server/config/scoring.json`. Totals include combined hours and average score for
  quick prioritisation.

  **Request body**

  ```json
  {
    "findings": [
      {
        "id": "F-1",
        "title": "Example CVE",
        "cvss": 8.0,
        "epss": 0.2,
        "mvi": 6.0,
        "kev": true,
        "effort_hours": 4,
        "asset": {
          "name": "api-gateway",
          "criticality": "high",
          "exposure": "internet",
          "data_sensitivity": "pii"
        }
      }
    ]
  }
  ```

  **Response body**

  ```json
  {
    "findings": [
      {
        "id": "F-1",
        "title": "Example CVE",
        "score": 7.04,
        "priority": "High",
        "effort_hours": 4.0,
        "components": {
          "cvss": 4.8,
          "epss": 0.5,
          "mvi": 0.6,
          "kev": 1.0,
          "context": 0.14
        },
        "context_multiplier": 1.39
      }
    ],
    "totals": {
      "count": 1,
      "total_score": 7.04,
      "average_score": 7.04,
      "total_effort_hours": 4.0,
      "by_priority": {
        "High": 1
      }
    }
  }
  ```

### `POST /api/optimize/plan`

  Build remediation waves using a greedy risk-per-hour heuristic. Findings are scored (unless supplied) and sorted by expected
  risk saved per hour before filling waves within the `max_hours_per_wave` budget.

  **Request body**

  ```json
  {
    "max_hours_per_wave": 8,
    "findings": [
      { "id": "F-1", "cvss": 9.0, "epss": 0.3, "mvi": 8.0, "kev": true, "effort_hours": 6.0 },
      { "id": "F-2", "cvss": 7.0, "epss": 0.1, "mvi": 5.0, "kev": false, "effort_hours": 5.0 }
    ]
  }
  ```

  **Response body**

  ```json
  {
    "waves": [
      {
        "name": "Wave 1",
        "total_hours": 6.0,
        "risk_saved": 9.0,
        "items": [
          { "id": "F-1", "score": 8.18, "risk_saved": 9.0, "effort_hours": 6.0, "priority": "High" }
        ]
      },
      {
        "name": "Wave 2",
        "total_hours": 5.0,
        "risk_saved": 5.0,
        "items": [
          { "id": "F-2", "score": 5.0, "risk_saved": 5.0, "effort_hours": 5.0, "priority": "Medium" }
        ]
      }
    ],
    "totals": {
      "waves": 2,
      "total_hours": 11.0,
      "total_risk_saved": 14.0
    }
  }
  ```
### `POST /api/impact/estimate`

  Convert remediation waves into program-level impact metrics. Provide the original findings (with CVEs) alongside the optimizer
  output to receive readiness percent, cumulative risk saved per wave, and a projected compliance boost based on CIS mappings.

  **Request body**

  ```json
  {
    "findings": [
      { "id": "F-1", "cve": "CVE-2023-12345", "cvss": 9.0, "epss": 0.3, "mvi": 8.0, "kev": true, "effort_hours": 6.0 },
      { "id": "F-2", "cve": "CVE-2024-9876", "cvss": 7.0, "epss": 0.1, "mvi": 5.0, "kev": false, "effort_hours": 5.0 }
    ],
    "waves": [
      {
        "name": "Wave 1",
        "total_hours": 6.0,
        "risk_saved": 9.0,
        "items": [
          { "id": "F-1", "score": 8.18, "risk_saved": 9.0, "effort_hours": 6.0, "priority": "High" }
        ]
      }
    ]
  }
  ```

  **Response body**

  ```json
  {
    "readiness_percent": 48.0,
    "risk_saved_curve": [
      { "wave": "Wave 1", "cumulative_risk_saved": 9.0, "percent_of_total": 100.0 }
    ],
    "compliance_boost": 27.6,
    "controls_covered": ["CIS 4.1", "CIS 6.2", "CIS 7.6"]
  }
  ```
### `POST /api/map/controls`

  Translate CVEs to CIS Controls coverage. Supply findings (with CVEs) to receive the controls touched, coverage percentage, and
  any unmapped vulnerabilities.

  **Request body**

  ```json
  {
    "framework": "CIS",
    "findings": [
      { "id": "F-1", "cve": "CVE-2023-12345" },
      { "id": "F-2", "cve": "CVE-2024-9876" }
    ]
  }
  ```

  **Response body**

  ```json
  {
    "framework": "CIS",
    "coverage": 100.0,
    "unique_controls": ["CIS 4.1", "CIS 6.2", "CIS 7.6"],
    "mappings": [
      { "cve": "CVE-2023-12345", "control": "CIS 4.1", "description": "Establish and Maintain a Secure Configuration Process", "finding_id": "F-1" }
    ],
    "unmapped": []
  }
  ```
### `POST /api/summary/generate`

  Produce a printable HTML report that stitches together scoring, optimization, impact, and control coverage. The rendered file is
  saved under `server/output/summary-<timestamp>.html` and the HTML is also returned in the response.

  **Request body**

  ```json
  {
    "scope": "pilot",
    "framework": "CIS",
    "findings": [
      { "id": "F-1", "cve": "CVE-2023-12345", "cvss": 9.0, "epss": 0.3, "mvi": 8.0, "kev": true, "effort_hours": 6.0 }
    ]
  }
  ```

  **Response body**

  ```json
  {
    "path": "server/output/summary-20250101120000.html",
    "html": "<!DOCTYPE html>...RiskAlign-AI Summary..."
  }
  ```
### `POST /api/nl/query`

  Lightweight natural-language router for the backend capabilities. Returns the inferred intent, matched keywords, and the
  recommended REST endpoint.

  ```json
  {
    "query": "Plan remediation waves for this sprint"
  }
  ```

  **Response**

  ```json
  {
    "intent": "plan",
    "response": "I'll build remediation waves based on risk saved per hour.",
    "details": {
      "matched_keywords": ["plan", "wave"],
      "confidence": 0.4,
      "endpoint": "/api/optimize/plan"
    }
  }
  ```

### `POST /api/feedback/submit`

  Append analyst feedback to `server/output/feedback/` as JSONL for lightweight learning loops.

  ```json
  {
    "finding_id": "F-1",
    "action": "agree",
    "comment": "High exposure, please expedite"
  }
  ```

  **Response**

  ```json
  {
    "status": "recorded",
    "path": "server/output/feedback/feedback-20250101.jsonl",
    "recorded_at": "2025-01-01T12:00:00+00:00"
  }
  ```

## 🐳 Docker quick start

1. Build the images:
   ```bash
   docker compose build
   ```
2. Start both services:
   ```bash
   docker compose up
   ```
3. Open http://localhost:4173 for the web UI. API available at http://localhost:8000.

The compose stack mounts `server/output/` so generated summaries and feedback logs persist on the host.
