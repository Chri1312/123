import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Atletica Team App", page_icon="🏃‍♂️", layout="wide")

# ---- DATABASE REALE DA GOOGLE FOGLI ----
# Sostituisci il link qui sotto con quello del tuo foglio Google abilitato alla lettura pubblica
LINK_FOGLIO = "https://docs.google.com/spreadsheets/d/1fm1K3lc2kXAKc9h2QmIOZPU_4y61T6KBEAXPJvgpN_4/edit?usp=drive_link"
@st.cache_data
def carica_dati_esempio():
    allenatori = pd.DataFrame([
        {"ID_Allenatore": "ALL01", "Nome": "Marco", "Cognome": "Rossi", "Email": "coach@atletica.it", "Specialità": "Velocità"}
    ])
    atleti = pd.DataFrame([
        {"ID_Atleta": "ATL01", "ID_Allenatore": "ALL01", "Nome": "Luca", "Cognome": "Bianchi", "Email": "atleta@atletica.it", "Data_Nascita": "2005-04-12", "Tessera_FIDAL": "AA012345", "Link_Profilo_FIDAL": "https://fidal.it", "Scadenza_Visita_Medica": "2025-12-31"}
    ])
    gare = pd.DataFrame([
        {"ID_Gara": "GAR01", "Nome_Gara": "Campionati Regionali Assoluti", "Data_Gara": "2027-06-15", "Luogo": "Milano", "Tipo_Gara": "Pista Outdoor", "Link_Dispositivo_FIDAL": "https://fidal.it"}
    ])
    prestazioni = pd.DataFrame([
        {"ID_Prestazione": "P01", "ID_Atleta": "ATL01", "ID_Gara": "GAR01", "Gara_Specialità": "100m", "Stato_Convocazione": "Convocato", "Risultato_Ottenuto": "-", "Note_Gara": "-"}
    ])
    return allenatori, atleti, gare, prestazioni

df_allenatori, df_atleti, df_gare, df_prestazioni = carica_dati_esempio()

# ---- INTERFACCIA DI LOGIN ----
st.title("🏃‍♂️ Sistema Gestione Atletica Leggera")
st.write("Benvenuto nell'app della tua squadra. Inserisci la tua email per accedere.")

email_input = st.text_input("Inserisci la tua Email:", placeholder="esempio@atletica.it").strip().lower()

if email_input:
    # Controlla se è un allenatore
    is_coach = df_allenatori[df_allenatori['Email'].str.lower() == email_input]
    # Controlla se è un atleta
    is_atleta = df_atleti[df_atleti['Email'].str.lower() == email_input]

    if not is_coach.empty:
        # ---- VISTA ALLENATORE ----
        coach = is_coach.iloc[0]
        st.success(f"Loggato come Allenatore: **{coach['Nome']} {coach['Cognome']}** ({coach['Specialità']})")
        
        tab1, tab2, tab3 = st.tabs(["I Miei Atleti", "Calendario Gare", "Inserimento Risultati"])
        
        with tab1:
            st.subheader("I tuoi Atleti in gestione")
            miei_atleti = df_atleti[df_atleti['ID_Allenatore'] == coach['ID_Allenatore']]
            for _, atleta in miei_atleti.iterrows():
                # Controllo Visita Medica
                scadenza = datetime.strptime(atleta['Scadenza_Visita_Medica'], "%Y-%m-%d").date()
                oggi = datetime.now().date()
                
                col1, col2, col3 = st.columns([2, 2, 2])
                col1.write(f"**{atleta['Nome']} {atleta['Cognome']}** (Tessera: {atleta['Tessera_FIDAL']})")
                col2.link_button("Vedi Profilo FIDAL ↗", atleta['Link_Profilo_FIDAL'])
                
                if scadenza < oggi:
                    col3.error(f"🔴 VISITA SCADUTA ({atleta['Scadenza_Visita_Medica']})")
                else:
                    col3.success(f"🟢 In Regola ({atleta['Scadenza_Visita_Medica']})")
                    
        with tab2:
            st.subheader("Aggiungi o vedi gare della stagione")
            st.dataframe(df_gare, use_container_width=True)
            
        with tab3:
            st.subheader("Gestione Convocazioni e Tempi/Misure")
            st.dataframe(df_prestazioni, use_container_width=True)

    elif not is_atleta.empty:
        # ---- VISTA ATLETA ----
        atleta = is_atleta.iloc[0]
        st.success(f"Loggato come Atleta: **{atleta['Nome']} {atleta['Cognome']}**")
        
        # Alert Visita Medica Urgente
        scadenza = datetime.strptime(atleta['Scadenza_Visita_Medica'], "%Y-%m-%d").date()
        oggi = datetime.now().date()
        if scadenza < oggi:
            st.error(f"🚨 ATTENZIONE: La tua visita medica agonistica è SCADUTA il {atleta['Scadenza_Visita_Medica']}. Rinnovala subito per gareggiare!")
        else:
            st.info(f"✅ Certificato medico valido fino al: {atleta['Scadenza_Visita_Medica']}")
            
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("I tuoi Dati FIDAL")
            st.write(f"**Numero Tessera:** {atleta['Tessera_FIDAL']}")
            st.link_button("Apri la tua Scheda FIDAL Ufficiale ↗", atleta['Link_Profilo_FIDAL'])
            
        with col2:
            st.subheader("Le tue Prossime Gare & Convocazioni")
            mie_gare = df_prestazioni[df_prestazioni['ID_Atleta'] == atleta['ID_Atleta']]
            
            for _, prestazione in mie_gare.iterrows():
                gara_info = df_gare[df_gare['ID_Gara'] == prestazione['ID_Gara']].iloc[0]
                st.write(f"🏆 **{gara_info['Nome_Gara']}** ({gara_info['Luogo']}) - Data: {gara_info['Data_Gara']}")
                st.write(f"Specialità assegnata: **{prestazione['Gara_Specialità']}**")
                
                # Bottone conferma presenza
                if prestazione['Stato_Convocazione'] == "Convocato":
                    if st.button("Conferma Presenza alla Gara", key=prestazione['ID_Prestazione']):
                        st.success("Presenza confermata all'allenatore!")

    else:
        st.warning("Email non trovata. Usa `coach@atletica.it` o `atleta@atletica.it` per provare il test.")
