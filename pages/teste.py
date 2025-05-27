import streamlit as st
import pandas as pd
import requests # Para fazer chamadas HTTP para a API do LLM
import json
import time # Para adicionar pequenos atrasos, se necessário

# Tenta importar GSheetsConnection; se não estiver disponível, pode ser necessário instalar ou configurar.
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    st.error("A biblioteca streamlit-gsheets não foi encontrada. Por favor, instale-a com 'pip install streamlit-gsheets' e configure suas credenciais do Google Sheets.")
    st.stop()

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Gerador de Emojis para Alimentos")
st.title("🥑 Gerador de Emojis para Alimentos da Tabela TACO 🥕")
st.markdown("Esta página utiliza um LLM para sugerir emojis para os alimentos da Tabela TACO.")

# Define um número fixo de alimentos para processar para simplificar
ITEMS_TO_PROCESS = 597

# --- Carregamento de Dados da Tabela TACO ---
@st.cache_data(ttl=3600) # Cache por 1 hora
def load_taco_food_names():
    """
    Carrega os nomes dos alimentos da planilha 'TACO' no Google Sheets.
    Retorna um DataFrame com uma coluna 'Alimento' contendo nomes únicos.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="TACO")
        
        if 'descricao_alimento' not in df.columns:
            st.error("A coluna 'descricao_alimento' não foi encontrada na sua Tabela TACO.")
            return pd.DataFrame({'Alimento': []})
            
        food_names_df = df[['descricao_alimento']].copy()
        food_names_df.rename(columns={'descricao_alimento': 'Alimento'}, inplace=True)
        food_names_df.dropna(subset=['Alimento'], inplace=True)
        food_names_df['Alimento'] = food_names_df['Alimento'].astype(str).str.strip()
        unique_food_names_df = food_names_df.drop_duplicates(subset=['Alimento']).reset_index(drop=True)
        
        if unique_food_names_df.empty:
            st.warning("Nenhum nome de alimento encontrado ou a coluna 'descricao_alimento' está vazia após a limpeza.")
        return unique_food_names_df
    except Exception as e:
        st.error(f"Erro ao carregar dados da Tabela TACO: {e}")
        return pd.DataFrame({'Alimento': []})

# --- Configuração do LLM (Gemini) ---
# A chave da API do Gemini. 
# ATENÇÃO: É mais seguro usar st.secrets ou variáveis de ambiente para chaves de API.
# No entanto, seguindo a solicitação do usuário, a chave está sendo definida diretamente.
GEMINI_API_KEY = "AIzaSyDdzfeIF5x4C3ZvRyuL71Ht5MRIKOfWTtQ" 

# Template do prompt para o LLM
EMOJI_PROMPT_TEMPLATE = """
Para o alimento '{food_name}', sugira de 1 a 3 emojis que o representem da melhor maneira.
Retorne APENAS os emojis, separados por um espaço, sem nenhuma outra palavra, explicação, numeração ou qualquer outro texto.
Por exemplo, se o alimento for 'Maçã', uma boa resposta seria: 🍎
Se o alimento for 'Pão de Queijo', uma boa resposta seria: 🧀🍞
Se o alimento for 'Suco de Laranja', uma boa resposta seria: 🍊🥤
Alimento: '{food_name}'
Emojis:
"""

@st.cache_data(ttl=86400) # Cache das respostas do LLM por 24 horas
def generate_emojis_for_food(food_name: str) -> str:
    """
    Gera emojis para um nome de alimento usando a API Gemini.
    """
    if not food_name:
        return "Nome do alimento inválido"

    prompt_text = EMOJI_PROMPT_TEMPLATE.format(food_name=food_name)
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "role": "user", 
            "parts": [{"text": prompt_text}]
        }],
        "generationConfig": { 
            "temperature": 0.5, 
            "maxOutputTokens": 10 
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=45) # Timeout aumentado para 45s
        response.raise_for_status()  
        
        result = response.json()
        
        if (result.get("candidates") and 
            result["candidates"][0].get("content") and
            result["candidates"][0]["content"].get("parts") and
            result["candidates"][0]["content"]["parts"][0].get("text")):
            
            emojis = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            valid_emojis = "".join(char for char in emojis if ord(char) > 255 or char.isspace()) 
            return valid_emojis.strip() if valid_emojis else emojis 
        else:
            error_detail = result.get("error", {}).get("message", "Formato de resposta desconhecido.")
            if "API_KEY_INVALID" in error_detail or "API key not valid" in error_detail or "PERMISSION_DENIED" in error_detail:
                 st.error("Erro de API Key ou Permissão: A chave da API Gemini não é válida, está ausente, ou não tem permissão para este modelo. Verifique a configuração.")
                 return "Erro de API Key/Permissão" 
            st.warning(f"Resposta inesperada da API para '{food_name}': {result}")
            return f"Não foi possível gerar emojis (Resposta: {error_detail[:100]})"

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 403:
            st.error(f"Erro 403 Forbidden ao chamar a API Gemini para '{food_name}'. Isso geralmente indica um problema com a API Key ou permissões.")
            return "Erro 403: Acesso Negado"
        elif http_err.response.status_code == 429: # Too Many Requests
            st.warning(f"Limite de taxa da API atingido ao processar '{food_name}'. Tentando novamente em alguns segundos...")
            return "Limite de taxa" # Sinaliza para tentar novamente
        st.error(f"Erro HTTP ao tentar gerar emojis para '{food_name}': {http_err}")
        return "Erro HTTP"
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao tentar gerar emojis para '{food_name}': {e}")
        return "Erro de conexão"
    except Exception as e:
        st.error(f"Erro inesperado ao gerar emojis para '{food_name}': {e}")
        return "Erro inesperado"

# --- Interface Principal ---
df_foods_full = load_taco_food_names()

if not df_foods_full.empty:
    st.write(f"Tabela TACO carregada com {len(df_foods_full)} alimentos únicos.")
    
    df_sample_foods = df_foods_full.head(ITEMS_TO_PROCESS)
    st.write(f"Serão processados os primeiros {min(len(df_sample_foods), ITEMS_TO_PROCESS)} alimentos da lista.")


    if st.button(f"✨ Gerar Emojis para os Primeiros {min(len(df_sample_foods), ITEMS_TO_PROCESS)} Alimentos"):
        if df_sample_foods.empty:
            st.warning("Nenhum alimento para processar. Verifique o carregamento da Tabela TACO.")
        else:
            st.info(f"Gerando emojis para {min(len(df_sample_foods), ITEMS_TO_PROCESS)} alimentos... Isso pode levar vários minutos.")
            
            if 'emojis_results' not in st.session_state or \
               st.session_state.emojis_results.empty or \
               len(st.session_state.emojis_results) != min(len(df_sample_foods), ITEMS_TO_PROCESS) or \
               list(st.session_state.emojis_results['Alimento']) != list(df_sample_foods['Alimento'].head(min(len(df_sample_foods), ITEMS_TO_PROCESS))):
                
                current_sample_df = df_sample_foods.head(min(len(df_sample_foods), ITEMS_TO_PROCESS))
                st.session_state.emojis_results = current_sample_df[['Alimento']].copy()
                st.session_state.emojis_results['Emojis Sugeridos'] = ["⏳"] * len(current_sample_df)


            progress_bar = st.progress(0)
            total_items_to_process = len(st.session_state.emojis_results)
            
            max_retries = 3 # Número máximo de tentativas para erros de limite de taxa
            base_delay = 5  # Delay inicial em segundos para limite de taxa

            for index, row in st.session_state.emojis_results.iterrows():
                food_item_name = row['Alimento']
                
                # Só gera se ainda não tiver emoji válido ou se for placeholder
                if row['Emojis Sugeridos'] == "⏳" or "Erro" in str(row['Emojis Sugeridos']):
                    retries = 0
                    emojis = "Pendente" 
                    while retries < max_retries:
                        emojis = generate_emojis_for_food(food_item_name)
                        if emojis == "Limite de taxa":
                            retries += 1
                            current_delay = base_delay * (2 ** (retries -1)) # Exponential backoff
                            st.info(f"Limite de taxa. Tentando '{food_item_name}' novamente em {current_delay}s... (Tentativa {retries}/{max_retries})")
                            time.sleep(current_delay)
                        else:
                            break # Sai do loop de tentativas se não for erro de limite de taxa
                    
                    st.session_state.emojis_results.loc[index, 'Emojis Sugeridos'] = emojis
                
                # Atualiza a barra de progresso pelo índice real no dataframe que está sendo iterado
                progress_bar.progress((st.session_state.emojis_results.index.get_loc(index) + 1) / total_items_to_process)
                time.sleep(0.2) # Pequeno delay entre chamadas para não sobrecarregar a API
            
            st.success("Geração de emojis concluída!")
            st.rerun()


    if 'emojis_results' in st.session_state and not st.session_state.emojis_results.empty:
        st.subheader("Alimentos com Emojis Sugeridos")
        
        edited_df = st.data_editor(
            st.session_state.emojis_results,
            column_config={
                "Alimento": st.column_config.TextColumn("Alimento (Não Editável)", disabled=True, width="large"),
                "Emojis Sugeridos": st.column_config.TextColumn("Emojis Sugeridos ✨ (Editável)")
            },
            hide_index=True,
            num_rows="fixed" 
        )
        
        st.session_state.emojis_results = edited_df
        
        @st.cache_data 
        def convert_df_to_csv(df_to_convert):
            return df_to_convert.to_csv(index=False).encode('utf-8')

        csv_export = convert_df_to_csv(edited_df) 
        st.download_button(
            label="📥 Baixar tabela como CSV",
            data=csv_export,
            file_name=f"alimentos_com_emojis_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

else:
    st.warning("A Tabela TACO parece estar vazia ou não pôde ser carregada. Verifique sua planilha Google Sheets e as configurações de conexão.")

st.markdown("---")
st.caption("Nota: A qualidade dos emojis gerados depende da capacidade do LLM. Erros 403 ou 429 (limite de taxa) podem ocorrer devido à configuração da API Key ou limites de uso.")
