import os
import json
import uuid
import time
import re
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.models import Gemini
from google.genai import types

from app.tools.custom_tools import (
    url_inspection_tool,
    text_risk_scoring_tool,
    job_post_verification_tool,
    attachment_ocr_tool,
    threat_intel_lookup_tool,
    report_generator_tool,
    safe_reply_tool,
    case_history_tool
)
from app.memory.database import log_trace, save_case, update_or_add_memory_entity

# 1. Output Schema for the final verdict
class CyberShieldVerdict(BaseModel):
    verdict: str = Field(description="verdict value: SAFE, SUSPICIOUS, HIGH RISK, or DANGEROUS")
    risk_score: int = Field(description="risk score from 0 to 100")
    scam_type: str = Field(description="scam category (phishing, fake job, fake internship, scholarship scam, payment fraud, malicious URL, social engineering, impersonation, etc.)")
    explanation: str = Field(description="clear, simple, non-technical explanation of the decision")
    evidence: List[str] = Field(description="list of specific scam indicators and signs found by agents")
    what_to_do: str = Field(description="practical instructions on what to do next (block, ignore, report)")
    safe_reply: Optional[str] = Field(description="copy-paste polite reply/refusal template if applicable, else empty string")
    report_summary: str = Field(description="professional summary of the incident for placement cells or authorities")

# Check if Gemini credentials are ready
def is_gemini_available() -> bool:
    return bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "True")

# Define the models
model_client = Gemini(
    model="gemini-flash-latest",
    retry_options=types.HttpRetryOptions(attempts=3)
)

# ----------------------------------------------------
# 2. ADK Agent Definitions (LLM-based)
# ----------------------------------------------------

triage_agent = Agent(
    name="triage_agent",
    model=model_client,
    instruction="""
    You are the Scam Triage Agent.
    Your job is to analyze the raw input text, identify the likely scam category, and decide which specialized analysis agents need to run.
    Categories: phishing, fake job, fake internship, scholarship scam, payment fraud, malicious URL, social engineering, impersonation, safe.
    Provide your triage results in JSON format.
    """,
    output_key="triage_result",
    description="Triage incoming text, URL, or email inputs to detect initial scam categories."
)

message_agent = Agent(
    name="message_agent",
    model=model_client,
    instruction="""
    You are the Message & Language Analysis Agent.
    Inspect the wording, urgency, spelling errors, threats, or high-pressure tactics.
    Highlight words like 'urgent', 'act now', 'congratulations', 'blocked', 'selected'.
    Use the text_risk_scoring_tool to analyze risk.
    """,
    tools=[text_risk_scoring_tool],
    output_key="message_result",
    description="Analyzes language patterns, urgency triggers, reward bait, and threat vectors."
)

job_agent = Agent(
    name="job_agent",
    model=model_client,
    instruction="""
    You are the Job / Internship Verification Agent.
    Evaluate job/internship details for anomalies like payment requests (training fees), unofficial communication channels, too-good-to-be-true stipends, or fake recruiter domains.
    Use job_post_verification_tool to check patterns.
    """,
    tools=[job_post_verification_tool],
    output_key="job_result",
    description="Verifies recruiting emails, job postings, and internships for fraudulent recruitment signals."
)

url_agent = Agent(
    name="url_agent",
    model=model_client,
    instruction="""
    You are the URL / Website Safety Agent.
    Inspect URLs for shortened links, typosquatting (micr0soft.com), domain base mimicry, or suspicious TLDs (.xyz, .cc).
    Use url_inspection_tool to analyze.
    """,
    tools=[url_inspection_tool],
    output_key="url_result",
    description="Inspects suspicious links, checks lookalike domains, shortened URLs, and phishing redirects."
)

intel_agent = Agent(
    name="intel_agent",
    model=model_client,
    instruction="""
    You are the Threat Intelligence Agent.
    Look up phone numbers, emails, domains, or URLs in the threat intel database using threat_intel_lookup_tool.
    Report similar known threat families.
    """,
    tools=[threat_intel_lookup_tool],
    output_key="intel_result",
    description="Queries local threat databases and logs to find matches for known scammers and domains."
)

