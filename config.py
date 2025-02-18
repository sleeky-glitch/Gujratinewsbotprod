import os
from datetime import datetime

class Config:
    # Environment
    ENV = os.getenv("STREAMLIT_ENV", "development")

    # API Settings
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

    # GitHub Settings
    GITHUB_REPO_OWNER = "sleeky-glitch"
    GITHUB_REPO_NAME = "Gujratinewsbotprod"
    GITHUB_BRANCH = "main"

    # File Pattern
    NEWS_FILE_PATTERN = "dd_news_page_*.txt"

    # Cache Settings
    CACHE_TTL = 3600  # 1 hour

    # Model Parameters
    MODEL_PARAMS = {
        "max_new_tokens": 200,
        "temperature": 0.3,
        "top_p": 0.9,
        "return_full_text": False
    }

    # Date Settings
    DEFAULT_DATE_FORMAT = "%d-%m-%Y"

    # Translation Settings
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'gu': 'ગુજરાતી (Gujarati)'
    }

    # Highlighting Settings
    HIGHLIGHT_COLORS = {
        'primary': '#FFE082',    # Light yellow
        'secondary': '#A5D6A7',  # Light green
        'tertiary': '#90CAF9',   # Light blue
        'quaternary': '#F48FB1', # Light pink
        'emphasis': '#B39DDB'    # Light purple
    }

    @staticmethod
    def get_default_date():
        return datetime.now().strftime(Config.DEFAULT_DATE_FORMAT)
