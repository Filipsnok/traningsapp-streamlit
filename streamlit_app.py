import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# ---------- Grundfunktioner ----------
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

def hamta_ovningsdata(user, ovning):
    fil = get_filename(user)
    if not os.path.exists(fil):
        return pd.DataFrame()
    df = pd.read_csv(fil)
    df = df[df["Övning"].str.lower() == ovning.lower()]
    if df.empty:
        return df
    df["Datum"] = pd.to_datetime(df["Datum"])
    df = df.sort_values("Datum")
    df["Totalvikt"] = df["Vikt"] * df["Reps"] * df["Set"]
    return df

def hamta_senaste_vikt(user, ovning):
    df = hamta_ovningsdata(user, ovning)
    if df.empty:
        return 0.0
    return df["Vikt"].iloc[-1]

def hamta_senaste_rad(user, ovning):
    df = hamta_ovningsdata(user, ovning)
    if df.empty:
        return None
    return df.iloc[-1]

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Träningslogg", page_icon="📋", layout="centered")

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

st.title("Träningslogg 📋")

user = st.text_input("Användarnamn")

if user:
    menu = st.radio("Välj funktion", ["Logga pass", "Visa senaste pass", "Visa progression"], horizontal=True)

    if menu == "Logga pass":
        st.header("Logga nytt pass")
        with st.form("logg_form"):
            ovning = st.text_input("Övning")
            mg = st.text_input("Muskelgrupp")
            autofyll_vikt = 0.0
            senaste_rad = None
            if ovning:
                autofyll_vikt = hamta_senaste_vikt(user, ovning)
                senaste_rad = hamta_senaste_rad(user, ovning)

            if senaste_rad is not None:
                st.info(f"Senaste för {ovning}: {senaste_rad['Vikt']} kg x {senaste_rad['Reps']} reps x {senaste_rad['Set']} set")

            col1, col2, col3 = st.columns(3)
            with col1:
                vikt = st.number_input("Vikt (kg)", min_value=0.0, step=1.0, value=autofyll_vikt)
            with col2:
                reps = st.number_input("Reps", min_value=1, step=1)
            with col3:
                sets = st.number_input("Set", min_value=1, step=1)
            kommentar = st.text_input("Kommentar")
            checkboxes = [st.checkbox(f"Set {i+1} utfört") for i in range(int(sets))]
            submitted = st.form_submit_button("Spara pass")
            if submitted:
                utförda_set = sum(checkboxes)
                if utförda_set == 0:
                    st.warning("Du måste kryssa i minst ett set som utfört.")
                else:
                    logga_pass(user, ovning, mg, vikt, reps, utförda_set, kommentar)
                    st.success(f"{utförda_set} set för {ovning} sparades!")

    elif menu == "Visa senaste pass":
        st.header("Senaste 10 pass")
        df = senaste_pass(user)
        if df.empty:
            st.info("Ingen data hittades.")
        else:
            st.dataframe(df, use_container_width=True)

    elif menu == "Visa progression":
        st.header("Progression över tid")
        ovning_val = st.text_input("Skriv övning att visa graf för")
        if ovning_val:
            df_prog = hamta_ovningsdata(user, ovning_val)
            if df_prog.empty:
                st.warning("Ingen data hittades för den övningen.")
            else:
                st.line_chart(df_prog.set_index("Datum")["Totalvikt"])
else:
    st.info("Ange användarnamn för att börja.")
