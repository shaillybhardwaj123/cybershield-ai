import re
import os
import json
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.memory.database import (
    lookup_memory_entity,
    update_or_add_memory_entity,
    save_case,
    get_case,
    get_all_cases,
    log_tool_call
)

# Helper function for domain distance (Levenshtein)
def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]

# 1. URL Inspection Tool
def url_inspection_tool(url: str, case_id: str = "") -> Dict[str, Any]:
    """Analyzes a URL for suspicious phishing features, lookalike domains, and shortened links.

    Args:
        url: The URL to inspect.
        case_id: Optional case identifier for logging.

    Returns:
        A dict containing parsed components, indicators, and risk score.
    """
    inputs = {"url": url}
    
    # Simple normalization
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "http://" + clean_url
        
    try:
        parsed = urllib.parse.urlparse(clean_url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
    except Exception:
        domain = clean_url
        path = ""
        
    indicators = []
    risk_score = 0
    
    # A) Check shortened link services
    shorteners = ["bit.ly", "tinyurl.com", "t.co", "cutt.ly", "is.gd", "rebrand.ly", "ow.ly", "buff.ly", "shorturl.at"]
    is_shortened = any(sh in domain for sh in shorteners)
    if is_shortened:
        indicators.append("Shortened URL: Hides the final destination domain.")
        risk_score += 40
        
    # B) Check suspicious TLDs
    suspicious_tlds = [".xyz", ".cc", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".work", ".click", ".win", ".club", ".info", ".bid", ".loan"]
    matched_tld = next((tld for tld in suspicious_tlds if domain.endswith(tld)), None)
    if matched_tld:
        indicators.append(f"Suspicious Top-Level Domain (TLD) '{matched_tld}': Frequently used for scam sites.")
        risk_score += 25
        
    # C) Check suspicious keywords in subdomain/path
    suspicious_keywords = ["login", "verify", "secure", "bank", "account", "update", "jobs", "career", "free", "gift", "prize", "bonus", "wallet", "pay"]
    matched_words = [word for word in suspicious_keywords if word in domain or word in path]
    if matched_words:
        indicators.append(f"Contains misleading urgency/brand keywords: {', '.join(matched_words)}.")
        risk_score += 20 * len(matched_words)
        
    # D) Typosquatting / Domain Similarity Check
    legitimate_brands = ["google.com", "microsoft.com", "amazon.com", "tcs.com", "wipro.com", "sbi.co.in", "netflix.com", "paypal.com", "linkedin.com", "github.com", "whatsapp.com", "telegram.org"]
    
    for brand in legitimate_brands:
        if domain == brand:
            continue
        # Compare base domain name without TLD
        brand_base = brand.split('.')[0]
        domain_base = domain.split('.')[0]
        
        # Exact substring match (e.g. google-verify.com)
        if brand_base in domain_base and brand_base != domain_base:
            indicators.append(f"Brand Impersonation Signal: Domain base '{domain_base}' mimicks trust brand '{brand}'.")
            risk_score += 35
            break
        # Levenshtein distance check (close typosquatting like micr0soft.com)
        dist = levenshtein_distance(domain_base, brand_base)
        if 0 < dist <= 2:
            indicators.append(f"Typosquatting Risk: Domain base '{domain_base}' is extremely similar to brand '{brand_base}'.")
            risk_score += 45
            break

    # E) IP Address as Host
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    if re.match(ip_pattern, domain):
        indicators.append("IP Address Domain: Accesses site via IP instead of domain name, highly unusual for clean sites.")
        risk_score += 50

    # Cap risk score at 100
    risk_score = min(risk_score, 100)
    
    # Check Threat Intelligence Database
    db_match = lookup_memory_entity(domain)
    if not db_match:
        db_match = lookup_memory_entity(url)
        
    if db_match:
        indicators.append(f"Threat Intel Hit: Found in local threat database as {db_match['verdict']} (seen {db_match['times_seen']} times).")
        if db_match['verdict'] == 'DANGEROUS':
            risk_score = max(risk_score, 95)
        elif db_match['verdict'] == 'HIGH RISK':
            risk_score = max(risk_score, 80)
        else:
            risk_score = max(risk_score, 50)
            
    output = {
        "domain": domain,
        "is_shortened": is_shortened,
        "indicators": indicators,
        "risk_score": risk_score,
        "verdict": "SAFE" if risk_score < 25 else "SUSPICIOUS" if risk_score < 60 else "HIGH RISK" if risk_score < 85 else "DANGEROUS"
    }
    
    if case_id:
        log_tool_call(case_id, "url_inspection_tool", inputs, output)
        if risk_score >= 60:
            update_or_add_memory_entity("domain", domain, output["verdict"])
            
    return output


# 2. Text Risk Scoring Tool
def text_risk_scoring_tool(text: str, case_id: str = "") -> Dict[str, Any]:
    """Scores text for high-pressure wording, reward bait, threat language, and fake offers.

    Args:
        text: The text content to score.
        case_id: Optional case identifier for logging.

    Returns:
        A dict containing risk score, matched phrases, and categories.
    """
    inputs = {"text": text}
    risk_score = 0
    matched_signals = {}
    
    # A) Urgency signals
    urgency_patterns = [
        (r"\b(urgent|urgently|act now|hurry|last chance|last date|deadline)\b", 15, "Urgency"),
        (r"\b(within \d+ (hours|mins|minutes|days)|today itself)\b", 20, "Time pressure"),
        (r"\b(account (will be |is )?blocked|card (will be |is )?suspended|expires in)\b", 25, "Urgency / Threat")
    ]
    
    # B) Reward bait signals
    reward_patterns = [
        (r"\b(congratulations|congrats|selected|you are selected|shortlisted)\b", 15, "Unsolicited Selection"),
        (r"\b(lottery|jackpot|won \$?\d+|lucky draw|cash prize|free reward)\b", 25, "Financial Bait"),
        (r"\b(earn \d+ (daily|per day|hourly)|work from home job|data entry job|no skills required)\b", 20, "Easy Money Job Bait"),
        (r"\b(double your money|investment bonus|crypto profit|earn fast)\b", 25, "Get-Rich-Quick")
    ]
    
    # C) Threat / Fear / Compliance pressure
    threat_patterns = [
        (r"\b(police|court|legal action|avoid arrest|customs department|security deposit)\b", 20, "Fear Tactics"),
        (r"\b(pay \d+ fee|deposit first|refundable fee|processing charges|upfront payment|upfront fee|advance payment|fake internship|internship scam|pay before hiring)\b", 25, "Advance Fee Fraud / Internship Scam"),
        (r"\b(share OTP|verify details|confirm password|verify netbanking)\b", 30, "Credential Harvesting")
    ]
    
    # Score calculations
    matched_items = []
    
    for pattern, weight, cat in urgency_patterns + reward_patterns + threat_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            risk_score += weight * len(matches)
            matched_items.append(f"{cat}: matched '{matches[0][0] if isinstance(matches[0], tuple) else matches[0]}'")
            
    # D) Formatting checks (all caps, exclamation marks, suspicious phone formatting)
    if text.isupper() and len(text) > 20:
        risk_score += 15
        matched_items.append("Formatting: Entire message written in UPPERCASE (creates false urgency).")
        
    if "!!!" in text or "???" in text:
        risk_score += 10
        matched_items.append("Formatting: Excessive exclamation/question marks (creates panic/hype).")
        
    # Cap risk score at 100
    risk_score = min(risk_score, 100)
    
    output = {
        "risk_score": risk_score,
        "matched_signals": matched_items,
        "verdict": "SAFE" if risk_score < 25 else "SUSPICIOUS" if risk_score < 60 else "HIGH RISK" if risk_score < 85 else "DANGEROUS"
    }
    
    if case_id:
        log_tool_call(case_id, "text_risk_scoring_tool", inputs, output)
        
    return output


# 3. Job Post Verification Tool
def job_post_verification_tool(job_details: str, case_id: str = "") -> Dict[str, Any]:
    """Analyzes a job or internship description/message for fake recruitment patterns.

    Args:
        job_details: Text from the job posting or recruiting message.
        case_id: Optional case identifier.

    Returns:
        A dict with verified factors, anomalies, and scam score.
    """
    inputs = {"job_details": job_details}
    anomalies = []
    scam_score = 0
    
    # A) Advance payment request
    payment_keywords = ["refundable deposit", "security fee", "training charge", "registration fee", "laptop charges", "document processing fee", "buy software first", "upfront payment", "upfront fee", "fake internship", "internship scam", "advance payment", "pay before hiring"]
    for kw in payment_keywords:
        if kw in job_details.lower():
            anomalies.append(f"Advance Fee Request: Flags request to pay '{kw}' (Legitimate employers never ask candidates to pay).")
            scam_score += 45
            
    # B) Unofficial communication channel
    channel_keywords = ["whatsapp group", "telegram channel", "telegram contact", "dm on whatsapp", "text to hr on telegram"]
    for kw in channel_keywords:
        if kw in job_details.lower():
            anomalies.append(f"Unofficial Communication: Uses private messaging platforms ('{kw}') for recruitment.")
            scam_score += 25
            
    # C) Too-good-to-be-true salary
    salary_patterns = [
        (r"(earn|salary|payment|package)\s+(of\s+)?(up\s+to\s+)?(rs\.?|inr|usd|\$)\s*(\d{4,6})\s*(per\s*day|daily|per\s*week|weekly|per\s*hr|hourly)", "High hourly/daily wages for entry-level work"),
        (r"(part\s*time|work\s*from\s*home|simple\s*task)\s*.*(earn|salary|pay)\s*.*(rs\.?|inr|usd|\$)\s*(\d{4,6})", "High payout for simple task")
    ]
    for pattern, desc in salary_patterns:
        if re.search(pattern, job_details, re.IGNORECASE):
            anomalies.append(f"Unrealistic Salary: {desc} (Often used as bait for students).")
            scam_score += 30
            break
            
    # D) Vague description & Urgent hire
    if "immediate joiner" in job_details.lower() or "urgent hiring" in job_details.lower():
        if "no experience required" in job_details.lower() or "freshers welcome" in job_details.lower():
            anomalies.append("Immediate Easy Recruitment: Offers immediate hiring with zero barriers to entry (common scam recruitment tactic).")
            scam_score += 15

    scam_score = min(scam_score, 100)
    
    output = {
        "scam_score": scam_score,
        "anomalies": anomalies,
        "verdict": "SAFE" if scam_score < 25 else "SUSPICIOUS" if scam_score < 60 else "HIGH RISK" if scam_score < 85 else "DANGEROUS"
    }
    
    if case_id:
        log_tool_call(case_id, "job_post_verification_tool", inputs, output)
        
    return output


# 4. Attachment OCR Tool
def attachment_ocr_tool(file_path: str, case_id: str = "") -> Dict[str, Any]:
    """Simulates extracting text from suspicious flyers, screenshots, banners, or PDFs.
       Integrates standard mock database content or reads local file content if it is a text-based file.

    Args:
        file_path: Path or filename of the attachment.
        case_id: Optional case identifier.

    Returns:
        A dict containing the extracted text and visual indicators.
    """
    inputs = {"file_path": file_path}
    
    # Baseline simulated responses for demo screenshots
    simulated_texts = {
        "whatsapp_internship.png": """
            🚀 GOOGLE INTERNSHIP OFFER 🚀
            Location: Work from Home
            Stipend: ₹45,000 / Month
            Duration: 3 Months
            No qualifications required! Students from any stream can apply.
            Registration fee: ₹499 (Refundable)
            Contact HR on Telegram: @GoogleIndiaRecruit
            Click to register: https://google-internship-registration.cc/apply
        """,
        "scholarship_scam.pdf": """
            NATIONAL MERIT SCHOLARSHIP DRIVE 2026
            Apply now to get ₹1,50,000 yearly scholarship.
            Supported by Ministry of Student Welfare.
            To claim your scholarship, deposit a processing fee of ₹1,200 immediately to account: 4433-2211-0987.
            Deadline: TODAY.
            Official Link: http://national-welfare-portal.net/verify
        """,
        "verification_email.png": """
            Dear Customer,
            Your State Bank of India account has been flagged for suspicious activity.
            Please verify your NetBanking credentials immediately or your account will be BLOCKED within 24 hours.
            Click here to verify: https://sbi-verification-secure.com/login.html
            Thank you,
            SBI Security Team
        """
    }
    
    base_name = os.path.basename(file_path)
    extracted_text = simulated_texts.get(base_name, "")
    
    # Fallback to reading file directly if it's text/log, or run real Gemini Vision OCR for images
    if not extracted_text:
        if os.path.exists(file_path):
            file_lower = file_path.lower()
            # If it's a binary image, run Gemini OCR
            if file_lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
                has_gemini = bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "True")
                if has_gemini:
                    try:
                        from google.genai import Client
                        from google.genai import types
                        client = Client()
                        with open(file_path, "rb") as f:
                            img_bytes = f.read()
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                                "Extract all visible text from this image as plain text. Return only the extracted text, nothing else."
                            ]
                        )
                        if response and response.text:
                            extracted_text = response.text
                    except Exception as e:
                        extracted_text = f"[Gemini Vision OCR Failed: {str(e)}]"
                else:
                    extracted_text = f"[Simulated OCR fallback: Image uploaded but Gemini API key is not configured for OCR.]"
            else:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        extracted_text = f.read(1500) # read first 1500 chars
                except Exception:
                    extracted_text = f"[OCR Extraction Failed for: {base_name}]"
        else:
            extracted_text = f"[Simulated OCR: Generic banner offering rewards for clicking link: http://win-prize-now.click]"

    indicators = []
    if "fee" in extracted_text.lower() or "deposit" in extracted_text.lower():
        indicators.append("Visual text asks for upfront fee or bank deposit.")
    if "telegram:" in extracted_text.lower() or "@" in extracted_text.lower():
        indicators.append("Visual text directs user to telegram recruiter/handles.")
        
    output = {
        "file_name": base_name,
        "extracted_text": extracted_text.strip(),
        "visual_indicators": indicators
    }
    
    if case_id:
        log_tool_call(case_id, "attachment_ocr_tool", inputs, output)
        
    return output


