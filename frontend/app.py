"""Streamlit entrypoint for PennyWise frontend."""

import json
import os
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="PennyWise", page_icon="💰", layout="wide")

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")


def _build_api_candidates(base_url: str) -> list[str]:
    candidates = [base_url.rstrip("/")]
    parsed = urlparse(base_url)
    if parsed.hostname == "backend":
        candidates.extend(
            [
                "http://localhost:8000",
                "http://host.docker.internal:8000",
            ]
        )

    unique_candidates: list[str] = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return unique_candidates


API_CANDIDATES = _build_api_candidates(api_base_url)


def _request_api(method: str, path: str, **kwargs: object) -> requests.Response:
    errors: list[str] = []
    for candidate in API_CANDIDATES:
        try:
            response = requests.request(method, f"{candidate}{path}", **kwargs)
            response.raise_for_status()
            if candidate != API_CANDIDATES[0]:
                st.warning(f"Using fallback API endpoint: {candidate}")
            return response
        except requests.RequestException as exc:
            errors.append(f"{candidate}: {exc}")

    raise requests.RequestException(" ; ".join(errors))

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["Expense Dashboard", "CSV Import"],
        label_visibility="collapsed",
    )

if page == "Expense Dashboard":
    st.title("Expense Dashboard")
    st.caption("Track backend availability before loading finance insights.")

    st.write(f"Connected API: `{api_base_url}`")

    if st.button("Check API status"):
        try:
            response = _request_api("GET", "/health", timeout=5)
            payload = response.json()
            status = payload.get("status", "unknown")
            st.success(f"API status: {status}")
        except requests.RequestException as exc:
            st.error(f"API unavailable: {exc}")

if page == "CSV Import":
    st.title("CSV Import")
    st.caption("Upload transaction CSV and map columns before importing.")
    st.write(f"Connected API: `{api_base_url}`")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        csv_bytes = uploaded_file.getvalue()
        try:
            dataframe = pd.read_csv(uploaded_file)
        except Exception as exc:  # parser errors vary by pandas version
            st.error(f"Unable to read CSV: {exc}")
            st.stop()

        if dataframe.empty:
            st.warning("CSV has no rows to import.")
            st.stop()

        st.subheader("Preview")
        st.dataframe(dataframe.head(20), use_container_width=True)

        csv_columns = dataframe.columns.tolist()
        st.subheader("Column Mapping")

        col1, col2, col3 = st.columns(3)
        with col1:
            date_column = st.selectbox("Date column", csv_columns)
        with col2:
            amount_column = st.selectbox("Amount column", csv_columns)
        with col3:
            description_column = st.selectbox("Description column", csv_columns)

        mapping_config = {
            "date": date_column,
            "amount": amount_column,
            "description": description_column,
        }

        if len({date_column, amount_column, description_column}) < 3:
            st.warning("Please map each field to a different CSV column.")

        if st.button("Import CSV", type="primary"):
            if len({date_column, amount_column, description_column}) < 3:
                st.error("Mappings must use three different columns.")
                st.stop()

            files = {
                "file": (uploaded_file.name, csv_bytes, "text/csv"),
            }
            data = {
                "mapping_config": json.dumps(mapping_config),
            }

            with st.spinner("Importing..."):
                try:
                    response = _request_api(
                        "POST",
                        "/api/v1/imports/transactions/csv",
                        files=files,
                        data=data,
                        timeout=30,
                    )
                    payload = response.json()
                except requests.RequestException as exc:
                    st.error(f"Import failed: {exc}")
                else:
                    st.success("Import complete")
                    st.subheader("Import Summary")
                    st.write(f"Total rows: {payload.get('total_rows', 0)}")
                    st.write(f"Inserted rows: {payload.get('inserted_rows', 0)}")
                    st.write(f"Failed rows: {payload.get('failed_rows', 0)}")

                    error_samples = payload.get("error_samples", [])
                    if error_samples:
                        st.write("Errors:")
                        for error in error_samples:
                            st.write(f"- {error}")
