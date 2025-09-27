# RiskAlign-AI

RiskAlign-AI is an **AI-driven Cybersecurity Decision Intelligence platform** designed to transform vulnerability data into business-aligned insights. It combines vulnerability scoring, compliance mapping, and explainable narratives into a single, modular system. Built with **FastAPI, React, and the Model Context Protocol (MCP)**, RiskAlign-AI helps security teams prioritize what matters most, communicate effectively with all stakeholders, and integrate seamlessly with the growing AI ecosystem.

---

## 🔑 Key Features

- **Risk-to-Cost Optimizer**: Generates remediation plans that balance risk reduction with time and resource constraints.
- **Compliance Mapper**: Automatically maps findings (CVEs, vulnerabilities) to industry frameworks like NIST, ISO, and CIS.
- **Explainable Narratives**: Converts technical findings into plain-language explanations tailored for engineers, CISOs, and board members.
- **Business Impact Scoring**: Estimates financial risk ($) and compliance improvement (%) for every decision.
- **Executive Summary Generator**: Produces auto-generated one-page reports for leadership.
- **Adaptive Prioritization**: Learns from analyst feedback to adjust weights and rules over time.
- **Natural-Language Risk Queries**: Ask questions like *"What should we fix this week for maximum compliance gain?"* and get actionable answers.
- **Explainability Heatmaps**: Transparent scoring breakdowns showing how each component (CVSS, EPSS, KEV, context, rules) contributes to final risk.
- **MCP Integration**: All features are exposed as MCP tools, enabling interoperability with AI copilots and external systems.

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │    │  FastAPI Server │    │    MCP Layer    │
│                 │    │                 │    │                 │
│ • Plan Tab      │◄──►│ • Score Engine  │◄──►│ • MCP Tools     │
│ • Compliance    │    │ • Optimizer     │    │ • External AI   │
│ • Narratives    │    │ • Impact Model  │    │ • Interop APIs  │
│ • Copilot       │    │ • Summarizer    │    │ • Extensions    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (for summaries and narratives)
- (Optional) MCP-compatible client (Claude Desktop, VSCode MCP)

### 1. Clone Repository
```bash
git clone https://github.com/<your-username>/riskalign-ai.git
cd riskalign-ai
```

### 2. Backend Setup
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd client
npm install
npm run dev
```

### 4. Start Backend
```bash
cd server
uvicorn main:app --reload --port 8000
```

### 5. Access Application
Visit: `http://localhost:5173`

---

## 📂 Project Structure

```
riskalign-ai/
├── server/               # FastAPI backend + MCP server
│   ├── scoring.py        # scoring engine with explainability
│   ├── optimizer.py      # risk-to-cost optimization
│   ├── impact.py         # business impact calculations
│   ├── mapping.py        # compliance mapping
│   ├── feedback.py       # adaptive learning from feedback
│   ├── nl_router.py      # natural language query routing
│   ├── main.py           # FastAPI app entry
│   ├── config/           # scoring rules, compliance maps
│   └── data/             # sample findings
├── client/               # React + Vite frontend
│   ├── src/pages/        # Plan, Compliance, Narratives, Copilot
│   ├── src/components/   # reusable components
│   └── vite.config.ts
└── README.md
```

---

## 🧠 Example Use Cases

- **CISO**: Understand which vulnerabilities reduce the most business risk.  
- **Compliance Officer**: Map vulnerabilities directly to control frameworks for audit prep.  
- **Engineer**: Get prioritized tickets with clear explanations of *why this matters*.  
- **Board**: Receive a one-page executive summary with $$ impact and compliance coverage.  

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -m "Added my feature"`)  
4. Push to branch (`git push origin feature/my-feature`)  
5. Open a Pull Request  

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**Built with:** FastAPI • React • Model Context Protocol • OpenAI
