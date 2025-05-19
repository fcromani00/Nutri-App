def ler_pacientes_consultas():
    import streamlit as st 
    from streamlit_gsheets import GSheetsConnection
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_pacientes = conn.read(worksheet="AnamnesePacientes")
    df_consultas = conn.read(worksheet="Consultas")
    return df_pacientes, df_consultas


def inserir_consulta(dict_consulta, paciente_escolhido):
    import streamlit as st 
    import pandas as pd
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Consultas")

    dict_consulta['id_consulta'] = df['id_consulta'].max() + 1

    df2 = pd.DataFrame([dict_consulta])

    df = pd.concat([df, df2], ignore_index=True)

    conn.update(worksheet="Consultas", data=df)
    st.success(f"Consulta de {paciente_escolhido} registrada com sucesso!")
    st.toast("🩺 Consulta registrada!")
    st.cache_data.clear()