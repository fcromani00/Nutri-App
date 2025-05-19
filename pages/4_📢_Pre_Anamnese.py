import streamlit as st
import datetime
import pandas as pd
from core.anamnese import copiar_link_streamlit
from streamlit_gsheets import GSheetsConnection

with st.sidebar:
    st.subheader("Compartilhar")
    link = f"https://seu-app.streamlit.app/pagina?id={st.session_state.id_nutricionista}"
    copiar_link_streamlit(link)

try:
    id_nutricionista = st.query_params['id_nutricionista']
except:
    st.warning("""Nutricionista não identificado. Parâmetro id_nutricionista não fornecido.""")
    st.write("""Insira o id_nutricionista no link para validar""")
    st.write("""Ex: /Pre_Anamnese/?id_nutricionista=1""")
    st.write("Confirme com seu nuticionista o link correto")
    st.stop()

if 'nome_nutricionista' in st.query_params:
    nome_nutricionista = st.query_params['nome_nutricionista']
else:
    nome_nutricionista = ""

st.title(f"📝 Pré-Anamnese Nutricional {nome_nutricionista}")

with st.form("pre_anamnese_form"):
    nome = st.text_input("Nome completo")
    email = st.text_input("Email")
    telefone = st.text_input("Telefone (opcional)")
    objetivo = st.selectbox("Qual seu objetivo principal?", ["Emagrecimento", "Ganho de massa", "Saúde geral", "Outro"])
    info_extra = st.text_area("Deseja deixar alguma observação ou dúvida?")

    enviado = st.form_submit_button("Enviar")

if enviado:
    st.success("✅ Informações recebidas com sucesso!")
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="LeadsPacientes")

    novo_lead = {
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "objetivo": objetivo,
        "info_extra": info_extra,
        "id_nutricionista": id_nutricionista,
        "data_envio": datetime.datetime.now(),
    }

    df_novo = pd.DataFrame([novo_lead])
    df = pd.concat([df, df_novo], ignore_index=True)
    conn.update(worksheet="LeadsPacientes", data=df)

    st.toast("Pré-Anamnese enviada com sucesso! ✨")