# 5. Threat Intel Lookup Tool
def threat_intel_lookup_tool(query: str, case_id: str = "") -> Dict[str, Any]:
    """Looks up threat intelligence history for a phone number, email, domain, or URL.

    Args:
        query: The indicator (domain, phone number, email, URL) to check.
        case_id: Optional case identifier.

    Returns:
        A dict with lookup findings.
    """
    inputs = {"query": query}
    
    # Extract domain if query is a URL
    clean_query = query.strip()
    if clean_query.startswith(("http://", "https://")):
        try:
            parsed = urllib.parse.urlparse(clean_query)
            domain = parsed.netloc.lower()
            # Try to lookup domain first
            match = lookup_memory_entity(domain)
            if match:
                clean_query = domain
        except Exception:
            pass

    match = lookup_memory_entity(clean_query)
    
    if match:
        output = {
            "found": True,
            "entity_type": match["entity_type"],
            "entity_value": match["entity_value"],
            "verdict": match["verdict"],
            "times_seen": match["times_seen"],
            "last_seen": match["last_seen"],
            "description": f"Known {match['entity_type']} flagged as {match['verdict']} in CyberShield Threat Intel Database. Seen in {match['times_seen']} previous incidents."
        }
    else:
        # Fallback: simple keyword matching in local threat families
        scam_families = {
            "whatsapp": "WhatsApp Task Scam (like-and-subscribe for money)",
            "telegram": "Telegram Recruiting Fraud (fake hr contacts)",
            "verification": "Impersonation Phishing (bank/utility account block threats)",
            "deposit": "Advance Fee Employment Scam (requiring training/laptop fees)"
        }
        
        matched_family = next((family for kw, family in scam_families.items() if kw in clean_query.lower()), "Unknown/New Indicator")
        output = {
            "found": False,
            "entity_type": "unknown",
            "entity_value": clean_query,
            "verdict": "SAFE",
            "description": f"No direct matches found in threat database. Placed in category: {matched_family} for baseline verification."
        }
        
    if case_id:
        log_tool_call(case_id, "threat_intel_lookup_tool", inputs, output)
        
    return output


