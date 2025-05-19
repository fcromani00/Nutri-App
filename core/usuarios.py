def ler_nutricionistas():
    import pandas as pd
    import streamlit as st 
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Nutricionistas")
    df['id_nutricionistas'] = df['id_nutricionista'].astype(int)
    return df