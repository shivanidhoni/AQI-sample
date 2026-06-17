import pandas as pd
import streamlit as st
import os


@st.cache_data(show_spinner=False)
def load_data():

    try:
        # -----------------------------
        # BASE PATH RESOLUTION
        # -----------------------------
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        file_path = os.path.join(
            base_dir,
            "data",
            "dehradun_master_dataset.parquet"
        )

        df = pd.read_parquet(file_path)

        # -----------------------------
        # CLEAN COLUMN NAMES
        # -----------------------------
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        # -----------------------------
        # DROP FULLY EMPTY ROWS (IMPORTANT)
        # -----------------------------
        df = df.dropna(how="all")

        # -----------------------------
        # DATETIME CONVERSION
        # -----------------------------
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["datetime"],
                errors="coerce"
            )

        # -----------------------------
        # ZONE CLEANING (CRITICAL FIX)
        # -----------------------------
        if "zone" in df.columns:
            df["zone"] = (
                df["zone"]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace("nan", pd.NA)
            )

            # remove invalid zones
            df = df.dropna(subset=["zone"])

        # -----------------------------
        # AQI COLUMN SAFETY CHECK
        # -----------------------------
        if "eu_aqi" in df.columns:
            df["eu_aqi"] = pd.to_numeric(df["eu_aqi"], errors="coerce")

        if "pm25" in df.columns:
            df["pm25"] = pd.to_numeric(df["pm25"], errors="coerce")

        # -----------------------------
        # REMOVE BAD ROWS
        # -----------------------------
        if "eu_aqi" in df.columns:
            df = df.dropna(subset=["eu_aqi"])

        return df

    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return pd.DataFrame()