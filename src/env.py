import os

from dotenv import load_dotenv

_SECRET_KEYS = ("GOOGLE_API_KEY", "APIFY_API_TOKEN")


def load_api_keys() -> None:
    """Load API keys from Streamlit secrets and/or .env into os.environ."""
    try:
        import streamlit as st

        for key in _SECRET_KEYS:
            if key in st.secrets:
                value = str(st.secrets[key]).strip()
                if value:
                    os.environ[key] = value
    except Exception:
        pass

    load_dotenv(override=False)


def get_api_key(name: str) -> str | None:
    value = os.getenv(name)
    if not value:
        return None
    value = value.strip()
    return value or None
