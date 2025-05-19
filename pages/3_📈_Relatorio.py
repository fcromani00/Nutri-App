import streamlit as st
from login import check_password

if not check_password():
    st.stop()

st.sidebar.markdown(f"👤 Logado como: **{st.session_state.get('user', '')}**")

if st.sidebar.button("🔒 Logout"):
    st.session_state["password_correct"] = False

# st.sidebar.button("Copiar Link para novo Cliente")


# def criar_botao_copiar(texto, botao_texto="Copiar para área de transferência", key=None):
#     """
#     Cria um botão que copia um texto para a área de transferência quando clicado.
    
#     Args:
#         texto: O texto a ser copiado
#         botao_texto: O texto a ser exibido no botão
#         key: Uma chave única para o componente HTML (importante se usar múltiplos botões)
#     """
#     if key is None:
#         key = f"copiar_{hash(texto)}"
    
#     # Criar o componente HTML com JavaScript para copiar para a área de transferência
#     html_code = f"""
#     <div style="display: flex; align-items: center;">
#         <p id="texto_{key}" style="margin-right: 10px; overflow: hidden; text-overflow: ellipsis;">{texto}</p>
#         <button id="botao_{key}" 
#                 style="background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
#             {botao_texto}
#         </button>
#         <span id="mensagem_{key}" style="margin-left: 10px; color: green; display: none;">Copiado!</span>
#     </div>

#     <script>
#         // Aguardar até que o documento esteja totalmente carregado
#         document.addEventListener('DOMContentLoaded', function() {{
#             const botao = document.getElementById('botao_{key}');
#             const texto = '{texto}';
#             const mensagem = document.getElementById('mensagem_{key}');
            
#             botao.addEventListener('click', function() {{
#                 // Criar um elemento de texto temporário
#                 const tempInput = document.createElement('textarea');
#                 tempInput.value = texto;
                
#                 // Adicionar à página, selecionar e copiar
#                 document.body.appendChild(tempInput);
#                 tempInput.select();
#                 document.execCommand('copy');
                
#                 // Remover o elemento temporário
#                 document.body.removeChild(tempInput);
                
#                 // Mostrar mensagem de confirmação
#                 mensagem.style.display = 'inline';
#                 setTimeout(function() {{
#                     mensagem.style.display = 'none';
#                 }}, 2000);
#             }});
#         }});
#     </script>
#     """
    
#     # Renderizar o componente HTML
#     st.components.v1.html(html_code, height=50)

# # Exemplo de uso
# st.title("Exemplo de Botão para Copiar Link")

# # Link que queremos copiar
# link = "https://exemplo.com/minha-pagina-especial"

# # Exibir informações
# st.write("Clique no botão abaixo para copiar o link:")

# # Criar o botão para copiar
# criar_botao_copiar(link, "📋 Copiar Link")

# # Adicionar um exemplo mais completo
# st.subheader("Exemplo com vários links")

# links = {
#     "Link para pré-anamnese": "https://nutri-app.streamlit.app/Pre_Anamnese?id_nutricionista=123",
#     "Link para agendamento": "https://nutri-app.streamlit.app/Agendar?id_nutricionista=123",
#     "Link para WhatsApp": "https://wa.me/5511999999999"
# }

# for titulo, url in links.items():
#     st.write(f"**{titulo}:**")
#     criar_botao_copiar(url, "📋 Copiar", key=hash(url))
#     st.write("---")

# st.write(st.session_state)