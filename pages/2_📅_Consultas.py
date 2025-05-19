import streamlit as st
import pandas as pd
from datetime import datetime
from core.consultas import inserir_consulta, ler_pacientes_consultas
from login import check_password

if not check_password():
    st.stop()

st.sidebar.markdown(f"👤 Logado como: **{st.session_state.get('user', '')}**")

if st.sidebar.button("🔒 Logout"):
    st.session_state["password_correct"] = False

st.title("🩺 Registrar Consulta")

df_pacientes, df_consultas = ler_pacientes_consultas()

pacientes = df_pacientes[df_pacientes['id_nutricionista'] == st.session_state['id_nutricionista']]["nome_paciente"].dropna().unique()
paciente_escolhido = st.selectbox("Selecione o paciente:", pacientes)

if paciente_escolhido:

    st.subheader("📋 Dados da Consulta")

    queixas = st.text_area("Queixas principais")
    conduta = st.text_area("Conduta ou plano alimentar")
    orientacoes = st.text_area("Orientações gerais")

    incluir_retorno = st.checkbox("Deseja marcar uma data e horário de retorno?", value=True)
    if incluir_retorno:
        data_retorno = st.date_input("Data de retorno", format="DD/MM/YYYY")
        horario_retorno = st.time_input("Horário de retorno")
    else:
        data_retorno = None
        horario_retorno = None

    if st.button("💾 Salvar Consulta"):
        dict_consulta = {
            "id_consulta": df_consultas['id_consulta'].max() + 1 if not df_consultas.empty else 1,
            "nome_paciente": paciente_escolhido,
            "data_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "queixas": queixas,
            "conduta": conduta,
            "orientacoes": orientacoes,
            "data_retorno": data_retorno.strftime("%Y-%m-%d") if data_retorno else "",
            "horario_retorno": horario_retorno.strftime("%H:%M") if horario_retorno else ""
        }

        inserir_consulta(dict_consulta, paciente_escolhido)
        st.success(f"Consulta de {paciente_escolhido} registrada com sucesso!")