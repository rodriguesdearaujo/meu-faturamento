import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

# --- SENHA ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("☕ Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "1563":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- FUNÇÕES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def obter_dia_semana(data_str):
    try:
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        return dias[data_obj.weekday()]
    except: return ""

def clean_currency(val):
    if isinstance(val, str):
        clean = val.replace('R$', '').replace('\xa0', '').replace('.', '').replace(',', '.').strip()
        try: return float(clean)
        except: return 0.0
    return val

# --- CARGA ---
file_name = "Faturamento.csv" if os.path.exists("Faturamento.csv") else "faturamento.csv"
if os.path.exists(file_name):
    df = pd.read_csv(file_name, sep=';').copy()
    hourly_cols = [c for c in df.columns if ":" in c]
    for col in hourly_cols + ['Faturamento do dia']:
        df[col] = df[col].apply(clean_currency)
    
    st.title("🔮 Previsão e Consulta")
    st.write("Madureira Shopping")

    st.divider()
    hora_alvo = st.selectbox("Horário Atual:", hourly_cols, index=hourly_cols.index("18:00"))
    
    col1, col2 = st.columns(2)
    with col1:
        v_min = st.number_input("Valor Inicial Acumulado:", value=1000.0)
    with col2:
        v_max = st.number_input("Valor Final Acumulado:", value=1200.0)

    # Lógica de Acumulado
    idx_hora = hourly_cols.index(hora_alvo)
    df['Soma_Acumulada'] = df[hourly_cols[:idx_hora + 1]].sum(axis=1)
    df_filtrado = df[(df['Soma_Acumulada'] >= v_min) & (df['Soma_Acumulada'] <= v_max)]

    # --- SEÇÃO DE PREVISÃO ---
    if not df_filtrado.empty:
        st.divider()
        st.subheader("🚀 Previsão de Fechamento")
        
        media_fechamento = df_filtrado['Faturamento do dia'].mean()
        min_fechamento = df_filtrado['Faturamento do dia'].min()
        max_fechamento = df_filtrado['Faturamento do dia'].max()

        # Criando colunas de destaque para os números principais
        m1, m2, m3 = st.columns(3)
        m1.metric("📉 Mínimo", formatar_moeda(min_fechamento))
        m2.metric("🎯 Média", formatar_moeda(media_fechamento))
        m3.metric("💰 Máximo", formatar_moeda(max_fechamento))

        st.info(f"Cálculo baseado em **{len(df_filtrado)} dias parecidos** no histórico.")

        # --- HISTÓRICO DETALHADO ---
        st.divider()
        st.subheader("📅 Gêmeos Históricos")
        
        # Preparando os dados para uma tabela limpa
        dados_tabela = []
        for _, linha in df_filtrado.iterrows():
            dados_tabela.append({
                "Data": linha['Data'],
                "Dia da Semana": obter_dia_semana(linha['Data']),
                f"Acumulado {hora_alvo}": formatar_moeda(linha['Soma_Acumulada']),
                "Total do Dia": formatar_moeda(linha['Faturamento do dia'])
            })
        
        # Exibindo como uma tabela interativa que cabe na tela do celular
        st.table(dados_tabela)
        
    else:
        st.warning("Nenhum cenário parecido encontrado para prever.")
