import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E ACESSO ---
st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "1234":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- MATRIZES DE PESO (DADOS FORNECIDOS) ---
PESOS_SEMANA = [0.677, 0.930, 0.878, 0.965, 1.016, 1.098, 1.435] # Dom a Sab
PESOS_MES = [
    0.94, 0.97, 0.99, 1.02, 1.05, 1.07, 1.10, 1.12, 1.11, 1.10,
    1.08, 1.07, 1.05, 1.04, 1.03, 1.02, 1.00, 0.99, 0.98, 0.97,
    0.96, 0.94, 0.93, 0.93, 0.92, 0.92, 0.91, 0.90, 0.90, 0.89, 0.89
]

# --- FUNÇÕES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

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

    st.title("🔮 Previsão Ponderada")
    
    # --- ENTRADAS ---
    hora_alvo = st.selectbox("Horário Atual:", hourly_cols, index=hourly_cols.index("18:00"))
    v_acumulado = st.number_input("Faturamento Acumulado Agora (R$):", value=1000.0)

    # Contexto de Hoje (Data da última atualização)
    hoje = datetime.strptime(df['Data'].iloc[-1], "%d/%m/%Y")
    peso_hoje_sem = PESOS_SEMANA[hoje.weekday() if hoje.weekday() < 6 else 0] # Ajuste Dom-Sab
    peso_hoje_mes = PESOS_MES[min(hoje.day - 1, 30)]

    # Cálculo do Acumulado Histórico
    idx_hora = hourly_cols.index(hora_alvo)
    df['Soma_Acumulada'] = df[hourly_cols[:idx_hora + 1]].sum(axis=1)

    # Filtragem por Similaridade (Margem de 15% para encontrar dias parecidos)
    margem = 0.15
    df_parecidos = df[(df['Soma_Acumulada'] >= v_acumulado * (1-margem)) & 
                      (df['Soma_Acumulada'] <= v_acumulado * (1+margem))].copy()

    if not df_parecidos.empty:
        # --- CÁLCULO DA PREVISÃO PONDERADA ---
        projeções = []
        for _, linha in df_parecidos.iterrows():
            dt = datetime.strptime(linha['Data'], "%d/%m/%Y")
            p_sem = PESOS_SEMANA[dt.weekday() if dt.weekday() < 6 else 0]
            p_mes = PESOS_MES[min(dt.day - 1, 30)]
            
            # Ajustamos o fechamento histórico para a realidade de HOJE
            # Formula: (Valor Final / Pesos do Passado) * Pesos de Hoje
            ajustado = (linha['Faturamento do dia'] / (p_sem * p_mes)) * (peso_hoje_sem * peso_hoje_mes)
            projeções.append(ajustado)

        expectativa = sum(projeções) / len(projeções)

        st.divider()
        st.subheader("🎯 Expectativa de Fechamento")
        st.metric("Média Ponderada", formatar_moeda(expectativa))
        st.caption(f"Ajustado para: {hoje.strftime('%d/%m')} ({['Seg','Ter','Qua','Qui','Sex','Sab','Dom'][hoje.weekday()]})")

        # Exibição dos Gêmeos
        with st.expander("Ver dias similares usados no cálculo"):
            st.table(df_parecidos[['Data', 'Soma_Acumulada', 'Faturamento do dia']])
    else:
        st.warning("Nenhum cenário similar encontrado no histórico.")
else:
    st.error("Arquivo Faturamento.csv não encontrado.")
