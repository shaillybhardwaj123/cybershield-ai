<p align="center">
  <img src="https://raw.githubusercontent.com/shaillybhardwaj123/cybershield-ai/main/frontend/logo.png" width="120" alt="CyberShield AI Brand Logo" />
</p>

<h1 align="center">🛡️ CyberShield AI</h1>
<p align="center">
  <strong>AI-powered multi-agent cybersecurity platform that protects students from phishing, fake internships, scholarship fraud, and recruitment scams.</strong>
</p>

<p align="center">
  <a href="https://cybershield-ai-84fb.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-🚀-success?style=for-the-badge&logo=render" alt="Live Demo" />
  </a>
  <a href="https://github.com/shaillybhardwaj123/cybershield-ai" target="_blank">
    <img src="https://img.shields.io/badge/GitHub_Repository-💻-blue?style=for-the-badge&logo=github" alt="GitHub Repository" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white" alt="Google ADK" />
  <img src="https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2" alt="Gemini" />
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white" alt="Git" />
  <img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white" alt="GitHub" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7" alt="Render" />
</p>

---

## 🔗 Live Deployment
*   **Demo Portal:** [https://cybershield-ai-84fb.onrender.com/](https://cybershield-ai-84fb.onrender.com/)
*   **GitHub Repository:** [https://github.com/shaillybhardwaj123/cybershield-ai](https://github.com/shaillybhardwaj123/cybershield-ai)
*   **Kaggle Submission Link:** *(To be added upon submission)*

---

## 🖼️ Screenshots & UI Showcase

### 1. Dashboard Home
*Landing portal displaying scanning inputs and configuration cards.*
![Dashboard Home](assets/dashboard.png)

### 2. Scam Detection Result
*Verdict view showcasing risk gauge results and parsed indicator evidence.*
![Scam Detection Result](assets/result.png)

### 3. Observability Timeline
*Timeline visualizer displaying latencies and trace payloads.*
![Observability Timeline](assets/workflow.png)

---

## 💡 Project Overview
CyberShield AI is an autonomous, production-grade **Multi-Agent Security Pipeline** built using the **Google Agent Development Kit (ADK)** and the Gemini model family. It acts as a personal security analyst for students, helping them verify recruitment offers, scholarship opportunities, and messaging threads before they become victims of cybercrime.

Every year, thousands of students lose money, credentials, and career opportunities to fake internships, scholarship scams, phishing campaigns, and impersonation attacks.

---

## 1. Problem Statement
The transition from college to the professional world is a high-vulnerability window for fresh graduates. Malicious actors leverage this to target academic placement systems and students directly via:
*   **Fake Internships & Jobs:** Offering high wages or stipends but requiring upfront "refundable" registration fees, training packages, or equipment deposits.
*   **Scholarship Fraud:** Promoting fake grants to harvest banking credentials or sensitive personal information.
*   **Credential Phishing:** Tricking students into logging in via lookalike domains (e.g., `placement-portal-g00gle.com`).
*   **Impersonation & Social Engineering:** Contacting students on messaging channels (Telegram, WhatsApp) pretending to be official university recruiters.

---

## 📐 Architecture

![System Architecture](assets/architecture.png)

CyberShield AI integrates an asynchronous FastAPI backend with a multi-agent orchestration pipeline.

### Core Telemetry & DB Schema
All operations, latencies, and tool variables are tracked in a local SQLite database containing:
*   `cases`: Log of investigated incidents, evidence arrays, and safety recommendations.
*   `memory_bank`: Locally cached threat indicators (domain, email, phone number) updated in real-time when dangerous verdicts are issued.
*   `observability_traces`: Latency profiles and step-by-step agent statuses.

---

## 🤖 Why Google ADK?
CyberShield AI leverages the **Google Agent Development Kit (ADK)** to:
*   **Orchestrate Multiple Specialized Security Agents:** Allowing parallel or sequential agent runs depending on dynamic input triage.
*   **Maintain Stateful Workflows:** Sharing threat indicators and analysis details cleanly across agent sessions without prompt dilution.
*   **Enable Tool Routing:** Equipping specialized agents with targeted capability tools (e.g., OCR, domain analysis) instead of general reasoning.
*   **Provide Modular Observability:** Logging granular latencies and token usage for complex threat investigations.

---

## 📊 Evaluation Results

| Metric | Result |
| :--- | :--- |
| **Scam Detection Accuracy (Recall)** | `92.0%` |
| **False Positive Rate (FPR)** | `6.0%` |
| **Average Analysis Time** | `4.2s` |

*\*Observed during internal testing. These metrics were observed during sandbox development testing and serve as local baseline performance parameters.*

---

## 🤖 Agent Responsibility Matrix

The system splits security logic among multiple specialized agents built on the **Google ADK** framework:

| Agent | Responsibility | Key Security Actions |
| :--- | :--- | :--- |
| **Triage Agent** | Scam classification | Parses input text to identify potential scam categories and dynamically route to downstream agents. |
| **URL Agent** | Link verification | Inspects domains for lookalike patterns (typosquatting) and suspicious TLDs. |
| **Job Agent** | Recruitment analysis | Audits recruitment details, detecting advance fee requests or unofficial channels. |
| **Message Agent** | Language risk analysis | Scores wording pressure tactics, urgency markers, and coercion vectors. |
| **Intel Agent** | Threat intelligence | Queries local SQLite blacklists for flagged emails, phone numbers, and domains. |
| **Coordinator Agent** | Final verdict | Aggregates all specialists' findings, calculates final risk scores, and compiles verdict. |
| **Advisor Agent** | Recommendations | Generates copy-paste safe reply templates and authority incident report markdown. |

---

## 🔄 Multi-Agent Workflow

```
       User Input
           │
           ▼
     Triage Agent
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│  Message Agent ── URL Agent ── Job Agent ── Intel Agent │  (Parallel Analysis)
└─────────────────────────────────────────────────────────┘
           │
           ▼
   Coordinator Agent (Verdict & Score Engine)
           │
           ▼
     Advisor Agent   (Actionable Guidance)
           │
           ▼
     Final Verdict
```

1.  **Ingestion:** The system parses inputs and extracts text from attachments using `attachment_ocr_tool`.
2.  **Triage Routing:** The `triage_agent` analyzes the content, defines the scam category, and loads corresponding specialists.
3.  **Parallel Specialist Evaluation:**
    *   `message_agent`: Invokes `text_risk_scoring_tool` to check urgency markers and pressure vectors.
    *   `job_agent`: Runs `job_post_verification_tool` to look for advance payment cues.
    *   `url_agent`: Invokes `url_inspection_tool` to check typosquatting and base domain records.
    *   `intel_agent`: Queries the local SQLite blacklist database using `threat_intel_lookup_tool`.
4.  **Advisory Assembly:** The `advisor_agent` constructs action checklists and safe reply refusal scripts.
5.  **Reconciliation:** The `coordinator_agent` merges inputs, evaluates evidence, computes the final risk score, and maps it to a strict Pydantic output schema (`CyberShieldVerdict`).

---

## ✨ Features
*   **Autonomous Multi-Agent Orchestration:** Integrates the Google ADK to organize multiple specialized agents into a unified, stateful `SequentialAgent` workflow.
*   **Server-Side Security Enforcement:** Features robust server-side token handshakes to validate access to administrative dashboards, eliminating client-side inspector bypasses.
*   **Multimodal Vision Scanning:** Employs Gemini to run real-time Vision OCR on screenshots, chat transcripts, and flyers, extracting threat vectors dynamically.
*   **Observability & Trace Logs:** Every execution step, latency cost, and tool output is logged sequentially to a local database and rendered on a timeline.

---

## 🛠️ Complete Tech Stack
*   **Core Languages:** Python (v3.11+), HTML5, CSS3, JavaScript (ES6+).
*   **Agent SDK:** Google Agent Development Kit (ADK) (`Agent`, `SequentialAgent`, `ParallelAgent`).
*   **LLM Model Support:** Google GenAI SDK / Vertex AI (Gemini 2.5 Flash / Pro).
*   **API Framework:** FastAPI, Uvicorn (ASGI web server).
*   **Storage & Databases:** SQLite 3 (telemetry log records, threat intelligence memory cache, audit traces).
*   **Dependencies Management:** Astral `uv` toolchain, `pyproject.toml` configuration.
*   **Containerization:** Docker & Docker-Compose.

---

## 🔐 Role-Based Access Control (RBAC) & Admin Security
CyberShield AI separates student users from placement cell administrators via strict, token-validated access controls:
*   **Student Workspace Access:** Authorized students submit suspected scams (text/attachments) via standard student credentials (`USER_USERNAME`/`USER_PASSWORD`).
*   **Admin Dashboard Privileges:** Access to tracing timelines, system evaluations, and memory-bank overrides is restricted behind server-side token handshakes, requiring admin credentials (`ADMIN_USERNAME`/`ADMIN_PASSCODE`).
*   **Secure Storage:** Tokens and default administrative passwords are set dynamically inside the secure environment configuration (`.env`).

---

## ⚡ Setup & Local Execution

### 1. Install Dependencies
Ensure you have `uv` or standard pip installed:
```bash
uv sync
# OR
pip install -r requirements.txt
```

### 2. Initialize Database
Initialize the SQLite schema and seed default blacklist indicators:
```bash
uv run python -c "from app.memory.database import init_db; init_db()"
```

### 3. Run FastAPI Application
```bash
uv run python -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000` in your browser.

---

## 🔬 Observability & Quality Evaluations
*   **CLI Synthesizer:** Execute `agents-cli eval dataset synthesize` to produce standard evaluation dataset files.
*   **CLI Evaluator:** Run `agents-cli eval run` to measure classification speed and boundary accuracy targets.
*   **Interactive Panel:** Click **Run Agent Eval Suite** inside the **Admin Mode** tab on the web UI to verify accuracy scores live.

---

## 🔮 Future Improvements
1.  **Vector Embeddings for Semantic Scam Matching:** Represent incoming text structures as high-dimensional vectors and compare them against a vector database of historic scams to detect mutational templates.
2.  **Federated Blacklist Sharing:** Establish anonymous P2P sharing of discovered threat indicators across multiple campus nodes.
3.  **Agentic Interactive Sidecars:** Launch sandboxed agent sidecars that automatically interact with suspicious recruiters via email/chat, probing them for credentials to gather solid evidence without exposing the user.
4.  **In-App / Extension Scanning Hooks:** Build browser plugins to scan messages on Gmail or WhatsApp Web directly with a single click.

---

## ⚖️ License
Licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
