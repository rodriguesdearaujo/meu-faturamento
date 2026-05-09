import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurações de página para celular
st.set_page_config(page_title="Gestão Cheirin Bão", layout="centered")

# --- CONTROLE DE ACESSO ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("☕ Acesso Restrito")
        st.text_input("Digite a senha de acesso", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password"] == "1234": # <--- SUA SENHA
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.error("Senha incorreta")

def clean_currency(val):
    if isinstance(val, str):
        # Remove R$, espaços e ajusta os pontos/vírgulas brasileiros
        clean = val.replace('R$', '').replace('\xa0', '').strip()
        if not clean: return 0.0
        # Troca ponto de milhar por nada e vírgula decimal por ponto
        clean = clean.replace('.', '').replace(',', '.')
        try:
            return float(clean)
        except:
            return 0.0
    return val

if check_password():
    st.title("☕ Consulta de Faturamento")
    st.write("Unidade: Madureira Shopping")

    # Tenta carregar o arquivo (tratando F maiúsculo ou minúsculo)
    file_name = "Faturamento.csv" if os.path.exists("Faturamento.csv") else "faturamento.csv"

    if os.path.exists(file_name):
        @st.cache_data
        def load_data(fname):
            # Lendo com separador ; que é o padrão do seu arquivo
            df_raw = pd.read_csv(fname, sep=';', encoding='utf-8')
            
            # Limpando valores financeiros
            for col in df_raw.columns:
                if col != 'Data':
                    df_raw[col] = df_raw[col].apply(clean_currency)
            return df_raw

        df = load_data(file_name)

        # Interface de Filtro
        st.divider()
        st.subheader("🔍 Filtrar por Horário")
        
        lista_horarios = [c for c in df.columns if ":" in c]
        
        col1, col2 = st.columns(2)
        with col1:
            hora_selecionada = st.selectbox("Escolha a Hora", lista_horarios, index=len(lista_horarios)-6)
        with col2:
            st.write(f"Intervalo às {hora_selecionada}")
            v_min = st.number_input("Valor Mín (R$)", value=50.0, step=10.0)
            v_max = st.number_input("Valor Máx (R$)", value=500.0, step=10.0)

        # Filtragem lógica
        resultado = df[(df[hora_selecionada] >= v_min) & (df[hora_selecionada] <= v_max)].copy()

        if not resultado.empty:
            st.success(f"Encontramos {len(resultado)} dias com esse perfil!")
            
            # Gráfico Comparativo
            fig = px.bar(
                resultado, 
                x='Data', 
                y=[hora_selecionada, 'Faturamento do dia'],
                barmode='group',
                title="Total do Dia vs Faturamento na Hora",
                labels={'value': 'Valor (R$)', 'variable': 'Categoria'},
                color_discrete_sequence=['#ff7f0e', '#1f77b4']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela resumida
            st.dataframe(resultado[['Data', hora_selecionada, 'Faturamento do dia']], use_container_width=True)
        else:
            st.warning("Nenhum dia encontrado neste intervalo.")

    else:
        st.error(f"Arquivo '{file_name}' não encontrado no GitHub. Verifique o nome do arquivo enviado.")
