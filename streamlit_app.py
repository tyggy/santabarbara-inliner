import streamlit as st
import requests
from bs4 import BeautifulSoup
from premailer import transform

def main():
    st.title("Premailer-based CSS Inliner for Mailchimp")

    with st.form("premailer_form"):
        default_url = "https://www.santabarbarazencenter.org/events"
        url_input = st.text_input("Enter URL to fetch HTML from:", default_url)

        default_div_class = "eventlist eventlist--upcoming"
        div_class_input = st.text_input("Enter target div class:", default_div_class)

        # Additional options
        remove_classes = st.checkbox("Remove all class attributes in final HTML?", value=False)
        strip_important = st.checkbox("Strip '!important' declarations?", value=False)

        submitted = st.form_submit_button("Fetch & Inline CSS")

    if submitted:
        try:
            resp = requests.get(url_input, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            st.error(f"Error fetching URL: {e}")
            return

        # STEP 1: Parse the raw HTML to find the target <div>.
        soup = BeautifulSoup(resp.text, "html.parser")
        target_div = soup.find("div", class_=div_class_input)

        if not target_div:
            st.warning("No matching div found for that class.")
            return

        # We have two possible approaches to inlining:
        # A) Inline the entire page, then extract snippet.
        # B) Extract snippet first, then inline just that snippet.
        #
        # Usually, inlining the entire page is better if you want the snippet
        # to inherit site-wide <link> styles. Premailer tries to fetch them automatically.

        # --- Approach A: Inline ENTIRE PAGE, then extract snippet ---
        # This may give you more complete styling.
        # The 'transform' function from premailer automatically fetches external CSS
        # from <link> tags and inlines them if 'base_url' is provided.
        # You can pass various options, for example:
        #   base_url=url_input     ensures relative links are resolved
        #   remove_classes=remove_classes
        #   strip_important=strip_important
        #   etc...
        try:
            fully_inlined_html = transform(
                resp.text,
                base_url=url_input,
                remove_classes=remove_classes,
                strip_important=strip_important
            )
        except Exception as e:
            st.error(f"Premailer transform failed: {e}")
            return

        # Now parse the inlined result again and extract the snippet
        inlined_soup = BeautifulSoup(fully_inlined_html, "html.parser")
        final_snippet = inlined_soup.find("div", class_=div_class_input)

        if not final_snippet:
            st.warning("After inlining, the target div was not found! Possibly changed by JS or rewriting.")
            return

        snippet_html = str(final_snippet)

        st.subheader("Fully Inlined Snippet (Approach A):")
        st.code(snippet_html, language="html")

        # --- Approach B: Extract snippet first, then inline snippet only ---
        # This approach can be simpler but you might lose site-wide styling
        # that is outside local <style> tags. 
        #
        # snippet_only = str(target_div)
        # snippet_inlined = transform(
        #     snippet_only,
        #     base_url=url_input,
        #     remove_classes=remove_classes,
        #     strip_important=strip_important
        # )
        #
        # st.subheader("Snippet-Only Inlined (Approach B):")
        # st.code(snippet_inlined, language="html")


if __name__ == "__main__":
    main()