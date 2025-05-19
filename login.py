# https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso
# https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso
def check_password():
    """Returns `True` if the user had a correct password."""
    import streamlit as st
    from streamlit_gsheets import GSheetsConnection

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Nutricionistas")

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Email", key="email")
            st.text_input("Senha", type="password", key="password")
            st.form_submit_button("Login", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        user_row = df[
            (df['email_nutricionista'] == st.session_state["email"]) &
            (df['senha_nutricionista'] == st.session_state["password"])
        ]

        if not user_row.empty:
            st.session_state["password_correct"] = True
            st.session_state["user"] = user_row['nome_nutricionista'].iloc[0]
            st.session_state['id_nutricionista'] = user_row['id_nutricionista'].iloc[0]
            del st.session_state["password"]
            del st.session_state["email"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("Usuário ou senha incorretos")
    return False
