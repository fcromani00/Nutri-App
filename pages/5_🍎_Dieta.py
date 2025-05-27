import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA E CARREGAMENTO DOS DADOS ---

st.set_page_config(layout="wide", page_title="Prescrição de Dieta")

# Dicionário para mapear refeições a emojis. Você pode customizar como quiser!
MAPA_EMOJIS_REFEICOES = {
    "Café da Manhã": "🌅",
    "Lanche da Manhã": "🍎",
    "Almoço": "☀️",
    "Lanche da Tarde": "🥪",
    "Jantar": "🌃",
    "Ceia": "🦉"
}

st.title("📝 Módulo de Prescrição de Dieta")
st.markdown("Adicione alimentos a cada refeição para montar o plano alimentar do paciente.")

# Função para carregar e cachear os dados da Tabela TACO
@st.cache_data(ttl=3600)
def load_data():
    # Conexão com o Google Sheets conforme você especificou
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="TACO")
    
    # Limpeza e preparação dos dados
    # Seleciona e renomeia as colunas mais importantes para facilitar o uso
    colunas_essenciais = {
        'descricao_alimento': 'Alimento',
        'porcao_g': 'Porção Padrão (g)', # Embora não usada diretamente no resumo, pode ser útil manter
        'umidade_pct': 'Umidade (%)', # Idem
        'kcal': 'Energia (kcal)',
        'proteina_g': 'Proteínas (g)',
        'lipideos_g': 'Lipídeos (g)',
        'carboidrato_g': 'Carboidratos (g)',
        'fibra_alimentar_g': 'Fibra Alimentar (g)'
    }
    # Garante que apenas colunas existentes sejam selecionadas
    colunas_presentes = [col for col in colunas_essenciais.keys() if col in df.columns]
    df_selecionado = df[colunas_presentes].copy()
    
    # Renomeia apenas as colunas que foram selecionadas
    colunas_essenciais_presentes = {k: v for k, v in colunas_essenciais.items() if k in colunas_presentes}
    df_selecionado.rename(columns=colunas_essenciais_presentes, inplace=True)

    # Define as colunas que DEVEM ser numéricas para o app funcionar
    colunas_numericas_obrigatorias = ['Energia (kcal)', 'Proteínas (g)', 'Lipídeos (g)', 'Carboidratos (g)']

    # Converte colunas numéricas, tratando erros e valores nulos
    for col in colunas_numericas_obrigatorias:
        if col in df_selecionado.columns:
            df_selecionado[col] = pd.to_numeric(df_selecionado[col], errors='coerce').fillna(0)
        else:
            # Se uma coluna obrigatória não existir após renomear, cria com zeros
            # Isso previne erros se a planilha original não tiver exatamente essas colunas
            st.warning(f"Coluna '{col}' (originalmente '{[k for k, v in colunas_essenciais.items() if v == col][0]}') não encontrada na planilha. Valores serão considerados 0.")
            df_selecionado[col] = 0 
            
    # Garante que a coluna 'Alimento' exista
    if 'Alimento' not in df_selecionado.columns:
        st.error("Coluna 'Alimento' (originalmente 'descricao_alimento') é essencial e não foi encontrada. Verifique sua planilha TACO.")
        return pd.DataFrame(columns=['Alimento'] + colunas_numericas_obrigatorias)


    return df_selecionado

df_taco = load_data()

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---

if 'dieta_paciente' not in st.session_state:
    st.session_state.dieta_paciente = {
        "Café da Manhã": [],
        "Lanche da Manhã": [],
        "Almoço": [],
        "Lanche da Tarde": [],
        "Jantar": [],
        "Ceia": []
    }
# Para controlar o selectbox de alimentos e permitir reset se necessário
if 'alimento_selecionado_key' not in st.session_state:
    st.session_state.alimento_selecionado_key = None


# --- LAYOUT DA INTERFACE (SIDEBAR E ÁREA PRINCIPAL) ---

