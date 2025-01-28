import streamlit as st
import requests
from bs4 import BeautifulSoup
from inlinestyler.utils import inline_css  # Changed import
from urllib.parse import urljoin

st.title("Email HTML Inliner ✨")

def process_html(url, target_class):
    # Fetch HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Extract and combine CSS
    css_links = [urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet')]
    combined_css = "\n".join([requests.get(css).text for css in css_links])
    
    # Create full HTML document with CSS
    target_div = soup.find('div', class_=target_class)
    if not target_div:
        return None
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>{combined_css}</style>
    </head>
    <body>
        {target_div}
    </body>
    </html>
    """
    
    # Inline CSS (now only 1 argument)
    return inline_css(full_html)  # <-- Fixed call

# Rest of your Streamlit form code remains the same...

