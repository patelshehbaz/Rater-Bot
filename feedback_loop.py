import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --- Load Data ---
csv_path = "feedback_log.csv"

if not Path(csv_path).exists():
    st.warning("No feedback data found.")
    st.stop()

df = pd.read_csv(csv_path)

# --- Dashboard Header ---
st.title("🧠 RAG Feedback Dashboard")
st.markdown("Track user corrections to RAG-generated answers.")

# --- Metrics ---
total = len(df)
wrong = total  # all entries are corrections
unique_questions = df["Question"].nunique()

st.metric("Total Feedback Entries", total)
st.metric("Unique Questions Corrected", unique_questions)

# --- Frequent Questions ---
st.subheader("📌 Most Frequently Corrected Questions")
most_common = df["Question"].value_counts().head(5)
st.bar_chart(most_common)

# --- Table View ---
st.subheader("📋 Full Feedback Log")
st.dataframe(df)

# --- Optional: Accuracy Trend (if timestamp column exists) ---
if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    trend = df.groupby(df["Timestamp"].dt.date).size()
    st.subheader("📈 Feedback Volume Over Time")
    st.line_chart(trend)
