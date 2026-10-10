# 🌾 TerraTrust AI — Production Deployment Guide

> **International Hackathon Final Submission Deployment Guide**  
> Complete end-to-end instructions for deploying the **Full-Stack TerraTrust AI** system (AI/ML Models, FastAPI Backend, SQLite/PostgreSQL Database, and React Vite Frontend).

---

## 🚀 Architecture Overview

TerraTrust AI is architected for **zero-friction hackathon deployment**:
- **Frontend**: React 18 + Vite + TailwindCSS + Recharts
- **Backend**: FastAPI (Python 3.12/3.14) with RESTful API contracts
- **AI/ML Engine**: Scikit-Learn ExtraTreesRegressor trained crop yield pipeline (`models/terratust_crop_yield_model.pkl`)
- **Database**: Zero-configuration auto-seeded SQLite (with full support for cloud PostgreSQL)
- **Deployment Mode**: Unified Single-Origin Container (Frontend + Backend + ML served from a single port/URL) or Decoupled (Vercel + Render).

---

## 🌟 Quick Links for Hackathon Judges & Evaluators

Once deployed:
| Component | Endpoint | Purpose |
| :--- | :--- | :--- |
| **Web UI Portal** | `/` (e.g. `https://terratrust-ai.onrender.com/`) | Complete Interactive Dashboard & Farmer/Officer Portal |
| **Interactive API Docs** | `/docs` or `/api/v1/docs` | Swagger UI with OpenAPI 3.1 specification |
| **Live AI/ML Yield Inference** | `POST /predict-yield` | Direct model inference endpoint with conformal intervals |
| **System Health Check** | `/health` or `/api/v1/health/ready` | Automated readiness probe |
| **Pre-configured Demo Login** | `officer@fin03.local` / `password123` | Instant access with full Loan Officer permissions |

---

## Step 0: Push Code to GitHub

To deploy on Render, Vercel, or Hugging Face Spaces, push your repository to your GitHub account:

1. Open [GitHub](https://github.com/new) and click **New Repository**.
2. Name it `terratrust-ai` and set visibility to **Public**.
3. In your terminal, run:
```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/terratrust-ai.git
git branch -M main
git push -u origin main
```

---

## Option 1: 1-Click Free Cloud Deployment on Render (Recommended)

Render offers free web service hosting with automatic HTTPS, zero configuration, and Docker support.

### Method A — Using Render Blueprint (`render.yaml`):
1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository `terratrust-ai`.
4. Render will automatically detect `render.yaml` and configure the web service with Docker.
5. Click **Apply**. In 2–3 minutes, your live URL will be ready (e.g. `https://terratrust-ai.onrender.com`).

### Method B — Manual Docker Web Service:
1. In Render, click **New +** -> **Web Service**.
2. Select your `terratrust-ai` GitHub repository.
3. Select **Docker** as the runtime.
4. Set Instance Type to **Free**.
5. Click **Deploy Web Service**.

> **Note**: Render will automatically build the React frontend, package the Python ML model, auto-initialize the SQLite database, and launch on port `10000`/`8000`.

---

## Option 2: Free 16GB ML Deployment on Hugging Face Spaces

Hugging Face Spaces is beloved by AI/ML hackathon judges and provides **free 16GB RAM + 2 vCPU** with no credit card required:

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set Space Name: `terratrust-ai`.
3. Select **Space SDK**: **Docker** (Blank).
4. Select **Public**.
5. Push your repository to the Hugging Face Git remote:
```bash
git remote add hf https://huggingface.co/spaces/<YOUR_HF_USERNAME>/terratrust-ai
git push hf main
```
6. Hugging Face Spaces will build the multi-stage Dockerfile and give you a permanent live URL: `https://<YOUR_HF_USERNAME>-terratrust-ai.hf.space`.

---

## Option 3: Two-Tier Deployment (Frontend on Vercel + Backend on Render)

If you prefer hosting the React Frontend separately on **Vercel**:

### 1. Deploy Backend on Render:
Deploy following Option 1, getting your backend URL (e.g., `https://terratrust-backend.onrender.com`).

### 2. Deploy Frontend on Vercel:
1. Go to [Vercel](https://vercel.com/new).
2. Import your `terratrust-ai` repository.
3. In Project Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. In **Environment Variables**, add:
   - `VITE_API_URL` = `https://terratrust-backend.onrender.com/api/v1`
5. Click **Deploy**. Your frontend is live on `https://terratrust-ai.vercel.app`.

---

## Option 4: Run Locally for Demo / Presentation

If you are presenting locally or recording a screen demonstration:

```bash
# From the TerraTrust-AI-main root folder:
python start_production.py
```

This single command will:
1. Verify and compile the React production bundle (`apps/web/dist`).
2. Initialize and seed the SQLite database (`apps/api/fin03.db`).
3. Load the ExtraTreesRegressor ML model.
4. Start the server on `http://localhost:8000`.

---

## 🧪 Validating the Live Deployment

After deploying, verify the key endpoints:

1. **Health Check**:
   ```bash
   curl https://<YOUR_DEPLOYED_URL>/health
   # Expected output: {"status":"ok","app":"FIN-03 Agricultural Credit Risk API","version":"1.0.0"}
   ```

2. **Crop Yield AI Model Prediction**:
   ```bash
   curl -X POST https://<YOUR_DEPLOYED_URL>/predict-yield \
     -H "Content-Type: application/json" \
     -d '{"Fertilizer": 120.0, "temp": 28.5, "N": 90.0, "P": 45.0, "K": 40.0}'
   # Expected output: {"predicted_yield": 11.9721, "unit": "tonnes_per_hectare", "model_used": "ExtraTreesRegressor", "status": "success"}
   ```

3. **Frontend Dashboard**:
   Open `https://<YOUR_DEPLOYED_URL>/` in your browser. Log in with `officer@fin03.local` / `password123`.
