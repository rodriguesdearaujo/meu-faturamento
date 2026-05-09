# --- SAÍDA DOS RESULTADOS ---
    st.divider()
    if not df_filtrado.empty:
        st.subheader("📊 Resultados encontrados:")
        
        for _, linha in df_filtrado.iterrows():
            dia = linha['Data']
            # Formatação manual para garantir o padrão R$ 1.234,56
            acumulado_fmt = f"R$ {linha['Soma_Acumulada']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            total_dia_fmt = f"R$ {linha['Faturamento do dia']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Texto com espaçamento e negrito
            st.markdown(f"""
            📅 **Dia {dia}** Você atingiu **{acumulado_fmt}** até as {hora_alvo} e faturou **{total_dia_fmt}** no fechamento do dia.
            ---
            """)
    else:
        st.info("Nenhum dia encontrado com faturamento acumulado neste intervalo.")
