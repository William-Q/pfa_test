"""Streamlit entrypoint for PennyWise frontend."""

import os

import requests
import streamlit as st

st.set_page_config(page_title="PennyWise", page_icon="💰", layout="wide")

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Expense Dashboard"], label_visibility="collapsed")

if page == "Expense Dashboard":
    st.title("Expense Dashboard")
    st.caption("Track backend availability before loading finance insights.")

    st.write(f"Connected API: `{api_base_url}`")

    if st.button("Check API status"):
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            response.raise_for_status()
            payload = response.json()
            status = payload.get("status", "unknown")
            st.success(f"API status: {status}")
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")
