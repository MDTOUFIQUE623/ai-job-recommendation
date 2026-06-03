from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import re
 
load_dotenv()

apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

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
    run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
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
    run = apify_client.actor("alpcnRV9YI9lYVPWk").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
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

 