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

# --- FUNÇÃO DE LIMPEZA FINANCEIRA ---
def clean_currency(val):
    if isinstance(val, str):
        clean = val.replace('R$', '').replace('\xa0', '').replace('.', '').replace(',', '.').strip()
        try: return float(clean)
        except: return 0.0
    return val

# --- CARREGAMENTO DOS DADOS ---
file_name = "Faturamento.csv" if os.path.exists("Faturamento.csv") else "faturamento.csv"

if os.path.exists(file_name):
    # Lendo o arquivo com o separador correto
    df = pd.read_csv(file_name, sep=';').copy()
    hourly_cols = [c for c in df.columns if ":" in c]
    
    # Limpando todas as colunas financeiras
    for col in hourly_cols + ['Faturamento do dia']:
        df[col] = df[col].apply(clean_currency)
    
    st.title("☕ Consulta de Metas Acumuladas")
    st.write("Unidade: Madureira Shopping")

    # --- INTERFACE DE ENTRADA ---
    st.divider()
    hora_alvo = st.selectbox("Selecione a Hora:", hourly_cols, index=hourly_cols.index("18:00") if "18:00" in hourly_cols else 0)
    
    col1, col2 = st.columns(2)
    with col1:
        v_min = st.number_input("Valor Inicial (R$):", value=1000.0)
    with col2:
        v_max = st.number_input("Valor Final (R$):", value=1200.0)

    # --- LÓGICA DE CÁLCULO ACUMULADO ---
    idx_hora = hourly_cols.index(hora_alvo)
    colunas_ate_agora = hourly_cols[:idx_hora + 1]
    
    # Criamos uma coluna temporária com a soma das vendas até aquela hora
    df['Soma_Acumulada'] = df[colunas_ate_agora].sum(axis=1)
    
    # Filtragem conforme os valores de entrada
    df_filtrado = df[(df['Soma_Acumulada'] >= v_min) & (df['Soma_Acumulada'] <= v_max)]

    # --- SAÍDA DOS RESULTADOS ---
    st.divider()
    if not df_filtrado.empty:
        st.subheader("Resultados encontrados:")
        for _, linha in df_filtrado.iterrows():
            # Formatação seguindo o seu exemplo exato
            dia = linha['Data']
            acumulado = f"{linha['Soma_Acumulada']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            total_dia = f"{linha['Faturamento do dia']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            
            st.write(f"📅 **Dia {dia}**: Você atingiu **R$ {acumulado}** reais até as {hora_alvo} e faturou **R$ {total_dia}** reais no final do dia.")
    else:
        st.info("Nenhum dia encontrado com faturamento acumulado neste intervalo.")

else:
    st.error("Arquivo 'Faturamento.csv' não encontrado. Por favor, suba o arquivo para o GitHub.")
