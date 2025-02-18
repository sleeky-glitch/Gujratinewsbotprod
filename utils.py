import logging
import re
from datetime import datetime
from typing import Tuple, List, Dict, Optional
import streamlit as st
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_article(content: str) -> Dict[str, str]:
    """Parse article details from content"""
    title_match = re.search(r"Title:\s*(.+)", content)
    date_match = re.search(r"Date:\s*(.+)", content)
    link_match = re.search(r"Link:\s*(.+)", content)

    return {
        "title": title_match.group(1) if title_match else "No Title",
        "date": date_match.group(1) if date_match else "No Date",
        "link": link_match.group(1) if link_match else "#",
        "content": content
    }

def parse_mixtral_response(response: str) -> Tuple[List[str], Optional[str]]:
    """Parse tags and date from Mixtral response"""
    tags = []
    date = None

    # Extract tags
    tags_match = re.search(r"Tags:\s*\[(.*?)\]", response)
    if tags_match:
        tags = [tag.strip() for tag in tags_match.group(1).split(',')]

    # Extract date
    date_match = re.search(r"Date:\s*(\d{2}-\d{2}-\d{4})", response)
    if date_match:
        date = date_match.group(1)

    return tags, date

def validate_date(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def format_search_results(results: List[Dict], tags: List[str], target_lang: str) -> List[Dict]:
    """Format search results with translations and highlighting"""
    formatted_results = []

    for result in results:
        formatted_result = result.copy()

        # Translate title if needed
        if target_lang != detect_language(result['title']):
            formatted_result['title'] = translate_text(
                result['title'],
                detect_language(result['title']),
                target_lang
            )

        # Format content with highlighting and translation
        formatted_result = format_article_content(formatted_result, tags, target_lang)
        formatted_results.append(formatted_result)

    return formatted_results

def format_article_content(article: Dict, tags: List[str], target_lang: str) -> Dict:
    """Format and translate article content"""
    content = article['content']
    source_lang = detect_language(content)

    # Store original content
    article['original_content'] = content
    article['original_lang'] = source_lang

    # Translate if needed
    if target_lang != source_lang:
        translated_content = translate_text(content, source_lang, target_lang)
        # Highlight in translated content
        highlighted_translated = highlight_matching_text(translated_content, tags)
        article['content'] = highlighted_translated
    else:
        # Highlight in original content
        article['content'] = highlight_matching_text(content, tags)

    return article

def create_custom_css() -> str:
    """Generate custom CSS for the application"""
    css = """
    <style>
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .search-result {
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .color-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 10px 0;
    }
    .legend-item {
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    .translation-toggle {
        margin-top: 10px;
        padding: 5px;
        background-color: #f0f0f0;
        border-radius: 3px;
    }
    </style>
    """
    return css
