def inserir_anamnese_paciente(dict_anamnese):
    import streamlit as st 
    import pandas as pd
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="AnamnesePacientes")

    dict_anamnese['id_paciente'] = df['id_paciente'].max() + 1

    df2 = pd.DataFrame([dict_anamnese])

    df = pd.concat([df, df2], ignore_index=True)

    conn.update(worksheet="AnamnesePacientes", data=df)
    st.success(f"{dict_anamnese['nome_paciente']} - {dict_anamnese['id_paciente']} inserido com sucesso!")
    st.toast(f"✅🧾{dict_anamnese['nome_paciente']} inserido com sucesso! \n ​{dict_anamnese['id_paciente']}")
    st.cache_data.clear()

def copiar_link_streamlit(link, label = "📋 Copiar link"):
    import streamlit as st 
    import streamlit.components.v1 as components

    html = f"""
    <style>
        .botao-copiar {{
            font-family: sans-serif;
            background-color: rgb(255, 255, 255);
            border: 1px solid rgba(49, 51, 63, 0.2);
            color: rgb(49, 51, 63);
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1rem;
            height: 2.5rem;

        }}
        .botao-copiar:hover {{
            border-color: rgba(255, 0, 0, 0.3);
            color: red;
        }}
    </style>
    <button class="botao-copiar" onclick="copiarParaClipboard(this)">
        {label}
    </button>
    <script>
        function copiarParaClipboard(btn) {{
            navigator.clipboard.writeText("{link}").then(function() {{
                const textoOriginal = btn.innerHTML;
                btn.innerHTML = "✅ Copiado!";
                setTimeout(() => {{
                    btn.innerHTML = textoOriginal;
                }}, 2000);
            }});
        }}
    </script>
    """

    components.html(html, height=50)