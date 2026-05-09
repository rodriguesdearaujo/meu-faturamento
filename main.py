
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONTROLE DE ACESSO ---
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Digite a senha de acesso", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password"] == "1563": # <--- MUDE SUA SENHA AQUI
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.error("Senha incorreta")

if check_password():
    # --- TODO O RESTO DO SEU CÓDIGO COMEÇA AQUI ---
    st.title("☕ Sistema Interno - Cheirin Bão")
    st.write("Bem-vindo, chefe! Seus dados estão seguros.")
    
    # (Insira aqui o restante do código que te passei anteriormente)import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações para mobile
st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

st.title("☕ Consulta de Faturamento")

# Função para converter os dados brutos (R$ 1.234,56 -> 1234.56)
def clean_val(val):
    if isinstance(val, str):
        return float(val.replace('R$', '').replace('.', '').replace(',', '.').strip())
    return val

# Aqui você pode carregar seu arquivo ou colar os dados
# Futuramente, podemos conectar direto com seu Google Sheets
@st.cache_data
def load_data():
    # Simulando a carga dos dados que você enviou
    df = pd.read_csv("Faturamento.csv") 
    for col in df.columns:
        if col != 'Data':
            df[col] = df[col].apply(clean_val)
    return df

try:
    df = load_data()

    # Interface de Busca
    st.subheader("Filtros de Busca")
    col1, col2 = st.columns(2)
    with col1:
        hora = st.selectbox("Horário", df.columns[2:])
    with col2:
        v_min = st.number_input("Valor Mín (R$)", value=100.0)
        v_max = st.number_input("Valor Máx (R$)", value=500.0)

    # Filtragem
    res = df[(df[hora] >= v_min) & (df[hora] <= v_max)]

    if not res.empty:
        st.success(f"Encontrados {len(res)} dias similares")
        
        # Gráfico interativo que funciona no touch
        fig = px.bar(res, x='Data', y=[hora, 'Faturamento do dia'],
                     barmode='group', title="Comparativo Histórico",
                     labels={'value': 'Reais (R$)', 'variable': 'Legenda'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela para conferência rápida
        st.dataframe(res[['Data', hora, 'Faturamento do dia']])
    else:
        st.info("Nenhum registro no intervalo selecionado.")

except Exception as e:
    st.error("Aguardando upload da base de dados...")
