# 🚀 CyberShield AI: Deployment & Production Guide

This guide details how to build, run, and deploy **CyberShield AI** locally or in production environments.

---

## 1. Running Locally

### Prerequisites
- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) (Recommended for fast package management)

### Local Startup
1. Sync dependencies and activate virtual environment:
   ```bash
   uv sync
   ```
2. Set up environment variables in a `.env` file (see `.env.example`).
3. Run the FastAPI application using Uvicorn:
   ```bash
   uv run python -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
   ```
4. Access the web dashboard at `http://localhost:8000`.

---

## 2. Containerized Deployment (Docker)

CyberShield AI is containerized using the multi-stage Docker build files included in the project.

### Docker Compose Startup
Run the application with one command:
```bash
docker-compose up --build
```
This starts the FastAPI server container, exposing port `8000` to the host machine. SQLite database storage is persisted via a named volume.

---

## 3. Production Cloud Deployment (Google Cloud Run)

To deploy CyberShield AI as a serverless container on **Google Cloud Run**:

### Step 1: Build & Submit Container to Artifact Registry
Set your Google Cloud Project ID and Region:
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker us-east1-docker.pkg.dev
```

Build and tag the Docker image:
```bash
docker build -t us-east1-docker.pkg.dev/YOUR_PROJECT_ID/cybershield-repo/scanner:v1 .
docker push us-east1-docker.pkg.dev/YOUR_PROJECT_ID/cybershield-repo/scanner:v1
```

### Step 2: Deploy to Cloud Run
Run the deployment command:
```bash
gcloud run deploy cybershield-ai \
  --image us-east1-docker.pkg.dev/YOUR_PROJECT_ID/cybershield-repo/scanner:v1 \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=your_gemini_api_key,ALLOW_ORIGINS=*"
```

---

## 4. Google Cloud ADK Platform Registration

To register the core ADK agent with the **Gemini Enterprise Agent Platform**:

1. Authenticate with Google:
   ```bash
   agents-cli login --interactive
   ```
2. Enable Agent Runtime:
   ```bash
   agents-cli scaffold enhance . --deployment-target agent_runtime
   ```
3. Deploy & Register:
   ```bash
   agents-cli deploy
   agents-cli publish gemini-enterprise
   ```
This deploys the agent runner into Google's managed runtime and makes it discoverable as an Enterprise Agent capability.
