import os

import streamlit as st

from src.env import get_api_key, load_api_keys

load_api_keys()

from src.helper import analyze_resume, extract_text_from_pdf
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs


st.set_page_config(
    page_title="Job Recommender",
    page_icon="🤖",
    layout="wide",
)
st.title("📄 AI Job Recommender")
st.markdown(
    "Upload your resume and get job recommendations based on your skills and experience "
    "from LinkedIn and Naukri."
)

if not get_api_key("GOOGLE_API_KEY") or not get_api_key("APIFY_API_TOKEN"):
    st.error(
        "API keys are not configured. For local runs, add `GOOGLE_API_KEY` and "
        "`APIFY_API_TOKEN` to a `.env` file. On Streamlit Cloud, add them under "
        "**App settings → Secrets**."
    )
    st.stop()

uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])

if uploaded_file:
    file_key = f"{uploaded_file.name}:{uploaded_file.size}"

    try:
        if st.session_state.get("analysis_file") != file_key:
            with st.spinner("Extracting text from your resume..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                if not resume_text.strip():
                    st.error("Could not read text from this PDF. Try another file or a text-based PDF.")
                    st.stop()

            with st.spinner("Analyzing resume with AI (one API call)..."):
                analysis = analyze_resume(resume_text)

            st.session_state["analysis_file"] = file_key
            st.session_state["analysis"] = analysis
        else:
            analysis = st.session_state["analysis"]

        summary = analysis["summary"]
        gaps = analysis["skill_gaps"]
        roadmap = analysis["roadmap"]
        job_keywords = analysis["job_keywords"]

    except RuntimeError as exc:
        st.error(str(exc))
        if "429" in str(exc):
            st.info(
                "Tip: Free Gemini quota resets daily. For portfolio demos, wait a few minutes "
                "between tests or enable billing on your Google AI project."
            )
        st.stop()

    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summary}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gaps}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(
        f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>",
        unsafe_allow_html=True,
    )

    st.success("✅ Analysis Completed Successfully!")

    if st.button("🔎 Get Job Recomendations"):
        search_keywords_clean = job_keywords.replace("\n", "").strip()
        st.success(f"Job keywords: {search_keywords_clean}")

        try:
            with st.spinner("Fetching jobs from LinkedIn and Naukri..."):
                linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows=30)
                naukri_jobs = fetch_naukri_jobs(search_keywords_clean, rows=30)
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('link')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

        st.markdown("---")
        st.header("💼 Top Naukri Jobs (India)")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}*")
                st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('url')})")
                st.markdown("---")
        else:
            st.warning("No Naukri jobs found.")
