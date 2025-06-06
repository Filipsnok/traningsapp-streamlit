import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------- Grundfunktioner ----------
def get_pr_filename(user):
    return f"rekord_{user}.csv"

def get_filename(user):
    return f"logg_{user}.csv"

def logga_pr(user, ovning, vikt, reps):
    fil = get_pr_filename(user)
    ny_1rm = vikt * (1 + reps / 30)
    print(f"logga_pr: ny_1rm={ny_1rm}")
    if os.path.exists(fil):
        df = pd.read_csv(fil)
        df["1RM"] = df["Vikt"] * (1 + df["Reps"] / 30)
        tidigare_pr = df[df["Övning"].str.lower() == ovning.lower()]
        print(f"logga_pr: tidigare_pr={tidigare_pr}")
        if not tidigare_pr.empty:
            max_1rm = tidigare_pr["1RM"].max()
            print(f"logga_pr: max_1rm={max_1rm}")
            if ny_1rm <= max_1rm:
                return
    rad = {
        "Datum": datetime.today().strftime('%Y-%m-%d'),
        "Övning": ovning,
        "Vikt": vikt,
        "Reps": reps
    }
    df = pd.DataFrame([rad])
    print(f"logga_pr: sparar rad={rad}")
    if os.path.exists(fil):
        df.to_csv(fil, mode="a", index=False, header=False)
    else:
        df.to_csv(fil, mode="w", index=False, header=True)

def visa_pr(user):
    fil = get_pr_filename(user)
    if not os.path.exists(fil):
        return pd.DataFrame()
    return pd.read_csv(fil)

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
    print(f"logga_pass: sparar rad={rad}")
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
    print(f"hamta_ovningsdata: filtrerat df={df}")
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

with st.container():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        input[type=number] {
            width: 70px !important;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("Träningslogg 📋")

user = st.text_input("Användarnamn")

if user:
    menu = st.radio("Välj funktion", ["Logga pass", "Visa senaste pass", "Visa progression", "Visa rekord"], horizontal=True)

    if menu == "Logga pass":
        st.header("Logga nytt pass")
        with st.form("logg_form"):
            ovning = st.text_input("Övning")
            mg = st.text_input("Muskelgrupp")
            senaste_rad = hamta_senaste_rad(user, ovning) if ovning else None
            print(f"UI: senaste_rad={senaste_rad}")
            if senaste_rad is not None:
                st.info(f"Senaste för {ovning}: {senaste_rad['Vikt']} kg x {senaste_rad['Reps']} reps x {senaste_rad['Set']} set")

            st.markdown("**Set | Reps | Vikt | Klar | 🗑️**")

            if "set_data" not in st.session_state:
                st.session_state.set_data = [
                    {"reps": 5, "vikt": 40.0, "klar": False, "ta_bort": False} for _ in range(3)
                ]

            for i, row in enumerate(st.session_state.set_data):
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
                with col1:
                    st.markdown(f"**Set {i+1}**")
                with col2:
                    row["reps"] = st.number_input("Reps", value=row["reps"], min_value=1, step=1, key=f"reps_{i}", label_visibility="collapsed", placeholder="Reps")
                with col3:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        row["vikt"] = st.number_input("Vikt", value=row["vikt"], min_value=0.0, step=1.0, key=f"vikt_{i}", label_visibility="collapsed", placeholder="Vikt")
                    with c2:
                        st.markdown("kg")
                df_history = hamta_ovningsdata(user, ovning)
                if not df_history.empty:
                    row_1rm = row["vikt"] * (1 + row["reps"] / 30)
                    df_history["1RM"] = df_history["Vikt"] * (1 + df_history["Reps"] / 30)
                    max_1rm_all = df_history["1RM"].max()
                    max_1rm_year = df_history[df_history["Datum"].dt.year == datetime.now().year]["1RM"].max()
                    print(f"UI: row_1rm={row_1rm}, max_1rm_all={max_1rm_all}, max_1rm_year={max_1rm_year}")
                    label = []
                    if row_1rm >= max_1rm_all:
                        label.append("_**PR**_")
                    elif row_1rm >= max_1rm_year:
                        label.append("_**ÅB**_")
                    if label:
                        st.markdown(f"{' '.join(label)}")
                with col4:
                    row["klar"] = st.checkbox("", value=row["klar"], key=f"klar_{i}")
                with col5:
                    row["ta_bort"] = st.checkbox("🗑️", value=row.get("ta_bort", False), key=f"del_{i}")

            if st.form_submit_button("Spara pass"):
                st.session_state.set_data = [r for r in st.session_state.set_data if not r.get("ta_bort", False)]
                utforda_set = [row for row in st.session_state.set_data if row["klar"]]
                print(f"submit: utforda_set={utforda_set}")
                total_lyft = sum(row["vikt"] * row["reps"] for row in utforda_set)
                snittvikt = total_lyft / len(utforda_set) if utforda_set else 0

                kommentar = st.text_input("Kommentar")

                with st.expander("💪 Summering av passet"):
                    st.markdown(f"- Antal utförda set: **{len(utforda_set)}**")
                    st.markdown(f"- Total lyft vikt: **{total_lyft:.1f} kg**")
                    st.markdown(f"- Snittvikt per set: **{snittvikt:.1f} kg**")
                    st.markdown(f"- Kommentar: _{kommentar}_")

                st.success("Passet är nu klart och du kan spara när du vill.")
                if st.button("📂 Spara pass till fil"):
                    antal = 0
                    for row in utforda_set:
                        antal += 1
                        logga_pass(user, ovning, mg, row["vikt"], row["reps"], 1, kommentar)
                        logga_pr(user, ovning, row["vikt"], row["reps"])
                    if antal == 0:
                        st.warning("Inget set markerades som klart.")
                    else:
                        st.success(f"{antal} set för {ovning} sparades!")

        if st.button("➕ Lägg till set"):
            st.session_state.set_data.append({"reps": 5, "vikt": 40.0, "klar": False})

    elif menu == "Visa senaste pass":
        st.header("Senaste 10 pass")
        df = senaste_pass(user)
        if df.empty:
            st.info("Ingen data hittades.")
        else:
            st.dataframe(df, use_container_width=True)

    elif menu == "Visa rekord":
        st.header("Mina personliga rekord")
        df_pr = visa_pr(user)
        if df_pr.empty:
            st.info("Inga personliga rekord hittades.")
        else:
            st.dataframe(df_pr.sort_values("Datum", ascending=False), use_container_width=True)

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