# 6. Report Generator Tool
def report_generator_tool(case_data_json: str, case_id: str = "") -> Dict[str, Any]:
    """Generates a professional incident report template formatted for university placement cells or support teams.

    Args:
        case_data_json: Serialized JSON string containing case details (verdict, score, evidence, details).
        case_id: Optional case identifier.

    Returns:
        A dict with the markdown formatted report content.
    """
    inputs = {"case_data": case_data_json}
    
    try:
        data = json.loads(case_data_json)
    except Exception:
        data = {"verdict": "HIGH RISK", "risk_score": 85, "scam_type": "unknown", "explanation": "Failed to parse case data."}
        
    verdict = data.get("verdict", "SUSPICIOUS")
    score = data.get("risk_score", 50)
    scam_type = data.get("scam_type", "General Fraud")
    explanation = data.get("explanation", "")
    evidence = data.get("evidence", [])
    
    evidence_str = "\n".join([f"- [x] {item}" for item in evidence]) if evidence else "- [ ] Suspicious behavior patterns detected."
    
    report_md = f"""# 🛡️ CYBERSHIELD AI INCIDENT REPORT
**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Incident ID:** {case_id or 'CS-TEMP-99'}
**Risk Assessment:** {verdict} (Risk Score: {score}/100)
**Scam Category:** {scam_type.upper()}

---

## 📝 1. Incident Overview
The user requested verification of a suspicious message, communication, or document. Our automated multi-agent security pipeline analyzed the input against language manipulation vectors, phishing domains, recruitment policies, and visual markers.

### Summary of Verdict:
{explanation}

---

## 🔍 2. Technical Evidence Gathered
Below are the threat indicators detected during analysis:
{evidence_str}

---

## 🛑 3. Recommended Actions
1. **Do NOT reply** to the sender or transfer any funds.
2. **Block and Report** the sender on the messaging platform (e.g. WhatsApp, Telegram, Gmail).
3. **Escalate to University Authorities** if this message was received through college email listservs or placement portals.
4. **Warn Peers**: Share this incident report summary with classmates to prevent others from falling victim.

---
*Disclaimer: This report was compiled by CyberShield AI Security Agents. It is intended for educational safety and institutional compliance purposes.*
"""

    output = {
        "report_id": f"REP-{case_id or 'CS-TEMP-99'}",
        "verdict": verdict,
        "report_markdown": report_md.strip()
    }
    
    if case_id:
        log_tool_call(case_id, "report_generator_tool", inputs, output)
        
    return output


