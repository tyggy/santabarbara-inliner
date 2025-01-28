import streamlit as st
import requests
from bs4 import BeautifulSoup
from inlinestyler.utils import inline_css
from urllib.parse import urljoin

st.title("Email HTML Inliner ✨")

# Input fields
with st.form("input_form"):
    url = st.text_input("Page URL", value="https://www.santabarbarazencenter.org/events")
    target_class = st.text_input("Target Div Class", value="sqs-events-collection-list events events-list events-stacked")
    submitted = st.form_submit_button("Process HTML")

if submitted:
    try:
        # Fetch HTML
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract CSS
        css_links = [urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet')]
        combined_css = "\n".join([requests.get(css).text for css in css_links])

        # Extract target div
        target_div = soup.find('div', class_=target_class)
        if not target_div:
            st.error("Target div not found!")
        else:
            # Inline CSS
            inlined_html = inline_css(str(target_div), combined_css)
            
            # Display output
            st.success("✅ Ready for Mailchimp!")
            st.code(inlined_html, language="html")
            st.download_button("Download HTML", inlined_html, file_name="mailchimp-ready.html")

    except Exception as e:
        st.error(f"Error: {str(e)}")