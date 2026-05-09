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
