import streamlit as st

#define display metric function
def display_metric(column, title, value, delta=None, emoji=""):
    with column:
        st.subheader(f"{title} {emoji}")
        st.metric(label=title, value=value, delta=delta, label_visibility='hidden', border=True)