import re

from apify_client import ApifyClient

from src.env import get_api_key

_apify_client = None


def _get_apify_client():
    global _apify_client
    if _apify_client is None:
        token = get_api_key("APIFY_API_TOKEN")
        if not token:
            raise RuntimeError("APIFY_API_TOKEN is not set")
        _apify_client = ApifyClient(token)
    return _apify_client

# Fetch LinkedIn jobs based on search query and location
# Added 'internship' parameter to filter for internships

def fetch_linkedin_jobs(search_query, location = "Bangalore", rows=60, internship=False):
    run_input = {
        "keyword": search_query,
        "location": location,
        "rows": rows,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        }
    }
    client = _get_apify_client()
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    # Filter for internships if requested
    if internship:
        jobs = [job for job in jobs if (
            (job.get('title') and re.search(r'intern', job['title'], re.IGNORECASE)) or
            (job.get('description') and re.search(r'intern', job['description'], re.IGNORECASE))
        )]
    # Ensure each job has a 'link' field
    for job in jobs:
        if 'link' not in job and 'applyUrl' in job:
            job['link'] = job['applyUrl']
    return jobs

# Fetch Naukri jobs based on search query and location
# Added 'internship' parameter to filter for internships

def fetch_naukri_jobs(search_query, location = "Bangalore", rows=60, internship=False):
    run_input = {
        "keyword": search_query,
        "maxJobs": rows,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "0",
    }
    client = _get_apify_client()
    run = client.actor("alpcnRV9YI9lYVPWk").call(run_input=run_input)
    jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    # Filter for internships if requested
    if internship:
        jobs = [job for job in jobs if (
            (job.get('title') and re.search(r'intern', job['title'], re.IGNORECASE)) or
            (job.get('tagsAndSkills') and re.search(r'intern', job['tagsAndSkills'], re.IGNORECASE))
        )]
    # Ensure each job has a 'url' field with full link
    for job in jobs:
        if 'jdURL' in job:
            job['url'] = job['jdURL']
    return jobs

 