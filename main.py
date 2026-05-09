import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

# --- CONTROLE DE ACESSO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("☕ Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "1234":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- FUNÇÃO DE FORMATAÇÃO DE MOEDA ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def clean_currency(val):
    if isinstance(val, str):
        clean = val.replace('R$', '').replace('\xa0', '').replace('.', '').replace(',', '.').strip()
        try: return float(clean)
        except: return 0.0
    return val

# --- CARREGAMENTO DOS DADOS ---
file_name = "Faturamento.csv" if os.path.exists("Faturamento.csv") else "faturamento.csv"

if os.path.exists(file_name):
    df = pd.read_csv(file_name, sep=';').copy()
    hourly_cols = [c for c in df.columns if ":" in c]
    
    for col in hourly_cols + ['Faturamento do dia']:
        df[col] = df[col].apply(clean_currency)
    
    st.title("☕ Consulta Acumulada")
    st.write("Madureira Shopping")

    # --- INTERFACE ---
    st.divider()
    hora_alvo = st.selectbox("Selecione a Hora:", hourly_cols, index=hourly_cols.index("18:00") if "18:00" in hourly_cols else 0)
    
    col1, col2 = st.columns(2)
    with col1:
        v_min = st.number_input("Valor Inicial (R$):", value=1000.0)
    with col2:
        v_max = st.number_input("Valor Final (R$):", value=1200.0)

    # --- LÓGICA ---
    idx_hora = hourly_cols.index(hora_alvo)
    colunas_ate_agora = hourly_cols[:idx_hora + 1]
    df['Soma_Acumulada'] = df[colunas_ate_agora].sum(axis=1)
    df_filtrado = df[(df['Soma_Acumulada'] >= v_min) & (df['Soma_Acumulada'] <= v_max)]

    # --- SAÍDA FORMATADA ---
    st.divider()
    if not df_filtrado.empty:
        st.subheader(f"📊 Encontrados {len(df_filtrado)} dias:")
        
        for _, linha in df_filtrado.iterrows():
            acumulado_fmt = formatar_moeda(linha['Soma_Acumulada'])
            total_dia_fmt = formatar_moeda(linha['Faturamento do dia'])
            
            # Usando markdown para criar um visual de "card"
            st.markdown(f"""
            📅 **Dia {linha['Data']}**
            * Até as {hora_alvo}: **{acumulado_fmt}**
            * Final do dia: **{total_dia_fmt}**
            """)
            st.divider() # Linha fina para separar os dias
    else:
        st.info("Nenhum dia encontrado neste intervalo.")
else:
    st.error("Arquivo 'Faturamento.csv' não encontrado.")
