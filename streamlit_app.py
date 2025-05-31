import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------- Grundfunktioner ----------
def get_filename(user):
    return f"logg_{user}.csv"

def logga_pass(user, ovning, mg, vikt, reps, sets, kommentar):
    fil = get_filename(user)
    rad = {
        "Datum": datetime.today().strftime('%Y-%m-%d'),
        "\u00d6vning": ovning,
        "Muskelgrupp": mg,
        "Vikt": vikt,
        "Reps": reps,
        "Set": sets,
        "Kommentar": kommentar
    }
    df = pd.DataFrame([rad])
    if os.path.exists(fil):
        df.to_csv(fil, mode="a", index=False, header=False)
    else:
        df.to_csv(fil, mode="w", index=False, header=True)

def senaste_pass(user):
    fil = get_filename(user)
    if not os.path.exists(fil):
        return pd.DataFrame()
    return pd.read_csv(fil).tail(10)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Tr\u00e4ningslogg", page_icon="\ud83c\udfcb\ufe0f", layout="centered")

# Centrera innehåll för bättre mobilvy
with st.container():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("Tr\u00e4ningslogg \ud83c\udfcb\ufe0f")

user = st.text_input("Anv\u00e4ndarnamn")

if user:
    menu = st.radio("V\u00e4lj funktion", ["Logga pass", "Visa senaste pass"], horizontal=True)

    if menu == "Logga pass":
        st.header("Logga nytt pass")
        with st.form("logg_form"):
            ovning = st.text_input("\u00d6vning")
            mg = st.text_input("Muskelgrupp")
            col1, col2, col3 = st.columns(3)
            with col1:
                vikt = st.number_input("Vikt (kg)", min_value=0.0, step=1.0)
            with col2:
                reps = st.number_input("Reps", min_value=1, step=1)
            with col3:
                sets = st.number_input("Set", min_value=1, step=1)
            kommentar = st.text_input("Kommentar")
            submitted = st.form_submit_button("Spara pass")
            if submitted:
                logga_pass(user, ovning, mg, vikt, reps, sets, kommentar)
                st.success(f"Passet f\u00f6r {ovning} sparades!")

    elif menu == "Visa senaste pass":
        st.header("Senaste 10 pass")
        df = senaste_pass(user)
        if df.empty:
            st.info("Ingen data hittades.")
        else:
            st.dataframe(df, use_container_width=True)
else:
    st.info("Ange anv\u00e4ndarnamn f\u00f6r att b\u00f6rja.")
