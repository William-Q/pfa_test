"""Streamlit entrypoint for PennyWise frontend."""

import os

import requests
import streamlit as st

st.set_page_config(page_title="PennyWise", page_icon="💰", layout="wide")
st.title("PennyWise")
st.caption("Personal finance dashboard starter UI")

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
st.write(f"Connected API: `{api_base_url}`")

if st.button("Check API readiness"):
    try:
        response = requests.get(f"{api_base_url}/api/v1/health/ready", timeout=5)
        st.success(f"API responded with: {response.json()}")
    except requests.RequestException as exc:
        st.error(f"API unavailable: {exc}")
