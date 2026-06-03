# AI Job System

A modern AI-powered job recommender system that analyzes your resume, identifies skill gaps, suggests a personalized career roadmap, and fetches real-time job recommendations (including internships) from LinkedIn and Naukri.com. The system features both a Streamlit web app and an MCP (Model Context Protocol) tool interface.

---

## Features

- **Resume Analysis**: Upload your PDF resume and get a summary of your skills, education, and experience.
- **Skill Gap Detection**: AI highlights missing skills, certifications, and experiences for better job opportunities.
- **Personalized Roadmap**: Get a future roadmap with recommended skills, certifications, and industry exposure.
- **Job Recommendations**: Fetches jobs from LinkedIn and Naukri.com using Apify actors, with support for internship filtering.
- **Direct Job Links**: All job recommendations include direct links to the job postings.
- **MCP Tool Integration**: Exposes job search as MCP tools for integration with other AI agents or workflows.

---

## Getting Started

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd AI-Job-system
```

### 2. Install Dependencies

You can use pip or your preferred Python environment manager:

```sh
pip install -r requirements.txt
```
Or, if using `pyproject.toml`:
```sh
pip install .
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with the following:

```
GOOGLE_API_KEY=your_google_genai_api_key
APIFY_API_TOKEN=your_apify_api_token
```

---

## Usage

### Streamlit Web App

Start the web app:

```sh
streamlit run app.py
```

- Upload your resume (PDF).
- View AI-generated summary, skill gaps, and roadmap.
- Click "Get Job Recommendations" to fetch jobs from LinkedIn and Naukri.

### MCP Server

Start the MCP server:

```sh
mcp dev mcp_server.py
```

This exposes two tools:
- `fetchlinkedin(listofkey)`: Fetch LinkedIn jobs for given keywords.
- `fetchnaukri(listofkey)`: Fetch Naukri jobs for given keywords.

You can connect to this server using any MCP-compatible client or agent.

---

## Project Structure

```
AI Job system/
├── app.py                # Streamlit web app
├── mcp_server.py         # MCP server exposing job search tools
├── src/
│   ├── helper.py         # PDF extraction and Google GenAI integration
│   ├── job_api.py        # Job fetching logic (LinkedIn, Naukri)
│   └── __init__.py
├── requirements.txt
├── pyproject.toml
├── .env                  # Your API keys (not committed)
└── README.md
```

---

## Key Files

- **app.py**: Main Streamlit app for resume analysis and job recommendations.
- **src/helper.py**: Functions for extracting text from PDF and interacting with Google GenAI (Gemini).
- **src/job_api.py**: Functions to fetch jobs from LinkedIn and Naukri using Apify actors, with internship filtering and job link extraction.
- **mcp_server.py**: Exposes job search as MCP tools for integration with other AI agents.

---

## Configuration

- **Google GenAI**: Used for resume summarization, skill gap analysis, and roadmap generation.
- **Apify**: Used to fetch real-time job listings from LinkedIn and Naukri.
- **Environment Variables**: Store your API keys in `.env`.

---

## Dependencies

- streamlit
- google-genai
- pymupdf
- python-dotenv
- apify-client
- mcp[cli]

(See `requirements.txt` or `pyproject.toml` for exact versions.)

---

## Customization

- To fetch only internship jobs, set the `internship` parameter to `True` in the job fetching functions.
- The MCP server can be extended with more tools as needed.

---

## Troubleshooting

- **MCP server connection issues**: Ensure you run `mcp dev mcp_server.py` and not just `mcp dev`. If a client expects a different entrypoint, update your MCP config or create a wrapper script.
- **API errors**: Make sure your `.env` file contains valid API keys for both Google GenAI and Apify.

---

## Deploy (Portfolio)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions to publish on **Streamlit Community Cloud** (free, public URL for recruiters).

Quick summary: push to GitHub → [share.streamlit.io](https://share.streamlit.io) → connect repo → main file `app.py` → add `GOOGLE_API_KEY` and `APIFY_API_TOKEN` in **Secrets**.

---

## License

MIT (or your preferred license)

---

## Acknowledgements

- [Google GenAI (Gemini)](https://pypi.org/project/google-genai/)
- [Apify](https://apify.com/)
- [Streamlit](https://streamlit.io/)
- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol)
