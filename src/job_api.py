import os
import re

from apify_client import ApifyClient
from apify_client._errors import ApifyApiError

from src.env import get_api_key

_apify_client = None

# Old bebity actor (BHzefUZlZRKWxkTck) needs a $29.99/mo subscription — not for free Apify accounts.
LINKEDIN_ACTOR = os.getenv("LINKEDIN_ACTOR", "kaix/linkedin-jobs-scraper")
NAUKRI_ACTOR = os.getenv("NAUKRI_ACTOR", "automation-lab/naukri-scraper")
DEFAULT_MAX_JOBS = 15


def _get_apify_client():
    global _apify_client
    if _apify_client is None:
        token = get_api_key("APIFY_API_TOKEN")
        if not token:
            raise RuntimeError("APIFY_API_TOKEN is not set")
        _apify_client = ApifyClient(token)
    return _apify_client


def _primary_keyword(search_query: str) -> str:
    """Use the first keyword from a comma-separated list."""
    parts = [p.strip() for p in search_query.split(",") if p.strip()]
    return parts[0] if parts else "software engineer"


def _format_apify_error(exc: ApifyApiError, actor_id: str) -> str:
    message = str(exc)
    lower = message.lower()
    if any(
        word in lower
        for word in ("payment", "subscription", "billing", "insufficient", "credit", "quota")
    ):
        hint = (
            "This scraper needs Apify credits or a pay-per-use actor. "
            "Check https://console.apify.com/billing — free accounts get ~$5/month. "
            f"Current LinkedIn actor: `{LINKEDIN_ACTOR}`."
        )
    elif "401" in message or "unauthorized" in lower or "invalid" in lower:
        hint = "Check APIFY_API_TOKEN in Streamlit Secrets."
    else:
        hint = "See https://console.apify.com/actors/runs for run logs."
    return f"Apify error ({actor_id}): {message}. {hint}"


def _run_actor(actor_id: str, run_input: dict, timeout_secs: int = 300) -> list:
    client = _get_apify_client()
    try:
        run = client.actor(actor_id).call(
            run_input=run_input,
            timeout_secs=timeout_secs,
        )
        return list(client.dataset(run["defaultDatasetId"]).iterate_items())
    except ApifyApiError as exc:
        raise RuntimeError(_format_apify_error(exc, actor_id)) from exc


def _normalize_linkedin_jobs(raw_jobs: list) -> list:
    jobs = []
    for job in raw_jobs:
        title = job.get("title")
        if not title:
            continue
        jobs.append(
            {
                "title": title,
                "companyName": job.get("company") or job.get("companyName") or "—",
                "location": job.get("location") or "—",
                "link": job.get("jobUrl") or job.get("link") or job.get("applyUrl"),
            }
        )
    return jobs


def _normalize_naukri_jobs(raw_jobs: list) -> list:
    jobs = []
    for job in raw_jobs:
        title = job.get("title") or job.get("jobTitle")
        if not title:
            continue
        url = job.get("jobUrl") or job.get("url") or job.get("jdURL")
        jobs.append(
            {
                "title": title,
                "companyName": job.get("company") or job.get("companyName") or "—",
                "location": job.get("location") or "—",
                "url": url,
            }
        )
    return jobs


def fetch_linkedin_jobs(search_query, location="Bangalore", rows=DEFAULT_MAX_JOBS, internship=False):
    keyword = _primary_keyword(search_query)
    max_jobs = min(rows, DEFAULT_MAX_JOBS)

    run_input = {
        "keywords": keyword,
        "location": location,
        "maxJobs": max_jobs,
        "fetchDetails": False,
    }
    raw = _run_actor(LINKEDIN_ACTOR, run_input)
    jobs = _normalize_linkedin_jobs(raw)

    if internship:
        jobs = [
            job
            for job in jobs
            if job.get("title") and re.search(r"intern", job["title"], re.IGNORECASE)
        ]
    return jobs


def fetch_naukri_jobs(search_query, location="bangalore", rows=DEFAULT_MAX_JOBS, internship=False):
    keyword = _primary_keyword(search_query)
    max_jobs = min(rows, DEFAULT_MAX_JOBS)

    run_input = {
        "keyword": keyword,
        "location": location.lower(),
        "maxJobs": max_jobs,
    }
    raw = _run_actor(NAUKRI_ACTOR, run_input)
    jobs = _normalize_naukri_jobs(raw)

    if internship:
        jobs = [
            job
            for job in jobs
            if job.get("title") and re.search(r"intern", job["title"], re.IGNORECASE)
        ]
    return jobs
