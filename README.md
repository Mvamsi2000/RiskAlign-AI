# RiskAlign‑AI
**Explainable, Compliance‑Driven Cyber Risk Decision Intelligence — with MCP interoperability**

[![Status](https://img.shields.io/badge/status-MVP%2B-blue)]()
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

## 🔌 API Surface (REST)
- `GET /health` → lightweight readiness probe
- `GET /api/findings/sample` → sample dataset used by the UI
- `POST /api/score/compute` → final scores + contributions + rules applied
- `POST /api/optimize/plan` → remediation waves by risk/effort ratio
- `POST /api/map/controls` → CVE → control mappings (CIS/NIST/ISO)
- `POST /api/impact/estimate` → breach $ and compliance % estimates
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