advisor_agent = Agent(
    name="advisor_agent",
    model=model_client,
    instruction="""
    You are the Safety Advisor Agent.
    Generate practical, safe next steps, report templates (using report_generator_tool), and safe reply messages (using safe_reply_tool).
    """,
    tools=[report_generator_tool, safe_reply_tool],
    output_key="advisor_result",
    description="Generates actionable advice, safe copy-paste reply templates, and reporting instructions."
)

coordinator_agent = Agent(
    name="coordinator_agent",
    model=model_client,
    instruction="""
    You are the Crisis Coordinator Agent.
    Retrieve and merge findings from the previous agents in the session state:
    - Triage Result: {triage_result}
    - Message Analysis: {message_result}
    - Job/Internship Verification: {job_result}
    - URL Safety Analysis: {url_result}
    - Threat Intelligence Lookup: {intel_result}
    - Advisory Recommendations: {advisor_result}

    Verify all these inputs. Compute a final Risk Score (0-100), Verdict (SAFE, SUSPICIOUS, HIGH RISK, DANGEROUS), and Scam Type.
    Summarize evidence, draft a safe reply, and write a report summary conforming to the output schema.
    """,
    output_schema=CyberShieldVerdict,
    output_key="coordinator_result",
    description="Aggregates and compiles all agent findings into a structured final report."
)

# Real ADK sequential workflow pipeline
pipeline_agent = SequentialAgent(
    name="pipeline_agent",
    sub_agents=[triage_agent, message_agent, job_agent, url_agent, intel_agent, advisor_agent, coordinator_agent]
)

# ----------------------------------------------------
# 3. Hybrid Execution Engine (Rule-based Fallback & Trace Logging)
# ----------------------------------------------------