# 7. Safe Reply Tool
def safe_reply_tool(scam_type: str, details: str = "", case_id: str = "") -> Dict[str, Any]:
    """Generates polite refusal, inquiry, or warning reply templates that users can copy-paste.

    Args:
        scam_type: Type of scam (e.g., 'fake job offer', 'phishing', 'payment request').
        details: Specific details of the sender or offer.
        case_id: Optional case identifier.

    Returns:
        A dict containing reply templates.
    """
    inputs = {"scam_type": scam_type, "details": details}
    
    templates = {
        "fake job offer": """
"Thank you for the opportunity. Could you please send the formal offer letter and details from your official company email address (not a public domain like Gmail/Outlook)? Also, I would appreciate it if you could share a link to the job posting on your official company website so I can review it. Thank you."
        """,
        "payment request": """
"I am very interested in this opportunity, but company policies and security guidelines do not permit me to pay any upfront deposits, laptop configuration fees, or registration charges. I would be happy to proceed if the company can deduct any required fees directly from my monthly stipend/salary after I begin. Thank you for understanding."
        """,
        "phishing": """
"Thank you. I have received this warning regarding my account. To ensure safety, I will not be using the link provided in this message. Instead, I will log in to my account directly through the official website or contact support via the official toll-free helpline. Thank you."
        """,
        "general refusal": """
"Thank you for your message. I am not interested in this offer and request you to remove my contact details from your list. Please do not contact me further."
        """
    }
    
    key = scam_type.lower()
    selected_template = templates.get(key, templates["general refusal"])
    
    output = {
        "scam_type": scam_type,
        "reply_template": selected_template.strip()
    }
    
    if case_id:
        log_tool_call(case_id, "safe_reply_tool", inputs, output)
        
    return output


