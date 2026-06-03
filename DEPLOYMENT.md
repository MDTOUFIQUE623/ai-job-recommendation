# Deploy to Streamlit Community Cloud (Portfolio)

This app is a **Streamlit** project. The fastest free deployment for a portfolio demo is [Streamlit Community Cloud](https://share.streamlit.io/).

## Prerequisites

1. **GitHub repo** — this project is already at:
   `https://github.com/MDTOUFIQUE623/ai-job-recommendation`
2. **API keys** (keep private; never commit them):
   - [Google AI Studio](https://aistudio.google.com/apikey) → `GOOGLE_API_KEY` (prefer keys starting with `AIza`)
   - [Apify](https://console.apify.com/account/integrations) → `APIFY_API_TOKEN`

## Step 1 — Push latest code

```powershell
cd c:\Users\Lenovo\Downloads\deployed\1\ai-job-recommendation
git add .
git commit -m "Prepare app for Streamlit Cloud deployment"
git push origin main
```

## Step 2 — Create the Streamlit app

1. Open **https://share.streamlit.io/** and sign in with GitHub.
2. Click **Create app** → **From existing repo**.
3. Select repository: `MDTOUFIQUE623/ai-job-recommendation`.
4. Branch: `main`.
5. **Main file path:** `app.py`
6. **App URL** (optional): e.g. `ai-job-recommender` → `https://ai-job-recommender.streamlit.app`

## Step 3 — Add secrets

Before or right after deploy, open **Advanced settings → Secrets** and paste:

```toml
GOOGLE_API_KEY = "your-google-api-key"
APIFY_API_TOKEN = "your-apify-token"
```

Important:

- Keys must be **top-level** (not nested under `[sections]`).
- Use **quotes** around values in TOML.
- Do not use `.env` syntax (`KEY=value` without quotes) in the Secrets box.

Save and **Reboot app** if it was already running. If keys are missing, the app shows a configuration error instead of crashing.

### Gemini `ClientError` after upload

If resume upload fails with `google.genai.errors.ClientError`:

1. Regenerate the key at [Google AI Studio](https://aistudio.google.com/apikey) and update Secrets.
2. Prefer an **`AIza...`** key. Some accounts only get **`AQ....`** keys; those usually work, but if errors persist create a key in [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → **API key**.
3. Push the latest code (uses model `gemini-2.0-flash`, not the retired `gemini-2.0-flash-001`).
4. Check **Manage app → Logs** for the full error code (e.g. `401` = invalid key, `429` = quota).

## Step 4 — Share on your portfolio

Use the live URL in your resume/LinkedIn, e.g.:

> **AI Job Recommender** — Upload a PDF resume for Gemini-powered skill-gap analysis and live LinkedIn/Naukri job matches.  
> Live demo: `https://<your-app-name>.streamlit.app`

## Local secrets (development)

Create `.env` in the project root (not committed):

```env
GOOGLE_API_KEY=your_key
APIFY_API_TOKEN=your_token
```

Run locally:

```powershell
streamlit run app.py
```

## Costs and limits

- **Streamlit Cloud:** free tier for public apps.
- **Google Gemini:** free tier has quotas; heavy demo traffic may hit limits.
- **Apify:** job scraping uses Apify credits; each “Get Job Recommendations” run triggers actors (paid after free tier).

For portfolio demos, use a **sample PDF** and fetch jobs once per session to conserve Apify credits.

## Alternative hosts

| Platform | Fit |
|----------|-----|
| **Streamlit Cloud** | Best — built for this stack |
| **Railway / Render** | Run `streamlit run app.py` in a container; set env vars in dashboard |
| **Hugging Face Spaces** | Possible with a Docker/Streamlit Space; more setup |

MCP server (`mcp_server.py`) is for local/agent use; you do not need to deploy it for the portfolio web demo.
