import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Atletica Team App", page_icon="🏃‍♂️", layout="wide")

# ---- DATABASE REALE DA GOOGLE FOGLI ----
# Sostituisci il link qui sotto con quello del tuo foglio Google abilitato alla lettura pubblica
LINK_FOGLIO = "INCOLLA_QUI_IL_TUO_LINK_DI_GOOGLE_FOGLI"

@st.cache_data(ttl=60) # Aggiorna i dati dal foglio automaticamente ogni 60 secondi
def carica_dati_fogli(url):
    # Estrae l'ID del foglio dal link per poter leggere le singole schede
    sheet_id = url.split("/d/")[1].split("/")[0]
    
    # Crea i link diretti per scaricare le 4 tabelle in formato CSV
    url_allenatori = f"https://google.com{sheet_id}/gviz/tq?tqx=out:csv&sheet=Allenatori"
    url_atleti = f"https://google.com{sheet_id}/gviz/tq?tqx=out:csv&sheet=Atleti"
    url_gare = f"https://google.com{sheet_id}/gviz/tq?tqx=out:csv&sheet=Calendario_Gare"
    url_prestazioni = f"https://google.com{sheet_id}/gviz/tq?tqx=out:csv&sheet=Prestazioni_e_Convocazioni"
    
    # Legge i dati inserendoli nelle tabelle dell'applicazione
    allenatori = pd.read_csv(url_allenatori)
    atleti = pd.read_csv(url_atleti)
    gare = pd.read_csv(url_gare)
    prestazioni = pd.read_csv(url_prestazioni)
    
    # Converte i formati data per evitare errori nei controlli della visita medica
    atleti['Scadenza_Visita_Medica'] = pd.to_datetime(atleti['Scadenza_Visita_Medica']).dt.strftime('%Y-%m-%d')
    gare['Data_Gara'] = pd.to_datetime(gare['Data_Gara']).dt.strftime('%Y-%m-%d')
    
    return allenatori, atleti, gare, prestazioni

# Caricamento effettivo dei dati dal web
try:
    df_allenatori, df_atleti, df_gare, df_prestazioni = carica_dati_fogli(LINK_FOGLIO)
except Exception as e:
    st.error("Errore nel collegamento a Google Fogli. Controlla di aver inserito il link corretto e di aver impostato la condivisione su 'Chiunque abbia il link'.")
    st.stop()

# ---- DA QUI IN POI IL CODICE DEL LOGIN E DEI PANNELLI RIMANE IDENTICO A PRIMA ----
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
