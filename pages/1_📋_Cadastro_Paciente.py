import streamlit as st
from core.anamnese import inserir_anamnese_paciente
import datetime
from login import check_password

if not check_password():
    st.stop()

st.sidebar.markdown(f"👤 Logado como: **{st.session_state.get('user', '')}**")

if st.sidebar.button("🔒 Logout"):
    st.session_state["password_correct"] = False
st.title("📋 Formulário de Anamnese Nutricional")

with st.form("anamnese_form"):
    st.subheader("Dados Pessoais")
    nome = st.text_input("Nome completo")
    data_nascimento = st.date_input("Data de Nascimento", min_value=datetime.date(1925, 1, 1), max_value=datetime.date.today())
    sexo = st.selectbox("Sexo", ["Feminino", "Masculino", "Outro"])
    peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
    altura = st.number_input("Altura (cm)", min_value=0.0, step=0.1)

    st.subheader("Histórico e Hábitos")
    objetivo = st.selectbox("Objetivo principal", ["Emagrecimento", "Ganho de massa", "Melhora da saúde", "Outro"])
    alergias = st.text_area("Possui alergias ou intolerâncias alimentares?")
    medicamentos = st.text_area("Usa algum medicamento regularmente?")
    atividade_fisica = st.selectbox("Pratica atividade física?", ["Sim", "Não"])
    frequencia = ""
    if atividade_fisica == "Sim":
        frequencia = st.text_input("Com que frequência?")

    st.subheader("Hábitos alimentares")
    refeicoes = st.multiselect(
        "Quais refeições costuma fazer ao longo do dia?",
        ["Café da manhã", "Lanche da manhã", "Almoço", "Lanche da tarde", "Jantar", "Ceia"]
    )
    agua = st.number_input("Quantos copos de água bebe por dia?", min_value=0)

    # Botão de envio
    enviado = st.form_submit_button("Enviar")

if enviado:
    st.success("✅ Dados enviados com sucesso!")
    st.write("### 🧾 Resumo da Anamnese")
    dict_paciente = {
        "nome_paciente": nome,
        "data_nascimento_paciente": data_nascimento,
        "sexo_paciente": sexo,
        "peso_paciente": peso,
        "altura_paciente": altura,
        "objetivo_paciente": objetivo,
        "alergias_paciente": alergias,
        "medicamentos_paciente": medicamentos,
        "atividade_fisica_paciente": atividade_fisica,
        "frequencia_atividade_fisica_paciente": frequencia,
        "qtd_refeicoes_paciente": refeicoes,
        "consumo_agua_pacientes": agua,
        "data_envio" : datetime.datetime.now()
    }
    st.write(dict_paciente)
    inserir_anamnese_paciente(dict_paciente)