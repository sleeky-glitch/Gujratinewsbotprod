from deep_translator import GoogleTranslator
import streamlit as st
import re
from typing import List, Dict
from config import Config

@st.cache_data(ttl=3600)
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text between English and Gujarati
    """
    if not text or source_lang == target_lang:
        return text

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return text

def detect_language(text: str) -> str:
    """
    Detect if text is English or Gujarati
    """
    gujarati_chars = len([c for c in text if '\u0a80' <= c <= '\u0aff'])
    return 'gu' if gujarati_chars > len(text) * 0.3 else 'en'

def highlight_matching_text(content: str, search_terms: List[str], case_sensitive: bool = False) -> str:
    """
    Highlight matching terms in content using custom colors
    """
    highlighted_content = content
    colors = list(Config.HIGHLIGHT_COLORS.values())

    for idx, term in enumerate(search_terms):
        if not term.strip():
            continue

        color = colors[idx % len(colors)]

        if not case_sensitive:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(term))

        highlighted_content = pattern.sub(
            lambda m: f'<span style="background-color: {color}; padding: 0 2px; border-radius: 3px;">{m.group()}</span>',
            highlighted_content
        )

    return highlighted_content

@st.cache_data(ttl=3600)
def get_color_legend(search_terms: List[str]) -> str:
    """
    Generate HTML for color legend
    """
    if not search_terms:
        return ""

    colors = list(Config.HIGHLIGHT_COLORS.values())
    legend_html = "<div style='margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;'>"
    legend_html += "<p style='margin: 0 0 5px 0;'><strong>Search Terms:</strong></p>"

    for idx, term in enumerate(search_terms):
        if term.strip():
            color = colors[idx % len(colors)]
            legend_html += f"<span style='margin-right: 10px; background-color: {color}; padding: 2px 5px; border-radius: 3px;'>{term}</span>"

    legend_html += "</div>"
    return legend_html
