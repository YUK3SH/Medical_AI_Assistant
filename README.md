# Quick deploy: MedicAI (fastest: Render / Heroku)

This repo contains a small Flask app that uses Azure Document Intelligence and Azure OpenAI. The fastest way to get it running with minimal code changes is to deploy it as a normal web service (Render or Heroku) rather than converting to Vercel serverless functions.

Prerequisites
- A running GitHub repo containing this project
- Azure resources & keys (Document Intelligence, Azure OpenAI, Storage)

Required environment variables (see `.env.example`)
- `AZURE_STORAGE_CONNECTION_STRING`
- `DOCUMENT_INTELLIGENCE_ENDPOINT`
- `DOCUMENT_INTELLIGENCE_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT`

Local test (quick)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# set env vars (use real values when you want Azure calls to work)
$env:AZURE_OPENAI_ENDPOINT="https://example"
$env:AZURE_OPENAI_KEY="your-key"
$env:AZURE_OPENAI_DEPLOYMENT="deployment-name"
python app.py
# open http://localhost:5000
```

Deploy to Render (recommended)
1. Go to Render and create a new **Web Service**.
2. Connect your GitHub repo and pick the branch.
3. Build/Start settings:
   - Build command: leave blank (Render will install from `requirements.txt`)
   - Start command: `gunicorn app:app`
4. Add all required environment variables in the Render dashboard (Env Vars section).
5. Deploy and watch logs; once live test `/` and `/chat` endpoints.

Deploy to Heroku
```bash
heroku create my-medicai
git push heroku main
heroku config:set AZURE_OPENAI_KEY="..." AZURE_OPENAI_ENDPOINT="..." \
  AZURE_OPENAI_DEPLOYMENT="..." DOCUMENT_INTELLIGENCE_KEY="..." \
  DOCUMENT_INTELLIGENCE_ENDPOINT="..." AZURE_STORAGE_CONNECTION_STRING="..."
heroku ps:scale web=1
heroku logs --tail
```

Notes
- The app will raise runtime errors if environment variables are missing; set them in the host's dashboard.
- Vercel requires refactoring to serverless functions; that takes longer. This README focuses on fastest deployment with minimal changes.
