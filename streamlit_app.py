import streamlit as st
import requests
from bs4 import BeautifulSoup
from inlinestyler.utils import inline_css
from urllib.parse import urljoin

st.title("Email HTML Inliner ✨")

def process_html(url, target_class):
    # Fetch HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # <-- Use lxml parser explicitly
    
    # Extract CSS
    css_links = [urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet')]
    combined_css = "\n".join([requests.get(css).text for css in css_links])
    
    # Extract target div
    target_div = soup.find('div', class_=target_class)
    if not target_div:
        return None
    return inline_css(str(target_div), combined_css)

with st.form("input_form"):
    url = st.text_input("Page URL", value="https://www.santabarbarazencenter.org/events")
    target_class = st.text_input("Target Div Class", 
                               value="sqs-events-collection-list events events-list events-stacked")
    submitted = st.form_submit_button("Process HTML")

if submitted:
    try:
        result = process_html(url, target_class)
        if result:
            st.success("✅ Ready for Mailchimp!")
            st.code(result, language="html")
            st.download_button("Download HTML", result, file_name="mailchimp-ready.html")
        else:
            st.error("Target div not found!")
    except Exception as e:
        st.error(f"Error: {str(e)}")