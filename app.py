import streamlit as st
import requests
from datetime import datetime
from itertools import permutations
import logging
from typing import List, Dict, Optional
import re

from config import Config
from utils import (
    parse_article, parse_mixtral_response, validate_date, 
    format_search_results, create_custom_css
)
from github_utils import get_github_files, get_file_content, get_repo_stats
from translate_utils import (
    translate_text, detect_language, highlight_matching_text, 
    get_color_legend
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hugging Face API settings
headers = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"}

@st.cache_data(ttl=Config.CACHE_TTL)
def query_mixtral(prompt: str) -> Optional[str]:
    """Query the Mixtral model through Hugging Face API"""
    try:
        payload = {
            "inputs": prompt,
            "parameters": Config.MODEL_PARAMS
        }

        logger.info(f"Querying Mixtral with prompt: {prompt[:100]}...")
        response = requests.post(Config.API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()[0]["generated_text"]
    except Exception as e:
        logger.error(f"Error querying Mixtral: {str(e)}")
        st.error(f"Error querying Mixtral: {str(e)}")
        return None

def translate_query_and_extract(query: str, source_lang: str) -> tuple[List[str], Optional[str]]:
    """Translate query if needed and extract tags and date"""
    if source_lang == 'gu':
        query_en = translate_text(query, 'gu', 'en')
    else:
        query_en = query

    prompt = f"""Given the following news search query, extract relevant search tags and date information.
    Query: "{query_en}"

    Please format your response exactly as follows:
    Tags: [list of tags]
    Date: date in DD-MM-YYYY format (if mentioned)

    For example:
    Query: "cricket matches in gujarat last week"
    Tags: [cricket, matches, gujarat]
    Date: {(datetime.now()).strftime('%d-%m-%Y')}
    """

    response = query_mixtral(prompt)
    if response:
        return parse_mixtral_response(response)
    return [], None

def search_articles(tags: List[str], date: Optional[str] = None) -> List[Dict]:
    """Search for articles based on tags and date"""
    results = []
    files = get_github_files()

    for file in files:
        try:
            content = get_file_content(file['download_url'])
            
            # Create all possible combinations of tags
            all_combinations = []
            for r in range(1, len(tags) + 1):
                all_combinations.extend(permutations(tags, r))

            # Check if any combination of tags is present
            found = False
            for combo in all_combinations:
                if all(tag.lower() in content.lower() for tag in combo):
                    found = True
                    break

            if found:
                article_date_match = re.search(r"Date:\s*(\d{2}-\d{2}-\d{4})", content)
                if article_date_match:
                    article_date = datetime.strptime(article_date_match.group(1), "%d-%m-%Y")
                    
                    if date and validate_date(date):
                        query_date = datetime.strptime(date, "%d-%m-%Y")
                        if article_date >= query_date:
                            results.append(parse_article(content))
                    else:
                        results.append(parse_article(content))

        except Exception as e:
            logger.error(f"Error processing file {file['name']}: {str(e)}")
            continue

    return results

def initialize_session_state():
    """Initialize session state variables"""
    if 'show_original' not in st.session_state:
        st.session_state.show_original = {}
    if 'current_tags' not in st.session_state:
        st.session_state.current_tags = []
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

def main():
    st.set_page_config(
        page_title="Gujarati News Search Bot",
        page_icon="📰",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Inject custom CSS
    st.markdown(create_custom_css(), unsafe_allow_html=True)

    # Main title with both languages
    st.title("ગુજરાતી સમાચાર શોધ બોટ / Gujarati News Search Bot")

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col2:
        # Language selection
        st.markdown("### Language Settings")
        input_lang = st.radio(
            "Input Language:",
            ['English', 'ગુજરાતી (Gujarati)'],
            index=0
        )
        output_lang = st.radio(
            "Output Language:",
            ['English', 'ગુજરાતી (Gujarati)'],
            index=0
        )

        # Repository stats
        st.markdown("### Repository Stats")
        stats = get_repo_stats()
        st.write(f"Total Files: {stats['total_files']}")
        st.write(f"Last Updated: {stats['last_updated']}")

    with col1:
        # Convert language selection to codes
        input_lang_code = 'gu' if input_lang == 'ગુજરાતી (Gujarati)' else 'en'
        output_lang_code = 'gu' if output_lang == 'ગુજરાતી (Gujarati)' else 'en'

        # Search interface
        placeholder_text = (
            "તમારી ક્વેરી દાખલ કરો (દા.ત., 'ગુજરાતમાં ક્રિકેટ સમાચાર')"
            if input_lang_code == 'gu'
            else "Enter your query (e.g., 'cricket news in gujarat')"
        )

        query = st.text_input(placeholder_text)

        if query:
            with st.spinner('Processing your query...'):
                # Detect query language and extract information
                detected_lang = detect_language(query)
                tags, date = translate_query_and_extract(query, detected_lang)
                st.session_state.current_tags = tags

                # Show color legend for search terms
                st.markdown(get_color_legend(tags), unsafe_allow_html=True)

                # Search and format results
                results = search_articles(tags, date)
                formatted_results = format_search_results(results, tags, output_lang_code)

                # Display results count
                results_count = len(formatted_results)
                results_text = f"Found {results_count} articles"
                if output_lang_code == 'gu':
                    results_text = translate_text(results_text, 'en', 'gu')
                st.markdown(f"### {results_text}")

                # Display results
                for idx, result in enumerate(formatted_results):
                    with st.expander(f"{result['title']} ({result['date']})"):
                        st.markdown(f"[Read original article]({result['link']})")
                        st.markdown("---")

                        # Display content with highlighting
                        st.markdown(result['content'], unsafe_allow_html=True)

                        # Toggle button for original content
                        if result.get('original_content'):
                            toggle_key = f"toggle_{idx}"
                            if st.button(
                                "Show Original" if not st.session_state.show_original.get(idx) else "Show Translation",
                                key=toggle_key
                            ):
                                st.session_state.show_original[idx] = not st.session_state.show_original.get(idx, False)

                            if st.session_state.show_original.get(idx):
                                st.markdown("### Original Content")
                                st.markdown(highlight_matching_text(
                                    result['original_content'],
                                    tags
                                ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
