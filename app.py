import streamlit as st

# --- PAGE SETUP ---
cadastro_paciente = st.Page(
    "pages/1_📋_Cadastro_Paciente.py",
    title="Cadastro Paciente",
    icon="📝",
    default=True,
)

consulta = st.Page(
    "pages/2_📅_Consultas.py",
    title="Consultas",
    icon="✍️",
)

relatorio_paciente = st.Page(
    "pages/3_📈_Relatorio.py",
    title="Relatório Paciente",
    icon="📈",
)

pagina_lead = st.Page(
    "pages/4_📢_Pre_Anamnese.py",
    title="Lead",
    icon="📢",
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation({
    "Menu": [cadastro_paciente, consulta, relatorio_paciente],
    "Pacientes": [pagina_lead]
})


# --- RUN NAVIGATION ---
pg.run()