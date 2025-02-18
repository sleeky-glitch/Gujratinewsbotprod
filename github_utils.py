import base64
from github import Github
from typing import List, Dict
import streamlit as st
from config import Config
import requests

@st.cache_data(ttl=3600)
def get_github_files() -> List[Dict]:
    """
    Fetch all news text files from GitHub repository
    """
    try:
        # Initialize GitHub client with access token
        g = Github(st.secrets["GITHUB_TOKEN"])

        # Get repository
        repo = g.get_repo(f"{Config.GITHUB_REPO_OWNER}/{Config.GITHUB_REPO_NAME}")

        # Get all files matching the pattern
        contents = repo.get_contents("")
        news_files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            elif file_content.name.startswith("dd_news_pahe_") and file_content.name.endswith(".txt"):
                news_files.append({
                    "name": file_content.name,
                    "path": file_content.path,
                    "download_url": file_content.download_url,
                    "sha": file_content.sha
                })

        return news_files
    except Exception as e:
        st.error(f"Error accessing GitHub repository: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_file_content(file_url: str) -> str:
    """
    Fetch content of a file from GitHub
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching file content: {str(e)}")
        return ""

def get_repo_stats() -> Dict:
    """
    Get repository statistics
    """
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(f"{Config.GITHUB_REPO_OWNER}/{Config.GITHUB_REPO_NAME}")

        return {
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "last_updated": repo.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": len(get_github_files())
        }
    except Exception as e:
        st.error(f"Error fetching repository stats: {str(e)}")
        return {
            "stars": 0,
            "forks": 0,
            "last_updated": "N/A",
            "total_files": 0
        }