async def run_cyber_shield_scan(text: str, file_path: Optional[str] = None, mode: str = "quick") -> Dict[str, Any]:
    """Orchestrates sequential/parallel agent execution.
       Runs via LLM if Gemini is available, otherwise utilizes the rule-based expert engine.
       Records all traces, tool calls, and latencies in the SQLite database.
    """
    case_id = f"CS-{uuid.uuid4().hex[:8].upper()}"
    start_time = time.time()
    
    # Trace log: start
    log_trace(case_id, "System", "start", "INFO", "Scanning initiated.", 0)
    
    # Step 1: OCR Extraction if file is provided
    ocr_text = ""
    file_name = ""
    if file_path:
        file_name = os.path.basename(file_path)
        log_trace(case_id, "attachment_agent", "ocr_extraction_start", "RUNNING", f"Extracting text from: {file_name}", 0)
        t0 = time.time()
        ocr_result = attachment_ocr_tool(file_path, case_id)
        ocr_text = ocr_result["extracted_text"]
        latency = int((time.time() - t0) * 1000)
        log_trace(case_id, "attachment_agent", "ocr_extraction_complete", "DONE", f"Extracted: {ocr_text[:100]}...", latency)
        
    # Combine input text with OCR text
    combined_input = f"{text}\n\n[Extracted Visual Text]: {ocr_text}".strip() if ocr_text else text.strip()
    
    # Default rule-based values (always compute in case LLM fails or is disabled)
    detected_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', combined_input)
    has_url = len(detected_urls) > 0
    scam_type = "none"
    
    if "job" in combined_input.lower() or "internship" in combined_input.lower() or "recruit" in combined_input.lower() or "salary" in combined_input.lower() or "stipend" in combined_input.lower():
        scam_type = "fake job offer" if "job" in combined_input.lower() else "fake internship"
    elif "scholarship" in combined_input.lower() or "welfare" in combined_input.lower() or "student benefit" in combined_input.lower():
        scam_type = "scholarship scam"
    elif "block" in combined_input.lower() or "suspend" in combined_input.lower() or "verify bank" in combined_input.lower() or "otp" in combined_input.lower() or "netbanking" in combined_input.lower():
        scam_type = "phishing"
    elif "fee" in combined_input.lower() or "deposit" in combined_input.lower() or "transfer money" in combined_input.lower():
        scam_type = "payment fraud"
    elif has_url:
        scam_type = "suspicious URL"

    # Message Language Agent tool scoring
    msg_result = text_risk_scoring_tool(combined_input, case_id)
    # Job / Internship Agent tool scoring
    job_result = job_post_verification_tool(combined_input, case_id)
    # URL Safety Agent tool scoring
    url_results = []
    for u in detected_urls[:3]:
        url_results.append(url_inspection_tool(u, case_id))
    # Threat Intel Agent lookup scoring
    intel_results = []
    for r in url_results:
        intel_results.append(threat_intel_lookup_tool(r["domain"], case_id))
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', combined_input)
    phones = re.findall(r'\+?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', combined_input)
    for e in emails[:2]:
        intel_results.append(threat_intel_lookup_tool(e, case_id))
    for p in phones[:2]:
        intel_results.append(threat_intel_lookup_tool(p, case_id))

    url_max_score = max([r["risk_score"] for r in url_results]) if url_results else 0
    msg_score = msg_result["risk_score"]
    job_score = job_result["scam_score"]
    intel_hit = any(it["found"] for it in intel_results)
    
    risk_score = int((msg_score * 0.4) + (job_score * 0.3) + (url_max_score * 0.3))
    if intel_hit:
        risk_score = max(risk_score, 85)
    risk_score = max(0, min(risk_score, 100))
    
    verdict = "SAFE"
    if risk_score >= 85:
        verdict = "DANGEROUS"
    elif risk_score >= 60:
        verdict = "HIGH RISK"
    elif risk_score >= 25:
        verdict = "SUSPICIOUS"
        
    safe_reply_res = safe_reply_tool(scam_type if scam_type != "none" else "general refusal", text, case_id)
    reply_template = safe_reply_res["reply_template"]
    
    evidence = []
    if msg_result["matched_signals"]:
        evidence.extend(msg_result["matched_signals"][:3])
    if job_result["anomalies"]:
        evidence.extend(job_result["anomalies"][:3])
    for ur in url_results:
        if ur["indicators"]:
            evidence.extend(ur["indicators"][:2])
    for it in intel_results:
        if it["found"]:
            evidence.append(f"Threat Intelligence: {it['description']}")
    if not evidence:
        if risk_score > 25:
            evidence.append("Suspicious messaging markers and context anomalies detected.")
        else:
            evidence.append("No active threat vectors found in message content or URL domains.")
            
    explanations = {
        "SAFE": "This message appears legitimate. No common scam indicators, suspicious links, or advance fee requests were identified. However, always exercise baseline caution when sharing personal details.",
        "SUSPICIOUS": "Warning: This communication displays minor red flags. Urgency tactics or slightly suspicious language were detected. Verify the sender's identity before proceeding.",
        "HIGH RISK": "Attention: High probability of scam. This offer contains clear warning signs like requests for security deposits, unofficial recruiting channels, or mismatching domains. Do not reply or send money.",
        "DANGEROUS": "Critical: Severe Security Threat. Direct matches found in the threat intelligence databases, typosquatted brand domains, or phishing links designed to harvest your security credentials."
    }
    explanation = explanations[verdict]
    
    do_tips = {
        "SAFE": "You can safely reply or ignore if not needed. No action required.",
        "SUSPICIOUS": "Ask the recruiter for official verification. Do not click links directly; navigate to the official website instead.",
        "HIGH RISK": "Do NOT pay any fees. Report this sender to your college placement cell. Block their contact.",
        "DANGEROUS": "Block the sender immediately. If you entered details, reset your passwords and alert your bank immediately. File a complaint with the cyber cell."
    }
    what_to_do = do_tips[verdict]
    
    case_report_data = {
        "verdict": verdict,
        "risk_score": risk_score,
        "scam_type": scam_type if scam_type != "none" else "Normal Text",
        "explanation": explanation,
        "evidence": evidence
    }
    report_res = report_generator_tool(json.dumps(case_report_data), case_id)
    report_summary = report_res["report_markdown"]

    # ----------------------------------------------------
    # LLM Execution: Run actual ADK sequential agent pipeline
    # ----------------------------------------------------
    if is_gemini_available():
        log_trace(case_id, "System", "llm_agent_scan_start", "RUNNING", "Running Google ADK agent scan...", 0)
        t0 = time.time()
        try:
            # Create a dynamic sub-agents chain to optimize token billing & latency
            sub_agents = [triage_agent, message_agent]
            if has_url:
                sub_agents.append(url_agent)
            if any(k in combined_input.lower() for k in ["job", "internship", "recruit", "salary", "stipend"]):
                sub_agents.append(job_agent)
            
            sub_agents.extend([intel_agent, advisor_agent, coordinator_agent])
            
            dynamic_pipeline = SequentialAgent(
                name="dynamic_pipeline",
                sub_agents=sub_agents
            )
            
            # Create transient session for sequential pipeline
            session_service = InMemorySessionService()
            await session_service.create_session(app_name="app", user_id="user", session_id=case_id)
            runner = Runner(agent=dynamic_pipeline, app_name="app", session_service=session_service)
            
            # Run sequential pipeline to completion
            final_response = ""
            async for event in runner.run_async(
                user_id="user", session_id=case_id,
                new_message=types.Content(role="user", parts=[types.Part.from_text(text=combined_input)]),
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text

            # Retrieve final structured output from state
            session = await session_service.get_session(app_name="app", user_id="user", session_id=case_id)
            coord_res = session.state.get("coordinator_result")
            
            if coord_res:
                # Overwrite rule-based fields with genuine agent results
                if isinstance(coord_res, dict):
                    coord_data = coord_res
                elif isinstance(coord_res, BaseModel):
                    coord_data = coord_res.model_dump()
                else:
                    coord_data = json.loads(coord_res)
                
                verdict = coord_data.get("verdict", verdict)
                risk_score = int(coord_data.get("risk_score", risk_score))
                scam_type = coord_data.get("scam_type", scam_type)
                explanation = coord_data.get("explanation", explanation)
                evidence = coord_data.get("evidence", evidence)
                what_to_do = coord_data.get("what_to_do", what_to_do)
                reply_template = coord_data.get("safe_reply", reply_template)
                report_summary = coord_data.get("report_summary", report_summary)
                
                latency = int((time.time() - t0) * 1000)
                log_trace(case_id, "System", "llm_agent_scan_complete", "DONE", f"ADK Pipeline Scan completed successfully in {latency}ms", latency)
            else:
                log_trace(case_id, "System", "llm_agent_scan_failed", "ERROR", "Coordinator agent did not write result to session state.", 0)
        except Exception as e:
            log_trace(case_id, "System", "llm_agent_scan_error", "ERROR", f"ADK Scan pipeline crashed: {str(e)}", 0)

    # Save to SQLite DB
    case_db_record = {
        "id": case_id,
        "input_text": text,
        "file_name": file_name,
        "risk_score": risk_score,
        "verdict": verdict,
        "scam_type": scam_type if scam_type != "none" else "General / Safe",
        "explanation": explanation,
        "evidence": evidence,
        "next_steps": [what_to_do],
        "safe_reply": reply_template,
        "report_summary": report_summary,
        "timestamp": datetime.now().isoformat()
    }
    save_case(case_db_record)
    
    if verdict in ["HIGH RISK", "DANGEROUS"]:
        for ur in url_results:
            update_or_add_memory_entity("domain", ur["domain"], verdict)
        for e in emails[:2]:
            update_or_add_memory_entity("email", e, verdict)
        for p in phones[:2]:
            update_or_add_memory_entity("phone", p, verdict)
            
    total_latency = int((time.time() - start_time) * 1000)
    log_trace(case_id, "System", "complete", "INFO", f"Incident scan complete. Total Latency: {total_latency}ms", total_latency)
    
    return case_db_record
