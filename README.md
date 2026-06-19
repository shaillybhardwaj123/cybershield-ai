<p align="center">
  <img src="https://raw.githubusercontent.com/shaillybhardwaj123/cybershield-ai/main/frontend/logo.png" width="120" alt="CyberShield AI Brand Logo" />
</p>

<h1 align="center">🛡️ CyberShield AI</h1>
<p align="center">
  <strong>Student Scam & Fraud Protection Network</strong>
</p>

<p align="center">
  <marquee scrollamount="4" behavior="scroll" direction="left" style="color: #10B981; font-weight: bold; font-family: monospace;">
    ⚠️ SECURITY TICKER: TYPOSQUATTING DOMAINS FLAGGED // TG TASK SCAMS DETECTED // HELPLINE 1930 ACTIVE ⚠️
  </marquee>
</p>

<p align="center">
  An advanced, production-grade <strong>Multi-Agent Security Pipeline</strong> built independently using the cutting-edge concepts of LLM orchestration, vector tracking, and security systems. CyberShield AI acts as an autonomous digital assistant shielding students and freshers from recruitment fraud, fake internships, scholarship scams, and credential harvesting.
</p>

---

## 🚀 Architectural Design & Key Features

* **Autonomous Multi-Agent Orchestration:** Integrates the Google Agent Development Kit (ADK) to organize multiple specialised agents into a unified, stateful `SequentialAgent` workflow.
* **Server-Side Security Enforcement:** Features robust server-side token handshakes to validate access to administrative dashboards, eliminating client-side inspector bypasses.
* **Multimodal Vision Scanning:** Employs `gemini-2.5-flash` to run real-time Vision OCR on screenshots, chat transcripts, and flyers, extracting threat vectors dynamically.
* **Observability & Trace Logs:** Every execution step, latency cost, and tool output is logged sequentially to a local database and rendered on a timeline.

---

## 🛠️ Detailed Tech Stack & Implementation

### 🔹 Backend Architecture & LLM Orchestration
* **Google Agent Development Kit (ADK):** Orchestrates the agent pipeline (`pipeline_agent`), structuring agent memory states and routing intermediate analysis.
* **FastAPI (Python):** Powers asynchronous endpoints for scanner operations, file uploads, secure admin logins, and serves static files.
* **Google GenAI / Gemini SDK:** Drives multimodal vision analysis and formats final coordinator assessments under strict Pydantic schemas.

### 🔹 Storage, Memory & Telemetry
* **SQLite Database:** Stores logs across four separate tables:
  * `cases`: Active cases database containing scores, evidence arrays, next steps, and reports.
  * `memory_bank`: Long-term threat intelligence database checking blacklisted phone numbers, email hosts, and domains.
  * `observability_traces`: Latency profiles and agent execution status tracking.
  * `tool_calls`: Log tracking raw inputs and returned parameters for debugging.
* **OpenTelemetry:** Integrated setup for distributed tracing and performance metrics logging.

### 🔹 Frontend Client
* **Vanilla HTML5, CSS3, & Modern JS:** Designed with Inter typography, sleek dark mode aesthetics, and hover spotlight effects mimicking digital government portals.
* **Observability Visualizer:** Renders vertical trace logs dynamically from the database to present real-time latency timelines.

---

## 📐 System Flowcharts & Diagrams

### Core Orchestration Pipeline
```mermaid
graph TD
    User([Student / Job Seeker]) -->|Interacts with UI| Frontend[Frontend SPA Dashboard]
    Frontend -->|POST /api/scan| Backend[FastAPI Backend Server]
    
    subgraph Multi-Agent Pipeline [CyberShield Multi-Agent Network]
        Backend -->|Initial Triage| Triage[Scam Triage Agent]
        Triage -->|Routes Task| Message[Message Analysis Agent]
        Triage -->|Routes Task| Job[Job Verification Agent]
        Triage -->|Routes Task| URL[URL Safety Agent]
        Triage -->|Routes Task| Intel[Threat Intel Agent]
        
        Message & Job & URL & Intel -->|Parallel Context| Advisor[Safety Advisor Agent]
        Advisor -->|Draft Recommendations| Coordinator[Crisis Coordinator Agent]
    end

    subgraph Custom Tools [Security Action Tools]
        URL -->|Invokes| ToolURL[URLInspectionTool]
        Message -->|Invokes| ToolText[TextRiskScoringTool]
        Job -->|Invokes| ToolJob[JobPostVerificationTool]
        Intel -->|Invokes| ToolIntel[ThreatIntelLookupTool]
        Advisor -->|Invokes| ToolReply[SafeReplyTool]
        Advisor -->|Invokes| ToolRep[ReportGeneratorTool]
        Coordinator -->|Invokes| ToolHistory[CaseHistoryTool]
    end

    subgraph Memory & Logging [SQLite Storage]
        ToolHistory -->|Saves Case| DBCases[(cases table)]
        ToolIntel -->|Queries/Updates| DBIntel[(memory_bank table)]
        Backend -->|Logs Execution Traces| DBTraces[(observability_traces table)]
        Backend -->|Logs Tool Payload| DBToolCalls[(tool_calls table)]
    end
    
    Coordinator -->|Structured Verdict| Backend
    Backend -->|JSON Report & Traces| Frontend
```

---

## ⚡ Setup & Local Execution

Configure and launch the application locally:

### 1. Install Dependencies
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
* **CLI Synthesizer:** Execute `agents-cli eval dataset synthesize` to produce standard evaluation dataset files.
* **CLI Evaluator:** Run `agents-cli eval run` to measure classification speed and boundary accuracy targets.
* **Interactive Panel:** Click **Run Agent Eval Suite** inside the **Admin Mode** tab on the web UI to verify accuracy scores live.

---

## ⚖️ License & Copyright

**© 2026 Shailly Bhardwaj. All Rights Reserved.**

This repository and all associated contents (source code, diagrams, telemetry logs, assets) are private and proprietary. No portion of this project may be copied, cloned, reproduced, redistributed, or used in any manner without the explicit prior written permission of the author.
