"""Streamlit entrypoint for PennyWise frontend."""

import json
import os

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="PennyWise", page_icon="💰", layout="wide")

api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

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
            response = requests.get(f"{api_base_url}/health", timeout=5)
            response.raise_for_status()
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
                    response = requests.post(
                        f"{api_base_url}/api/v1/imports/transactions/csv",
                        files=files,
                        data=data,
                        timeout=30,
                    )
                    response.raise_for_status()
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
