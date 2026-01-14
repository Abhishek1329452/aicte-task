Deployment guide — Backend (FastAPI) & Frontend (Vite React)

Overview
- Backend: `backend` folder (FastAPI). Expects env vars in `.env` (Supabase URL & key, WEBHOOK_URL).
- Frontend: `frontend` folder (Vite + React). `VITE_API_BASE` config optional.

Option A — Quick (recommended): Vercel for frontend, Render (or Fly/Railway) for backend

1) Frontend → Vercel
- Push repo to GitHub.
- On Vercel, import the frontend project (select `frontend` directory).
- Set Environment Variable (if backend hosted at `https://api.example`):
  - `VITE_API_BASE=https://api.example`
- Deploy (Vercel auto-builds and serves the static site).

2) Backend → Render (or similar)
- Create a new Web Service on Render.
- Connect the GitHub repo and point the service to the `backend` folder.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Set Environment variables in Render dashboard: `SUPABASE_URL`, `SUPABASE_KEY` (service_role), `WEBHOOK_URL`.

Option B — Docker (build images and deploy anywhere)

Backend (local test):
```bash
cd backend
docker build -t hospital-receptionist-backend:latest .
docker run -e SUPABASE_URL="<url>" -e SUPABASE_KEY="<key>" -e WEBHOOK_URL="<url>" -p 8000:8000 hospital-receptionist-backend:latest
```

Frontend (local test):
```bash
cd frontend
docker build -t hospital-receptionist-frontend:latest .
docker run -p 80:80 hospital-receptionist-frontend:latest
```

Push to Docker Hub and deploy to your cloud provider (Cloud Run, ECS, DigitalOcean App Platform, etc.)

Notes & production considerations
- Use the Supabase `service_role` key only server-side (do not embed in frontend).
- Secure webhook endpoints and enable HTTPS.
- For production, keep RLS policies strict and avoid allowing anon writes.
- Add monitoring and logging for the backend.

Files added to repo for deployment
- `backend/Dockerfile` — container image for backend.
- `frontend/Dockerfile` — multi-stage build (Vite -> nginx) for frontend.

If you want, I can:
- Create GitHub Actions workflows to build and push Docker images, or
- Deploy the backend to Render or Fly for you (I will need access/confirmation), or
- Deploy frontend to Vercel (you can connect your GitHub and I can provide env settings).
