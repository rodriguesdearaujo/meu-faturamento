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

# --- MATRIZES DE PESO ---
PESOS_SEMANA = [0.677, 0.930, 0.878, 0.965, 1.016, 1.098, 1.435] # Dom a Sab
PESOS_MES = [
    0.94, 0.97, 0.99, 1.02, 1.05, 1.07, 1.10, 1.12, 1.11, 1.10,
    1.08, 1.07, 1.05, 1.04, 1.03, 1.02, 1.00, 0.99, 0.98, 0.97,
    0.96, 0.94, 0.93, 0.93, 0.92, 0.92, 0.91, 0.90, 0.90, 0.89, 0.89
]

# --- FUNÇÕES ---
def formatar_moeda(valor):
    parte_decimal = f"{valor:.2f}"
    inteiro, decimal = parte_decimal.split('.')
    resultado_inteiro = ""
    for i, digito in enumerate(reversed(inteiro)):
        if i > 0 and i % 3 == 0:
            resultado_inteiro = "." + resultado_inteiro
        resultado_inteiro = digito + resultado_inteiro
    return f"R$ {resultado_inteiro},{decimal}"

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

# --- CARGA DE DADOS ---
file_name = "Faturamento.csv" if os.path.exists("Faturamento.csv") else "faturamento.csv"
if os.path.exists(file_name):
    df = pd.read_csv(file_name, sep=';').copy()
    hourly_cols = [c for c in df.columns if ":" in c]
    for col in hourly_cols + ['Faturamento do dia']:
        df[col] = df[col].apply(clean_currency)

    st.title("🔮 Previsão e Histórico")
    st.write("Madureira Shopping")

    # --- DEFINIÇÃO DE HOJE ---
    data_escolhida = st.date_input("Data da projeção", value=datetime.now())
    hoje_obj = datetime.combine(data_escolhida, datetime.min.time())
    dias_traducao = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_semana_nome = dias_traducao[hoje_obj.weekday()]
    data_formatada = hoje_obj.strftime("%d/%m/%Y")

    # --- ENTRADAS DO USUÁRIO ---
    st.divider()
    hora_alvo = st.selectbox("Horário Atual:", hourly_cols, index=hourly_cols.index("18:00") if "18:00" in hourly_cols else 0)
    
    col1, col2 = st.columns(2)
    with col1:
        valor_centro = st.number_input("Faturamento Acumulado Atual (R$):", value=1100.0, step=50.0)
    with col2:
        margem_percentual = st.slider("Margem de busca (%):", min_value=0, max_value=50, value=5)

    # Cálculo do intervalo
    v_min = valor_centro * (1 - margem_percentual / 100)
    v_max = valor_centro * (1 + margem_percentual / 100)

    # SAÍDA LIMPA: Somente valores com duas casas decimais
    st.write(f"Buscando no histórico dias entre {v_min:.2f} e {v_max:.2f}")

    # Identifica pesos de hoje
    idx_sem_hoje = (hoje_obj.weekday() + 1) % 7
    peso_hoje_sem = PESOS_SEMANA[idx_sem_hoje]
    peso_hoje_mes = PESOS_MES[min(hoje_obj.day - 1, 30)]

    # Cálculo do Acumulado Histórico
    idx_hora = hourly_cols.index(hora_alvo)
    df['Soma_Acumulada'] = df[hourly_cols[:idx_hora + 1]].sum(axis=1)

    # Filtragem
    df_parecidos = df[
    (df['Soma_Acumulada'] >= v_min) &
    (df['Soma_Acumulada'] <= v_max)
    ].copy()

    considerar_mesmo_dia_semana = st.checkbox("Comparar apenas com o mesmo dia da semana")

    # Índice do dia da semana dos dias históricos
    df_parecidos["DiaSemanaIdx"] = df_parecidos["Data"].apply(
        lambda x: (datetime.strptime(x, "%d/%m/%Y").weekday() + 1) % 7
    )
    
    # Se marcado, mantém apenas os dias históricos com o mesmo dia da semana da data escolhida
    if considerar_mesmo_dia_semana:
        df_parecidos = df_parecidos[df_parecidos["DiaSemanaIdx"] == idx_sem_hoje]
    
    if not df_parecidos.empty:
    
    if not df_parecidos.empty:
        # --- CÁLCULO DA PREVISÃO ---
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
        st.subheader(f"🎯 Previsão para hoje ({dia_semana_nome}, {data_formatada})")
        st.metric("Expectativa de Fechamento", formatar_moeda(expectativa))
        
        st.info(f"O sistema identificou que hoje é um dia com peso **{peso_hoje_sem:.2f}** (semana) e **{peso_hoje_mes:.2f}** (mês).")
        st.write(f"Cálculo baseado em **{len(df_parecidos)} dias** similares encontrados no histórico.")

        with st.expander("Ver dias históricos comparados"):
            tabela_visual = []
            for _, linha in df_parecidos.iterrows():
                tabela_visual.append({
                    "Data": linha['Data'],
                    "Dia da Semana": obter_dia_semana(linha['Data']),
                    f"Acumulado {hora_alvo}": f"{linha['Soma_Acumulada']:.2f}",
                    "Final": f"{linha['Faturamento do dia']:.2f}"
                })
            st.table(tabela_visual)
    else:
        st.warning("Nenhum cenário similar encontrado.")
else:
    st.error("Arquivo Faturamento.csv não encontrado.")
