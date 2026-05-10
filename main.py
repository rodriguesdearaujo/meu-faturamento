import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E ACESSO ---
st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    st.title("☕ Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if senha == "1563":
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

def obter_dia_semana(data_str):
    try:
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        dias = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]
        idx = (data_obj.weekday() + 1) % 7
        return dias[idx]
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

    st.title("🔮 Previsão e Histórico")
    st.write("Madureira Shopping")

    # --- ENTRADAS (RESTAURADO O INTERVALO AQUI) ---
       st.divider()
        
        # Tradução do dia da semana para o cabeçalho
        dias_traducao = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        dia_semana_nome = dias_traducao[hoje_obj.weekday()]
        data_formatada = hoje_obj.strftime("%d/%m/%Y")

        st.subheader(f"🎯 Previsão para hoje ({dia_semana_nome}, {data_formatada})")
        
        col_metrica, col_info = st.columns([1, 1])
        with col_metrica:
            st.metric("Expectativa de Fechamento", formatar_moeda(expectativa))
        
        st.info(f"O sistema identificou que hoje é um dia com peso **{peso_hoje_sem:.2f}** (semana) e **{peso_hoje_mes:.2f}** (mês).")
        st.write(f"Cálculo baseado em **{len(df_parecidos)} dias** similares encontrados no histórico.")

    # Identifica contexto de hoje
    hoje_str = df['Data'].iloc[-1]
    hoje_obj = datetime.now()
    idx_sem_hoje = (hoje_obj.weekday() + 1) % 7
    peso_hoje_sem = PESOS_SEMANA[idx_sem_hoje]
    peso_hoje_mes = PESOS_MES[min(hoje_obj.day - 1, 30)]

    # Cálculo do Acumulado Histórico
    idx_hora = hourly_cols.index(hora_alvo)
    df['Soma_Acumulada'] = df[hourly_cols[:idx_hora + 1]].sum(axis=1)

    # Filtragem pelo Intervalo de Entrada
    df_parecidos = df[(df['Soma_Acumulada'] >= v_min) & (df['Soma_Acumulada'] <= v_max)].copy()

    if not df_parecidos.empty:
        # --- CÁLCULO DA PREVISÃO PONDERADA ---
        projeções = []
        for _, linha in df_parecidos.iterrows():
            dt = datetime.strptime(linha['Data'], "%d/%m/%Y")
            idx_sem_hist = (dt.weekday() + 1) % 7
            p_sem = PESOS_SEMANA[idx_sem_hist]
            p_mes = PESOS_MES[min(dt.day - 1, 30)]
            
            ajustado = (linha['Faturamento do dia'] / (p_sem * p_mes)) * (peso_hoje_sem * peso_hoje_mes)
            projeções.append(ajustado)

        expectativa = sum(projeções) / len(projeções)

        st.divider()
        st.subheader("🎯 Expectativa de Fechamento")
        st.metric("Média Ponderada", formatar_moeda(expectativa))
        st.info(f"Cálculo baseado em **{len(df_parecidos)} dias** dentro do intervalo informado.")

        # --- TABELA DE DIAS SEMELHANTES ---
        st.divider()
        st.subheader("📅 Gêmeos Históricos Encontrados")
        
        tabela_visual = []
        for _, linha in df_parecidos.iterrows():
            tabela_visual.append({
                "Data": linha['Data'],
                "Dia da Semana": obter_dia_semana(linha['Data']),
                f"Acumulado até {hora_alvo}": formatar_moeda(linha['Soma_Acumulada']),
                "Faturamento Final": formatar_moeda(linha['Faturamento do dia'])
            })
        
        st.table(tabela_visual)
        
    else:
        st.warning("Nenhum cenário similar encontrado no histórico para este intervalo.")
else:
    st.error("Arquivo Faturamento.csv não encontrado.")
