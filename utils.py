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
    """
    Parse article details from content with improved error handling and date parsing
    """
    try:
        # Split content into sections
        sections = content.split("--------------------------------------------------------------------------------")

        # Process the first (or only) section
        section = sections[0].strip()

        # Extract components with robust pattern matching
        title_match = re.search(r"Title:\s*(.+?)(?=Date:|$)", section, re.DOTALL)
        date_match = re.search(r"Date:\s*(.+?)(?=Link:|$)", section, re.DOTALL)
        link_match = re.search(r"Link:\s*(.+?)(?=Content:|$)", section, re.DOTALL)
        content_match = re.search(r"Content:\s*(.+?)$", section, re.DOTALL)

        # Format date consistently
        date_str = date_match.group(1).strip() if date_match else "No Date"
        try:
            # Parse and reformat date for consistency
            parsed_date = datetime.strptime(date_str, "%d-%m-%Y | %I:%M %p")
            formatted_date = parsed_date.strftime("%d-%m-%Y %I:%M %p")
        except ValueError:
            formatted_date = date_str

        return {
            "title": title_match.group(1).strip() if title_match else "No Title",
            "date": formatted_date,
            "link": link_match.group(1).strip() if link_match else "#",
            "content": content_match.group(1).strip() if content_match else content,
            "raw_content": content  # Store original content for reference
        }
    except Exception as e:
        logger.error(f"Error parsing article: {str(e)}")
        return {
            "title": "Error Parsing Article",
            "date": "No Date",
            "link": "#",
            "content": content,
            "raw_content": content
        }

def parse_mixtral_response(response: str) -> Tuple[List[str], Optional[str]]:
    """
    Parse tags and date from Mixtral response with improved handling
    """
    tags = []
    date = None

    try:
        # Extract tags with better pattern matching
        tags_match = re.search(r"Tags:\s*\[(.*?)\]", response, re.IGNORECASE)
        if tags_match:
            # Clean and validate tags
            tags = [
                tag.strip().lower()
                for tag in tags_match.group(1).split(',')
                if tag.strip()
            ]

        # Extract date with flexible format matching
        date_match = re.search(r"Date:\s*(\d{2}-\d{2}-\d{4})", response)
        if date_match:
            # Validate date format
            if validate_date(date_match.group(1)):
                date = date_match.group(1)

        return tags, date
    except Exception as e:
        logger.error(f"Error parsing Mixtral response: {str(e)}")
        return [], None

def validate_date(date_str: str) -> bool:
    """
    Validate date string format with enhanced error handling
    """
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except (ValueError, TypeError):
        return False

def format_search_results(results: List[Dict], tags: List[str], target_lang: str) -> List[Dict]:
    """
    Format search results with translations and highlighting with improved handling
    """
    formatted_results = []

    for result in results:
        try:
            formatted_result = result.copy()

            # Detect language of title and content
            title_lang = detect_language(result['title'])

            # Translate title if needed
            if target_lang != title_lang:
                formatted_result['title'] = translate_text(
                    result['title'],
                    title_lang,
                    target_lang
                )

            # Format content with highlighting and translation
            formatted_result = format_article_content(formatted_result, tags, target_lang)
            formatted_results.append(formatted_result)

        except Exception as e:
            logger.error(f"Error formatting result: {str(e)}")
            formatted_results.append(result)  # Add original result if formatting fails

    return formatted_results

def format_article_content(article: Dict, tags: List[str], target_lang: str) -> Dict:
    """
    Format and translate article content with improved handling
    """
    try:
        content = article.get('content', '')
        source_lang = detect_language(content)

        # Store original content and language
        article['original_content'] = content
        article['original_lang'] = source_lang

        # Translate if needed and target language is different
        if target_lang != source_lang:
            translated_content = translate_text(content, source_lang, target_lang)
            # Highlight in translated content if there are tags
            if tags:
                highlighted_translated = highlight_matching_text(translated_content, tags)
                article['content'] = highlighted_translated
            else:
                article['content'] = translated_content
        else:
            # Highlight in original content if there are tags
            if tags:
                article['content'] = highlight_matching_text(content, tags)

        return article
    except Exception as e:
        logger.error(f"Error formatting article content: {str(e)}")
        return article

def create_custom_css() -> str:
    """
    Generate custom CSS for the application with improved styling
    """
    return """
    <style>
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .search-result {
        padding: 15px;
        margin: 12px 0;
        border: 1px solid #eee;
        border-radius: 8px;
        background-color: #ffffff;
    }
    .color-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 15px 0;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 6px;
    }
    .legend-item {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.9em;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .translation-toggle {
        margin-top: 12px;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #eee;
    }
    .highlight {
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 500;
    }
    </style>
    """