with st.sidebar:
    st.header("Resumo Total do Dia")
    
    total_kcal = 0
    total_carb = 0
    total_prot = 0
    total_lipi = 0

    for refeicao_lista in st.session_state.dieta_paciente.values(): # Renomeado para evitar conflito
        if refeicao_lista:
            df_refeicao = pd.DataFrame(refeicao_lista)
            if not df_refeicao.empty:
                total_kcal += df_refeicao['Energia (kcal)'].sum()
                total_carb += df_refeicao['Carboidratos (g)'].sum()
                total_prot += df_refeicao['Proteínas (g)'].sum()
                total_lipi += df_refeicao['Lipídeos (g)'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Calorias", f"{total_kcal:.0f} kcal")
    col2.metric("Proteínas", f"{total_prot:.1f} g")
    col1.metric("Carboidratos", f"{total_carb:.1f} g")
    col2.metric("Lipídeos", f"{total_lipi:.1f} g")

    if st.button("🧹 Limpar Dieta Atual"):
        st.session_state.dieta_paciente = {
            "Café da Manhã": [], "Lanche da Manhã": [], "Almoço": [],
            "Lanche da Tarde": [], "Jantar": [], "Ceia": []
        }
        st.session_state.alimento_selecionado_key = None # Reseta também o alimento selecionado
        st.rerun()


# --- ÁREA DE INPUT PARA ADICIONAR ALIMENTOS ---
st.header("Adicionar Alimento")

col_refeicao, col_alimento_selecao, col_qtd = st.columns([1, 2, 1])

with col_refeicao:
    refeicao_selecionada_nome = st.selectbox( # Renomeado para evitar conflito
        "Selecione a Refeição",
        options=list(st.session_state.dieta_paciente.keys()),
        key="select_refeicao_key" 
    )

with col_alimento_selecao:
    # Usar a chave do session_state para controlar o selectbox
    # Isso permite resetar o selectbox programaticamente se necessário
    alimento_selecionado_nome = st.selectbox(
        "Busque um Alimento na Tabela TACO",
        options=df_taco['Alimento'].unique() if 'Alimento' in df_taco else [],
        placeholder="Digite para buscar...",
        index=None, # Começa com o placeholder
        key="alimento_selecionado_key" # Chave para controle
    )

    # NOVA SEÇÃO: Exibir resumo do alimento selecionado
    if st.session_state.alimento_selecionado_key: # Verifica se um alimento foi selecionado (usa a chave)
        # Pega as informações do alimento do df_taco
        # Garante que a coluna 'Alimento' existe antes de filtrar
        if 'Alimento' in df_taco.columns:
            info_alimento_resumo_df = df_taco[df_taco['Alimento'] == st.session_state.alimento_selecionado_key]
            if not info_alimento_resumo_df.empty:
                info_alimento_resumo = info_alimento_resumo_df.iloc[0]
            
                # Usar st.expander para o resumo, para não ocupar muito espaço por padrão
                with st.expander(f"Informações para 100g de: {st.session_state.alimento_selecionado_key}", expanded=True):
                    resumo_c1, resumo_c2 = st.columns(2)
                    with resumo_c1:
                        st.metric(label="Energia", value=f"{info_alimento_resumo.get('Energia (kcal)', 0):.0f} kcal")
                        st.metric(label="Carboidratos", value=f"{info_alimento_resumo.get('Carboidratos (g)', 0):.1f} g")
                    with resumo_c2:
                        st.metric(label="Proteínas", value=f"{info_alimento_resumo.get('Proteínas (g)', 0):.1f} g")
                        st.metric(label="Lipídeos", value=f"{info_alimento_resumo.get('Lipídeos (g)', 0):.1f} g")
            else:
                st.caption(f"Informações não encontradas para {st.session_state.alimento_selecionado_key} no DataFrame processado.")
        else:
            st.caption("Coluna 'Alimento' não disponível para buscar informações.")


with col_qtd:
    quantidade_g = st.number_input("Quantidade (g) para o plano", min_value=1, value=100, key="input_qtd_key")

# Botão de adicionar Alimento, posicionado abaixo das colunas de input para melhor fluxo
if st.button("✅ Adicionar Alimento ao Plano", key="btn_adicionar_alimento_key"):
    if st.session_state.alimento_selecionado_key and quantidade_g > 0:
        if 'Alimento' in df_taco.columns:
            info_alimento_para_adicionar_df = df_taco[df_taco['Alimento'] == st.session_state.alimento_selecionado_key]
            if not info_alimento_para_adicionar_df.empty:
                info_alimento_para_adicionar = info_alimento_para_adicionar_df.iloc[0]
                fator = quantidade_g / 100 
                
                alimento_para_dieta = {
                    'Alimento': st.session_state.alimento_selecionado_key,
                    'Quantidade (g)': quantidade_g,
                    'Energia (kcal)': info_alimento_para_adicionar.get('Energia (kcal)', 0) * fator,
                    'Carboidratos (g)': info_alimento_para_adicionar.get('Carboidratos (g)', 0) * fator,
                    'Proteínas (g)': info_alimento_para_adicionar.get('Proteínas (g)', 0) * fator,
                    'Lipídeos (g)': info_alimento_para_adicionar.get('Lipídeos (g)', 0) * fator,
                }
                
                st.session_state.dieta_paciente[refeicao_selecionada_nome].append(alimento_para_dieta)
                st.success(f"{st.session_state.alimento_selecionado_key} ({quantidade_g}g) adicionado ao {refeicao_selecionada_nome}!")
                # Opcional: Resetar a seleção do alimento para facilitar a próxima adição
                st.session_state.alimento_selecionado_key = None 
                st.rerun() # Força o rerun para atualizar o selectbox e o resumo
            else:
                st.warning(f"Não foi possível encontrar os dados para '{st.session_state.alimento_selecionado_key}' para adicionar ao plano.")
        else:
            st.warning("Não é possível adicionar alimento pois a coluna 'Alimento' não existe nos dados carregados.")
            
    elif not st.session_state.alimento_selecionado_key:
        st.warning("Por favor, selecione um alimento.")
    else: 
        st.warning("Por favor, insira uma quantidade válida (maior que 0).")


st.divider()

# --- EXIBIÇÃO DA DIETA COMPLETA (VERSÃO INTERATIVA COM BOTÃO DE REMOÇÃO) ---
st.header("Plano Alimentar do Paciente")

for nome_refeicao, alimentos_lista in st.session_state.dieta_paciente.items(): # Renomeado para evitar conflito
    if alimentos_lista:  
        emoji_refeicao = MAPA_EMOJIS_REFEICOES.get(nome_refeicao, "🍽️")
        st.subheader(f"{emoji_refeicao} {nome_refeicao}")
        
        col_header_1, col_header_2, col_header_3, col_header_4, col_header_5, col_header_6 = st.columns([3, 1.2, 1, 1, 1, 1])
        headers = ['Alimento', 'Qtd (g)', 'Kcal', 'Carbs (g)', 'Prot (g)', 'Ação']
        
        col_map = [col_header_1, col_header_2, col_header_3, col_header_4, col_header_5, col_header_6]
        for col, header_text in zip(col_map, headers):
            col.markdown(f"**{header_text}**")

        for i, alimento_item in enumerate(alimentos_lista): # Renomeado para evitar conflito
            col_data_1, col_data_2, col_data_3, col_data_4, col_data_5, col_data_6 = st.columns([3, 1.2, 1, 1, 1, 1])
            
            col_data_1.write(alimento_item.get('Alimento', 'N/A'))
            col_data_2.write(f"{alimento_item.get('Quantidade (g)', 0):.0f}")
            col_data_3.write(f"{alimento_item.get('Energia (kcal)', 0):.1f}")
            col_data_4.write(f"{alimento_item.get('Carboidratos (g)', 0):.1f}")
            col_data_5.write(f"{alimento_item.get('Proteínas (g)', 0):.1f}")
            
            if col_data_6.button("🗑️ Remover", key=f"remove_{nome_refeicao}_{i}"):
                st.session_state.dieta_paciente[nome_refeicao].pop(i)
                st.rerun()

        df_refeicao_view = pd.DataFrame(alimentos_lista)
        if not df_refeicao_view.empty:
            total_refeicao_kcal = df_refeicao_view['Energia (kcal)'].sum()
            total_refeicao_prot = df_refeicao_view['Proteínas (g)'].sum()
            total_refeicao_carb = df_refeicao_view['Carboidratos (g)'].sum()
            total_refeicao_lipi = df_refeicao_view['Lipídeos (g)'].sum()

            st.info(f"**Total da Refeição:** "
                    f"**{total_refeicao_kcal:.0f} kcal** | "
                    f"**P:** {total_refeicao_prot:.1f}g | "
                    f"**C:** {total_refeicao_carb:.1f}g | "
                    f"**L:** {total_refeicao_lipi:.1f}g")
        st.markdown("---") # Adiciona uma linha divisória após cada refeição

