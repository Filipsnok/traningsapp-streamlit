import streamlit as st
import pandas as pd
from datetime import datetime
import os

def get_filename(user):
    return f"logg_{user}.csv"

def logga_pass(user, ovning, mg, vikt, reps, sets, kommentar):
    fil = get_filename(user)
    rad = {
        "Datum": datetime.today().strftime('%Y-%m-%d'),
        "Övning": ovning,
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

st.title("🏋️ Träningslogg")

user = st.text_input("Användarnamn")

if user:
    st.subheader("Logga nytt pass")
    ovning = st.text_input("Övning")
    mg = st.text_input("Muskelgrupp")
    vikt = st.number_input("Vikt (kg)", min_value=0.0)
    reps = st.number_input("Reps", min_value=1)
    sets = st.number_input("Set", min_value=1)
    kommentar = st.text_input("Kommentar")

    if st.button("Spara pass"):
        logga_pass(user, ovning, mg, vikt, reps, sets, kommentar)
        st.success("✅ Pass sparat!")

    st.subheader("Senaste pass")
    st.dataframe(senaste_pass(user))
else:
    st.info("Fyll i användarnamn för att börja.")
