# LogIntel RAG - Deployment Guide

This guide covers three recommended deployment paths for the LogIntel RAG application:

1. [Option 1: Free/Low-Cost Cloud PaaS (Render / Vercel + Supabase)](#option-1-cloud-paas-recommended)
2. [Option 2: Single Server / VPS with Docker Compose (AWS, DigitalOcean, Hetzner)](#option-2-docker-compose-on-a-vps)
3. [Option 3: Railway 1-Click Deployment](#option-3-railway)

---

## Architecture Overview

- **Frontend**: Next.js 16 (App Router, React 19, Tailwind CSS)
- **Backend**: FastAPI (Python 3.11, Uvicorn, SQLAlchemy)
- **Database**: PostgreSQL 16 with `pgvector` extension
- **LLM Engine**: Groq API (`GROQ_API_KEY`)

---

## Option 1: Cloud PaaS (Recommended)

### Step 1: Provision a Free Vector Database (Supabase or Neon)
Both Supabase and Neon offer free tier PostgreSQL with `pgvector` pre-installed:

1. Create a free account at [Supabase](https://supabase.com) or [Neon](https://neon.tech).
2. Create a new database project.
3. In Supabase/Neon SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Copy the connection string (`postgresql://...`). Note: if using Supabase, copy the "Direct connection" or "Transaction pooler" string with Session mode (port 5432 or 6543).

### Step 2: Deploy Backend (Render)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** -> **Web Service**.
3. Select your repository `Baazigar111/RAG`.
4. Fill in the settings:
   - **Name**: `logintel-backend`
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `DATABASE_URL`: Your Supabase/Neon PostgreSQL connection string
   - `GROQ_API_KEY`: Your Groq API key (`gsk_...`)
   - `CORS_ORIGINS`: `*` (or your frontend domain once deployed)
6. Click **Deploy Web Service**. Once deployed, copy your backend URL (e.g., `https://logintel-backend.onrender.com`).

### Step 3: Deploy Frontend (Vercel or Render)

#### Deploying on Vercel (Fastest):
1. Sign in to [Vercel](https://vercel.com) and click **Add New...** -> **Project**.
2. Select your repository `Baazigar111/RAG`.
3. Set **Root Directory** to `frontend`.
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: `https://your-backend-url.onrender.com` (from Step 2)
5. Click **Deploy**.

---

## Option 2: Docker Compose on a VPS

Deploy the entire stack (Postgres + pgvector, Backend, Frontend) onto any Linux VM (AWS EC2, DigitalOcean Droplet, Hetzner, Linode, etc.).

### Prerequisites on the Server
- Docker & Docker Compose plugin installed:
  ```bash
  sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin
  ```

### Deployment Steps

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/Baazigar111/RAG.git
   cd RAG
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Fill in your `GROQ_API_KEY`:
   ```dotenv
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

3. **Start all services in detached mode:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify container status:**
   ```bash
   docker compose ps
   ```
   You should see:
   - `logintel_postgres` on port `5433` (healthy)
   - `logintel_backend` on port `8000` (running)
   - `logintel_frontend` on port `3000` (running)

5. **Access the application:**
   - Frontend: `http://<your-server-ip>:3000`
   - Backend API Docs: `http://<your-server-ip>:8000/docs`
   - Health Check: `http://<your-server-ip>:8000/health`

---

## Option 3: Railway

1. Install Railway CLI or link your GitHub repo at [railway.app](https://railway.app).
2. Add a **PostgreSQL** service and enable `pgvector`.
3. Add a service from your repo pointing to `/` (Backend).
4. Add a second service from your repo pointing to `/frontend` (Frontend).
5. Link `DATABASE_URL` and `GROQ_API_KEY` across services.

---

## Verification & Health Check

1. **Check Backend Health**:
   ```bash
   curl https://<backend-url>/health
   # Expected response: {"status":"healthy","service":"logintel-rag-backend"}
   ```

2. **Test Incident Ingestion**:
   Send a sample post-mortem to the ingest endpoint:
   ```bash
   curl -X POST "https://<backend-url>/api/v1/ingest?service_name=auth-service&error_code=ERR_CONN_RESET&severity=HIGH" \
     -F "file=@sample_log.md"
   ```

3. **Test Triage UI**:
   Open the frontend in your browser, submit an incident triage request, and verify that the Groq LLM root-cause synthesis displays on screen.
