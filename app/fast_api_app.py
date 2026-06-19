# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import shutil
from typing import Optional, List, Dict, Any

import google.auth
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback
from app.agents.cyber_agents import run_cyber_shield_scan
from app.memory.database import (
    get_all_cases,
    get_case,
    get_traces_for_case,
    get_tool_calls_for_case,
    get_analytics_summary,
    save_case,
    delete_case_db,
    clear_all_cases_db,
    get_all_memory_entities,
    delete_memory_entity_db,
    update_memory_entity_db,
    add_memory_entity_db,
    reseed_memory_bank_db
)

setup_telemetry()
try:
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    class LocalLogger:
        def log_struct(self, data, severity="INFO"):
            logging.info(f"[{severity}] Struct log: {data}")
    logger = LocalLogger()

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# Initialize base ADK FastAPI App
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=False,
)
app.title = "CyberShield AI"
app.description = "CyberShield AI: Student Scam & Fraud Protection Network API"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders for uploads if they do not exist
UPLOAD_DIR = os.path.join(AGENT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------------------------------------------
# Custom API Endpoints
# ----------------------------------------------------

@app.post("/api/scan")
async def scan_content(
    text: str = Form(""),
    filePath: Optional[str] = Form(None),
    mode: str = Form("quick")
):
    """Scan plain text, URLs, and screenshots for cybersecurity threats."""
    if not text.strip() and not filePath:
        raise HTTPException(status_code=400, detail="Either 'text' or a uploaded file is required.")
        
    try:
        case_record = await run_cyber_shield_scan(text, filePath, mode)
        return case_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan execution failed: {str(e)}")

def get_admin_key(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    """Security dependency checking for correct admin secret passcode."""
    admin_secret = os.getenv("ADMIN_PASSCODE", "cybershield_pvt_2026")
    if not x_admin_key or x_admin_key != admin_secret:
        raise HTTPException(status_code=401, detail="Access Denied: Invalid or missing admin key.")
    return x_admin_key

@app.post("/api/admin/verify")
def verify_admin(payload: Dict[str, str]):
    """Verify private admin username and passcode securely on the server side."""
    username = payload.get("username", "")
    key = payload.get("key", "")
    
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_secret = os.getenv("ADMIN_PASSCODE", "cybershield_pvt_2026")
    
    if username == admin_username and key == admin_secret:
        return {"status": "success", "token": "cybershield_admin_session_token_approved"}
    raise HTTPException(status_code=401, detail="Access Denied: Invalid admin username or password.")

@app.post("/api/user/verify")
def verify_user(payload: Dict[str, str]):
    """Verify standard user credentials (predefined single student account) securely on the server."""
    username = payload.get("username", "")
    password = payload.get("password", "")
    
    required_username = os.getenv("USER_USERNAME", "student@university.edu")
    required_password = os.getenv("USER_PASSWORD", "cybershield_student_2026")
    
    if username == required_username and password == required_password:
        return {"status": "success", "message": "Authenticated successfully as user."}
    raise HTTPException(status_code=401, detail="Access Denied: Invalid username or password.")

# --- Admin CRUD Operations for DB Management ---

@app.delete("/api/admin/cases/{case_id}")
def delete_case(case_id: str, admin_key: str = Depends(get_admin_key)):
    """Securely deletes a scam verification case by ID."""
    try:
        delete_case_db(case_id)
        return {"status": "success", "message": f"Case {case_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/cases/{case_id}")
def update_case(case_id: str, payload: Dict[str, Any], admin_key: str = Depends(get_admin_key)):
    """Securely updates database records of a case (e.g. verdicts, scores, explanation)."""
    try:
        # Load existing case to preserve structure
        case = get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found.")
        
        # Overlay new fields from payload
        for k, v in payload.items():
            case[k] = v
            
        save_case(case)
        return {"status": "success", "case": case}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/memory")
def list_memory_entities(admin_key: str = Depends(get_admin_key)):
    """Securely fetches all memory-bank threat entities (domains, phones, emails, URLs)."""
    try:
        return get_all_memory_entities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/memory")
def create_memory_entity(payload: Dict[str, Any], admin_key: str = Depends(get_admin_key)):
    """Securely adds a new threat intelligence entity to memory bank."""
    try:
        entity_type = payload.get("entity_type")
        entity_value = payload.get("entity_value")
        verdict = payload.get("verdict")
        
        if not entity_type or not entity_value or not verdict:
            raise HTTPException(status_code=400, detail="Missing required threat intelligence parameters.")
            
        new_id = add_memory_entity_db(entity_type, entity_value, verdict)
        return {"status": "success", "id": new_id, "entity_type": entity_type, "entity_value": entity_value, "verdict": verdict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/memory/{entity_id}")
def edit_memory_entity(entity_id: int, payload: Dict[str, Any], admin_key: str = Depends(get_admin_key)):
    """Securely edits a threat entity (type, value, verdict status, or verification counters)."""
    try:
        entity_type = payload.get("entity_type")
        entity_value = payload.get("entity_value")
        verdict = payload.get("verdict")
        times_seen = payload.get("times_seen", 1)
        
        if not entity_type or not entity_value or not verdict:
            raise HTTPException(status_code=400, detail="Missing threat update parameters.")
            
        update_memory_entity_db(entity_id, entity_type, entity_value, verdict, times_seen)
        return {"status": "success", "message": f"Threat indicator {entity_id} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/memory/{entity_id}")
def delete_memory_entity(entity_id: int, admin_key: str = Depends(get_admin_key)):
    """Securely deletes a threat entity from memory bank."""
    try:
        delete_memory_entity_db(entity_id)
        return {"status": "success", "message": f"Threat indicator {entity_id} deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/db/clear-cases")
def clear_cases(admin_key: str = Depends(get_admin_key)):
    """Securely clears all parsed safety cases logs."""
    try:
        clear_all_cases_db()
        return {"status": "success", "message": "Database cases and trace logs cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/db/reset-threat-memory")
def reset_threat_memory(admin_key: str = Depends(get_admin_key)):
    """Securely clears and reseeds baseline threat memory bank database."""
    try:
        reseed_memory_bank_db()
        return {"status": "success", "message": "Threat memory intelligence database reseeded to baseline rules."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload screenshots, job flyers, or PDFs securely with validation checks."""
    allowed_types = ["image/png", "image/jpeg", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PNG, JPEG, WEBP, PDF.")
        
    try:
        # Validate file size (max 5MB to prevent DoS disk exhaustion)
        MAX_SIZE = 5 * 1024 * 1024
        contents = await file.read()
        if len(contents) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size allowed is 5MB.")
        
        # Reset pointer after reading length
        file.file.seek(0)
        
        # Secure the filename against directory traversal attacks
        safe_name = os.path.basename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"status": "success", "file_path": file_path, "filename": safe_name}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/api/cases")
def list_cases(limit: int = 50):
    """Retrieve history of analyzed cases."""
    return get_all_cases(limit)

@app.get("/api/cases/{case_id}")
def retrieve_case(case_id: str):
    """Retrieve details of a specific case."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return case

@app.get("/api/traces/{case_id}")
def retrieve_traces(case_id: str):
    """Retrieve agent execution trails and latency details for a case."""
    traces = get_traces_for_case(case_id)
    tool_calls = get_tool_calls_for_case(case_id)
    return {"traces": traces, "tool_calls": tool_calls}

@app.get("/api/analytics")
def retrieve_analytics():
    """Retrieve high-level dashboard metrics for threat monitoring."""
    return get_analytics_summary()

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}

# Serve static frontend dashboard files
FRONTEND_DIR = os.path.join(AGENT_DIR, "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Remove any default root routes registered by ADK to let our redirect override
for r in list(app.routes):
    if r.path == "/":
        app.routes.remove(r)

@app.get("/")
def read_root():
    """Redirect roots to frontend dashboard page."""
    return RedirectResponse(url="/static/index.html")

@app.get("/admin")
def read_admin():
    """Redirect admin path to secure admin panel."""
    return RedirectResponse(url="/static/admin.html")


# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
