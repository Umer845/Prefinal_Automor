import streamlit as st
import premium, risk_profile, dashboard, qa

st.markdown("""
<style>
.st-emotion-cache-9ajs8n h4 {
    font-size: 14px;
    font-weight: 600;
    padding:0px;
}
.st-emotion-cache-zuyloh {
    border: none;
    border-radius: 0.5rem;
    padding: calc(-1px + 1rem);
    width: 100%;
    height: 100%;
    overflow: visible;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Inusrance Underwriting System", layout="wide")

if 'page' not in  st.session_state:
    st.session_state.page = "Dashboard"

st.sidebar.title("Navigation")
if st.sidebar.button("Dashboard"):
    st.session_state.page = "Dashboard"
if st.sidebar.button("Risk Profile"):
    st.session_state.page = "Risk Profile"
if st.sidebar.button("Premium"):
    st.session_state.page = "Premium"
if st.sidebar.button("QA"):
    st.session_state.page = "QA"


if st.session_state.page == "Dashboard":
   dashboard.show()
if st.session_state.page == "Risk Profile":
    risk_profile.show()
if st.session_state.page == "Premium":
    premium.show()
if st.session_state.page == "QA":
    qa.show()