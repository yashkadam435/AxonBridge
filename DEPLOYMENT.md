# 🚀 AxonBridge Deployment Guide

This guide provides step-by-step instructions for deploying the complete AxonBridge application. The architecture is split into a **Frontend (Next.js)** and a **Backend (FastAPI)**, making it highly flexible for modern PaaS providers.

For the fastest, most reliable deployment, we recommend:
- **Frontend:** [Vercel](https://vercel.com/) (Native Next.js support, edge caching)
- **Backend:** [Render](https://render.com/) or [Railway](https://railway.app/) (Native Python Docker support)

---

## 🏗️ 1. Prepare the Application for Deployment

I have already updated the codebase to use environment variables for API routing. The frontend is now dynamically configured to point to your deployed backend using `NEXT_PUBLIC_API_URL`. The backend FastAPI server already has CORS configured to accept requests from any origin (`allow_origins=["*"]`).

### Verify your GitHub Repository
Ensure your entire `AxonBridge Project` folder is pushed to a GitHub repository. Both Vercel and Render will pull directly from your GitHub repo.

---

## 🌐 2. Deploying the Backend (FastAPI) on Render

Render is ideal because it natively supports Docker and Python, and offers a generous free tier for demos.

1. Create an account at [Render.com](https://render.com).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select your AxonBridge repository.
4. **Configuration:**
   - **Name:** `axonbridge-api` (or similar)
   - **Root Directory:** `apps/clinical-service` (This tells Render where your Python backend lives).
   - **Environment:** `Python 3` (or `Docker` if you want Render to use the `Dockerfile` inside that directory).
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - Add your Groq API Key: `GROQ_API_KEY` = `your_api_key_here`
6. Click **Create Web Service**.
7. Once the build finishes, Render will provide a URL (e.g., `https://axonbridge-api.onrender.com`). **Save this URL.**

*(Note: For the demo, the backend uses local JSON files for its database. Render's free tier has an ephemeral disk, meaning your created encounters and agents will reset if the server sleeps. This is completely fine for a demo presentation).*

---

## ⚡ 3. Deploying the Frontend (Next.js) on Vercel

Vercel is the creator of Next.js and provides the best hosting experience for the frontend.

1. Create an account at [Vercel.com](https://vercel.com).
2. Click **Add New... -> Project**.
3. Import your AxonBridge GitHub repository.
4. **Configuration:**
   - **Project Name:** `axonbridge-web`
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `apps/web` (Click 'Edit' and select the `apps/web` folder).
5. **Environment Variables:**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: The Render backend URL you saved earlier (e.g., `https://axonbridge-api.onrender.com`).
   - *(Make sure you do NOT include a trailing slash in the URL)*.
6. Click **Deploy**.
7. Vercel will build your Next.js application. Once complete, it will provide you with a live URL (e.g., `https://axonbridge-web.vercel.app`).

---

## 🐳 Alternative: Self-Hosting (Docker Compose)
If you are deploying to a private VPS (like DigitalOcean, AWS EC2, or an on-premise hospital server), you can run the entire stack exactly as it runs locally.

1. SSH into your server.
2. Clone the repository.
3. Install `docker` and `docker-compose`.
4. Run:
   ```bash
   docker compose -f infrastructure/docker/docker-compose.yml up -d --build
   ```
5. Configure Nginx or Caddy as a reverse proxy to route port `80` to the web container (port `3000`) and port `8004` to the API container.

---

## ✅ Deployment Checklist

- [x] Backend deployed and running (Check `https://<backend-url>/health` - should return `{"status": "ok"}`).
- [x] Frontend deployed on Vercel.
- [x] Frontend `NEXT_PUBLIC_API_URL` variable correctly set to the backend URL.
- [x] Groq API key set in the backend environment variables.
- [x] Successfully create a new Agent Session on the live URL.

Your application is now fully deployed and ready for your client demo!
