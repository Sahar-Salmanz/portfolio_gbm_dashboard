import streamlit as st
 
_CSS = """
<style>
/* Risk level badges — only custom thing we need */
.badge-low    { background:#dcfce7; color:#166534; padding:2px 10px; border-radius:4px; font-size:13px; font-weight:600; }
.badge-medium { background:#fef9c3; color:#854d0e; padding:2px 10px; border-radius:4px; font-size:13px; font-weight:600; }
.badge-high   { background:#fee2e2; color:#991b1b; padding:2px 10px; border-radius:4px; font-size:13px; font-weight:600; }
</style>
"""
 
 
def inject_css() -> None:
    """Inject global custom CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)
 