# 8. Case History Tool
def case_history_tool(action: str, case_id: str = "", case_data_json: str = "") -> Dict[str, Any]:
    """Retrieves or saves scans to SQLite database to maintain cross-case history and track repeat offenders.

    Args:
        action: The database action to perform ('save', 'get', 'list').
        case_id: The ID of the case (required for 'save' and 'get').
        case_data_json: The JSON case representation (required for 'save').

    Returns:
        A dict with query results.
    """
    inputs = {"action": action, "case_id": case_id}
    
    if action == "save" and case_id and case_data_json:
        try:
            data = json.loads(case_data_json)
            data["id"] = case_id
            save_case(data)
            output = {"status": "success", "message": f"Case {case_id} saved successfully."}
        except Exception as e:
            output = {"status": "error", "message": f"Failed to save case: {str(e)}"}
            
    elif action == "get" and case_id:
        case = get_case(case_id)
        if case:
            output = {"status": "success", "case": case}
        else:
            output = {"status": "not_found", "message": f"Case {case_id} not found."}
            
    elif action == "list":
        cases = get_all_cases()
        output = {"status": "success", "cases": cases}
        
    else:
        output = {"status": "invalid_action", "message": f"Action '{action}' is not supported."}
        
    # We do NOT log tool call for list/get to avoid recursion or excessive db logs
    return output
