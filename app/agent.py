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
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Robust GCP auth handling
try:
    _, project_id = google.auth.default()
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
except Exception:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

# Import CyberShield Agent orchestrator components
from app.agents.cyber_agents import (
    triage_agent,
    message_agent,
    job_agent,
    url_agent,
    intel_agent,
    advisor_agent,
    coordinator_agent,
    pipeline_agent
)

# Root agent is the main CyberShield orchestrator sequential pipeline
root_agent = pipeline_agent

app = App(
    root_agent=root_agent,
    name="app",
)
