# Função para mostrar relatórios
def mostrar_relatorios():
    st.markdown("<h1 class='main-header'>Relatórios</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Relatório de Evolução", "Relatório de Frequência", "Relatório de Habilidades", "Compartilhar via WhatsApp"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Gerar Relatório de Evolução</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente
        paciente_id = st.selectbox(
            "Selecione o Paciente",
            options=pacientes_df['id'].tolist(),
            format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
            key="paciente_relatorio"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            periodo_inicio = st.date_input("Data Inicial", value=datetime.date.today() - datetime.timedelta(days=30))
        
        with col2:
            periodo_fim = st.date_input("Data Final", value=datetime.date.today())
        
        opcoes_relatorio = st.multiselect(
            "Incluir no relatório",
            options=["Dados pessoais", "Resumo de atendimentos", "Gráficos de evolução", "Avaliações do período", "Habilidades trabalhadas", "Recomendações"],
            default=["Dados pessoais", "Resumo de atendimentos", "Habilidades trabalhadas"]
        )
        
        if st.button("Gerar Relatório de Evolução"):
            if paciente_id and len(opcoes_relatorio) > 0:
                # Buscar dados do paciente
                paciente = pacientes_df[pacientes_df['id'] == paciente_id].iloc[0]
                
                # Buscar atendimentos do período
                atendimentos_periodo = atendimentos_df[
                    (atendimentos_df['paciente_id'] == paciente_id) &
                    (atendimentos_df['data'] >= periodo_inicio.strftime('%Y-%m-%d')) &
                    (atendimentos_df['data'] <= periodo_fim.strftime('%Y-%m-%d'))
                ]
                
                st.markdown(f"<h2>Relatório de Evolução - {paciente['nome']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p>Período: {periodo_inicio.strftime('%d/%m/%Y')} a {periodo_fim.strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
                
                if "Dados pessoais" in opcoes_relatorio:
                    st.markdown("### Dados Pessoais")
                    st.markdown(f"**Nome:** {paciente['nome']}")
                    if 'data_nascimento' in paciente and str(paciente['data_nascimento']) != 'nan':
                        data_nasc = datetime.datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                        idade = (datetime.datetime.now() - data_nasc).days // 365
                        st.markdown(f"**Idade:** {idade} anos")
                    st.markdown(f"**Diagnóstico:** {paciente['diagnostico']}")
                    if 'nivel_suporte' in paciente and paciente['nivel_suporte'] and str(paciente['nivel_suporte']) != 'nan':
                        st.markdown(f"**Nível de Suporte:** {paciente['nivel_suporte']}")
                
                if "Resumo de atendimentos" in opcoes_relatorio:
                    st.markdown("### Resumo de Atendimentos")
                    st.markdown(f"**Total de atendimentos no período:** {len(atendimentos_periodo)}")
                    
                    if len(atendimentos_periodo) > 0:
                        st.markdown("#### Evolução observada")
                        for i, atendimento in atendimentos_periodo.iterrows():
                            st.markdown(f"**Sessão {atendimento['data']}:**")
                            if 'evolucao' in atendimento:
                                st.markdown(atendimento['evolucao'])
                
                if "Habilidades trabalhadas" in opcoes_relatorio and len(atendimentos_periodo) > 0:
                    st.markdown("### Habilidades Trabalhadas")
                    
                    # Contar frequência de habilidades
                    habilidades_contagem = {}
                    for i, atendimento in atendimentos_periodo.iterrows():
                        if 'habilidades_trabalhadas' in atendimento and isinstance(atendimento['habilidades_trabalhadas'], str):
                            for hab in atendimento['habilidades_trabalhadas'].split(','):
                                hab = hab.strip()
                                if hab:
                                    if hab in habilidades_contagem:
                                        habilidades_contagem[hab] += 1
                                    else:
                                        habilidades_contagem[hab] = 1
                    
                    # Exibir habilidades mais trabalhadas
                    if habilidades_contagem:
                        # Ordenar por frequência
                        habilidades_ordenadas = sorted(habilidades_contagem.items(), key=lambda x: x[1], reverse=True)
                        
                        # Criar gráfico
                        fig, ax = plt.subplots(figsize=(10, 6))
                        habs, frequencias = zip(*habilidades_ordenadas[:10])  # Top 10
                        ax.barh(habs, frequencias, color='purple')
                        ax.set_xlabel('Número de Sessões')
                        ax.set_title('Habilidades Mais Trabalhadas no Período')
                        st.pyplot(fig)
                
                if "Gráficos de evolução" in opcoes_relatorio:
                    st.markdown("### Gráficos de Evolução")
                    st.info("Simulação: Gráficos seriam gerados com base em métricas quantitativas de evolução.")
                    
                    # Simulação de gráfico de evolução
                    fig, ax = plt.subplots(figsize=(10, 6))
                    datas = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in sorted(atendimentos_periodo['data'].unique())]
                    valores = np.cumsum(np.random.rand(len(datas)) * 0.5 + 0.5)  # Simulação de progresso
                    
                    ax.plot(datas, valores, marker='o', linestyle='-', color='purple')
                    ax.set_xlabel('Data')
                    ax.set_ylabel('Nível de Habilidade (simulado)')
                    ax.set_title('Evolução das Habilidades ao Longo do Tempo')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                
                if "Avaliações do período" in opcoes_relatorio:
                    st.markdown("### Avaliações no Período")
                    
                    avaliacoes_periodo = avaliacoes_df[
                        (avaliacoes_df['paciente_id'] == paciente_id) &
                        (avaliacoes_df['data'] >= periodo_inicio.strftime('%Y-%m-%d')) &
                        (avaliacoes_df['data'] <= periodo_fim.strftime('%Y-%m-%d'))
                    ]
                    
                    if len(avaliacoes_periodo) > 0:
                        for i, avaliacao in avaliacoes_periodo.iterrows():
                            st.markdown(f"#### {avaliacao['data']} - {avaliacao['tipo_avaliacao']}")
                            st.markdown("**Resultados:**")
                            if 'resultados' in avaliacao:
                                st.markdown(avaliacao['resultados'])
                            st.markdown("**Recomendações:**")
                            if 'recomendacoes' in avaliacao:
                                st.markdown(avaliacao['recomendacoes'])
                    else:
                        st.info("Não foram realizadas avaliações no período selecionado.")
                
                if "Recomendações" in opcoes_relatorio:
                    st.markdown("### Recomendações para o Próximo Período")
                    st.text_area("Adicione recomendações para o próximo período", height=150)
                
                # Botões de exportação
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "Exportar como PDF",
                        data="Simulação de PDF",
                        file_name=f"Relatorio_{paciente['nome']}_{periodo_inicio.strftime('%d%m%Y')}_{periodo_fim.strftime('%d%m%Y')}.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    st.download_button(
                        "Exportar como Word",
                        data="Simulação de DOCX",
                        file_name=f"Relatorio_{paciente['nome']}_{periodo_inicio.strftime('%d%m%Y')}_{periodo_fim.strftime('%d%m%Y')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                with col3:
                    if st.button("Enviar por WhatsApp"):
                        st.success("Simulação: Relatório enviado por WhatsApp para o responsável!")
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Relatório de Frequência</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes_ano_freq = st.date_input(
                "Selecione o mês",
                value=datetime.date.today().replace(day=1),
                format="MM/YYYY",
                key="mes_freq"
            )
        
        with col2:
            paciente_freq = st.selectbox(
                "Paciente (opcional)",
                options=[0] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == 0 else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
                key="paciente_freq"
            )
        
        if st.button("Gerar Relatório de Frequência"):
            st.markdown("<h3>Relatório de Frequência</h3>", unsafe_allow_html=True)
            
            # Determinar dias do mês
            primeiro_dia = mes_ano_freq.replace(day=1)
            if mes_ano_freq.month == 12:
                ultimo_dia = mes_ano_freq.replace(year=mes_ano_freq.year + 1, month=1, day=1) - datetime.timedelta(days=1)
            else:
                ultimo_dia = mes_ano_freq.replace(month=mes_ano_freq.month + 1, day=1) - datetime.timedelta(days=1)
            
            # Filtrar agendamentos do mês
            agendamentos_mes = agendamentos_df[
                (agendamentos_df['data'] >= primeiro_dia.strftime('%Y-%m-%d')) & 
                (agendamentos_df['data'] <= ultimo_dia.strftime('%Y-%m-%d'))
            ]
            
            if paciente_freq != 0:
                agendamentos_mes = agendamentos_mes[agendamentos_mes['paciente_id'] == paciente_freq]
            
            # Calcular estatísticas
            total_agendamentos = len(agendamentos_mes)
            
            if total_agendamentos > 0:
                # Simular análise de faltas
                status_counts = {
                    "Concluído": len(agendamentos_mes[agendamentos_mes['status'] == "Concluído"]),
                    "Faltou": len(agendamentos_mes[agendamentos_mes['status'] == "Faltou"]),
                    "Cancelado": len(agendamentos_mes[agendamentos_mes['status'] == "Cancelado"]),
                    "Outros": len(agendamentos_mes[~agendamentos_mes['status'].isin(["Concluído", "Faltou", "Cancelado"])])
                }
                
                # Exibir estatísticas gerais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Sessões", total_agendamentos)
                
                with col2:
                    taxa_presenca = status_counts["Concluído"] / total_agendamentos * 100 if total_agendamentos > 0 else 0
                    st.metric("Taxa de Presença", f"{taxa_presenca:.1f}%")
                
                with col3:
                    taxa_falta = status_counts["Faltou"] / total_agendamentos * 100 if total_agendamentos > 0 else 0
                    st.metric("Taxa de Faltas", f"{taxa_falta:.1f}%")
                
                with col4:
                    taxa_cancel = status_counts["Cancelado"] / total_agendamentos * 100 if total_agendamentos > 0 else 0
                    st.metric("Taxa de Cancelamentos", f"{taxa_cancel:.1f}%")
                
                # Gráfico de frequência
                fig, ax = plt.subplots(figsize=(10, 6))
                labels = status_counts.keys()
                sizes = status_counts.values()
                colors = ['#4CAF50', '#F44336', '#FFC107', '#9E9E9E']
                
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
                
                # Lista de faltas
                if status_counts["Faltou"] > 0:
                    st.markdown("<h3>Detalhamento de Faltas</h3>", unsafe_allow_html=True)
                    
                    faltas = agendamentos_mes[agendamentos_mes['status'] == "Faltou"]
                    faltas = faltas.merge(
                        pacientes_df[['id', 'nome']], 
                        left_on='paciente_id', 
                        right_on='id', 
                        suffixes=('', '_paciente')
                    )
                    
                    for i, falta in faltas.iterrows():
                        st.markdown(
                            f"<div style='background-color:#FFEBEE; padding:10px; margin:5px; border-radius:5px;'>"
                            f"**{falta['data']} às {falta['horario']}** - {falta['nome']} (Terapeuta: {falta['terapeuta']})"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                
                # Oferecer download do relatório
                st.download_button(
                    "Exportar Relatório de Frequência",
                    data="Simulação de relatório de frequência",
                    file_name=f"Frequencia_{mes_ano_freq.strftime('%m%Y')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("Não há dados de agendamento para o período selecionado.")
    
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Relatório de Habilidades</h2>", unsafe_allow_html=True)
        
        # Filtros para o relatório
        col1, col2 = st.columns(2)
        
        with col1:
            paciente_hab = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
                key="paciente_hab"
            )
        
        with col2:
            periodo_hab = st.selectbox(
                "Período de Análise",
                options=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"]
            )
        
        if st.button("Analisar Habilidades"):
            st.markdown("<h3>Análise de Habilidades Trabalhadas</h3>", unsafe_allow_html=True)
            
            # Determinar período de análise
            hoje = datetime.date.today()
            if periodo_hab == "Último mês":
                data_inicio = hoje - datetime.timedelta(days=30)
            elif periodo_hab == "Últimos 3 meses":
                data_inicio = hoje - datetime.timedelta(days=90)
            elif periodo_hab == "Últimos 6 meses":
                data_inicio = hoje - datetime.timedelta(days=180)
            else:  # Último ano
                data_inicio = hoje - datetime.timedelta(days=365)
            
            # Filtrar atendimentos do período
            atendimentos_periodo = atendimentos_df[
                (atendimentos_df['paciente_id'] == paciente_hab) &
                (atendimentos_df['data'] >= data_inicio.strftime('%Y-%m-%d')) &
                (atendimentos_df['data'] <= hoje.strftime('%Y-%m-%d'))
            ]
            
            # Buscar dados do paciente
            paciente = pacientes_df[pacientes_df['id'] == paciente_hab].iloc[0]
            
            if len(atendimentos_periodo) > 0:
                st.markdown(f"**Paciente:** {paciente['nome']}")
                st.markdown(f"**Período analisado:** {data_inicio.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}")
                st.markdown(f"**Total de atendimentos:** {len(atendimentos_periodo)}")
                
                # Analisar habilidades trabalhadas
                habilidades_contagem = {}
                for i, atendimento in atendimentos_periodo.iterrows():
                    if 'habilidades_trabalhadas' in atendimento and isinstance(atendimento['habilidades_trabalhadas'], str):
                        for hab in atendimento['habilidades_trabalhadas'].split(','):
                            hab = hab.strip()
                            if hab:
                                if hab in habilidades_contagem:
                                    habilidades_contagem[hab] += 1
                                else:
                                    habilidades_contagem[hab] = 1
                
                if habilidades_contagem:
                    # Ordenar por frequência
                    habilidades_ordenadas = sorted(habilidades_contagem.items(), key=lambda x: x[1], reverse=True)
                    
                    # Criar gráfico
                    fig, ax = plt.subplots(figsize=(12, 8))
                    habs, frequencias = zip(*habilidades_ordenadas)
                    
                    # Limite para exibir no máximo 15 habilidades
                    max_habs = min(15, len(habs))
                    ax.barh(habs[:max_habs], frequencias[:max_habs], color='purple')
                    ax.set_xlabel('Número de Sessões')
                    ax.set_title('Habilidades Trabalhadas no Período')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Análise de prioridades vs. habilidades trabalhadas
                    st.markdown("### Análise de Prioridades")
                    st.markdown("""
                    A análise abaixo compara as habilidades que precisam ser priorizadas com base na avaliação
                    mais recente e o número de sessões em que cada habilidade foi trabalhada.
                    """)
                    
                    # Simulação de habilidades prioritárias baseadas em avaliação
                    habilidades_prioritarias = {
                        "Equilíbrio estático": 8,
                        "Coordenação motora fina": 7,
                        "Cruzamento de linha média": 6,
                        "Planejamento motor": 9,
                        "Percepção espacial": 5
                    }
                    
                    # Comparar habilidades trabalhadas vs. prioritárias
                    dados_comparacao = []
                    
                    for hab, prioridade in habilidades_prioritarias.items():
                        frequencia = habilidades_contagem.get(hab, 0)
                        dados_comparacao.append({
                            'habilidade': hab,
                            'prioridade': prioridade,
                            'frequencia': frequencia
                        })
                    
                    # Criar gráfico de comparação
                    fig, ax = plt.subplots(figsize=(12, 6))
                    habs = [item['habilidade'] for item in dados_comparacao]
                    prioridades = [item['prioridade'] for item in dados_comparacao]
                    frequencias = [item['frequencia'] for item in dados_comparacao]
                    
                    x = np.arange(len(habs))
                    width = 0.35
                    
                    ax.bar(x - width/2, prioridades, width, label='Prioridade (0-10)', color='#7B1FA2')
                    ax.bar(x + width/2, frequencias, width, label='Sessões Realizadas', color='#4CAF50')
                    
                    ax.set_xticks(x)
                    ax.set_xticklabels(habs, rotation=45, ha='right')
                    ax.legend()
                    ax.set_title('Prioridades vs. Habilidades Trabalhadas')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Identificar habilidades sub-trabalhadas
                    st.markdown("### Recomendações")
                    
                    habilidades_subtrabalhadas = []
                    for item in dados_comparacao:
                        if item['prioridade'] > item['frequencia'] + 2:  # Prioridade maior que frequência + margem
                            habilidades_subtrabalhadas.append(item['habilidade'])
                    
                    if habilidades_subtrabalhadas:
                        st.markdown("#### Habilidades que precisam de mais atenção:")
                        for hab in habilidades_subtrabalhadas:
                            st.markdown(f"- **{hab}**")
                        
                        st.info("""
                        Recomenda-se aumentar o foco nestas habilidades nas próximas sessões, 
                        pois elas foram identificadas como prioritárias na avaliação, mas não estão 
                        recebendo atenção suficiente nos atendimentos.
                        """)
                    else:
                        st.success("As habilidades prioritárias estão sendo adequadamente trabalhadas!")
                else:
                    st.warning("Não foi possível encontrar dados de habilidades trabalhadas no período selecionado.")
            else:
                st.info(f"Não há registros de atendimentos para {paciente['nome']} no período selecionado.")
    
    with tabs[3]:
        st.markdown("<h2 class='sub-header'>Compartilhar Relatórios via WhatsApp</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente e tipo de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            paciente_whats = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
                key="paciente_whats"
            )
        
        with col2:
            tipo_relatorio = st.selectbox(
                "Tipo de Relatório",
                options=["Evolução Mensal", "Evolução Trimestral", "Relatório de Avaliação", "Relatório de Frequência", "Relatório Personalizado"]
            )
        
        # Opções para grupos de WhatsApp
        st.markdown("### Opções de Envio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            destinatario = st.radio(
                "Destinatário",
                options=["Grupo da família", "Responsável direto", "Equipe multidisciplinar", "Personalizado"]
            )
        
        with col2:
            if destinatario == "Personalizado":
                numero_whatsapp = st.text_input("Número de WhatsApp (com DDD)")
            
            incluir_anexos = st.checkbox("Incluir anexos (gráficos e tabelas)")
        
        # Mensagem personalizada
        st.markdown("### Mensagem Personalizada (opcional)")
        mensagem = st.text_area("Adicione uma mensagem personalizada ao relatório")
        
        if st.button("Enviar Relatório via WhatsApp"):
            if paciente_whats:
                # Buscar dados do paciente
                paciente = pacientes_df[pacientes_df['id'] == paciente_whats].iloc[0]
                
                # Simulação de envio
                st.success(f"Simulação: Relatório {tipo_relatorio} de {paciente['nome']} enviado com sucesso para {destinatario}!")
                
                # Exibir prévia da mensagem
                st.markdown("### Prévia da Mensagem")
                st.markdown("<div style='background-color:#E1F5FE; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)
                st.markdown(f"*Relatório {tipo_relatorio} - {paciente['nome']}*")
                st.markdown("Prezado(a) responsável,")
                st.markdown(f"Segue o relatório de {tipo_relatorio} do paciente {paciente['nome']}.")
                
                if mensagem:
                    st.markdown(f"*Nota do terapeuta:*\n{mensagem}")
                
                st.markdown("Atenciosamente,\nEquipe de Psicomotricidade")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Por favor, selecione um paciente para enviar o relatório.")# Função para mostrar agendamentos
def mostrar_agendamentos():
    st.markdown("<h1 class='main-header'>Agendamentos</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Novo Agendamento", "Calendário", "Gestão de Agendamentos", "Agrupamentos Sugeridos"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Agendar Nova Sessão</h2>", unsafe_allow_html=True)
        
        with st.form("form_agendamento"):
            # Seleção de paciente
            paciente_id = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
                key="paciente_agendamento"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_agendamento = st.date_input("Data da Sessão", min_value=datetime.date.today())
                horario = st.time_input("Horário", value=datetime.time(8, 0))
            
            with col2:
                terapeuta = st.text_input("Terapeuta Responsável", key="terapeuta_agendamento")
                status = st.selectbox("Status", ["Agendado", "Confirmado", "Em andamento", "Concluído", "Cancelado", "Faltou"])
            
            observacao = st.text_area("Observações", height=100)
            
            # Opção para gerar no Google Calendar
            col1, col2 = st.columns(2)
            with col1:
                gerar_gcal = st.checkbox("Gerar evento no Google Calendar")
            
            with col2:
                exportar_excel = st.checkbox("Exportar para Excel")
            
            submitted = st.form_submit_button("Agendar Sessão")
            
            if submitted:
                # Verificar dados obrigatórios
                if not paciente_id or not data_agendamento or not horario or not terapeuta:
                    st.error("Por favor, preencha os campos obrigatórios.")
                else:
                    # Criar novo ID
                    novo_id = 1
                    if len(agendamentos_df) > 0:
                        novo_id = int(agendamentos_df['id'].max()) + 1
                    
                    # Adicionar novo agendamento
                    novo_agendamento = {
                        'id': novo_id,
                        'paciente_id': paciente_id,
                        'data': data_agendamento.strftime('%Y-%m-%d'),
                        'horario': horario.strftime('%H:%M'),
                        'terapeuta': terapeuta,
                        'status': status,
                        'observacao': observacao
                    }
                    
                    agendamentos_df.loc[len(agendamentos_df)] = novo_agendamento
                    agendamentos_df.to_csv("dados/agendamentos.csv", index=False)
                    
                    # Mensagem de feedback
                    msg = f"Sessão agendada com sucesso!"
                    
                    if gerar_gcal:
                        msg += " (Google Calendar: simulado)"
                    
                    if exportar_excel:
                        msg += " (Excel: simulado)"
                    
                    st.success(msg)
                    time.sleep(1)
                    st.experimental_rerun()
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Calendário de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Escolher mês e ano
        col1, col2 = st.columns(2)
        with col1:
            mes_ano = st.date_input(
                "Selecione o mês",
                value=datetime.date.today().replace(day=1),
                format="MM/YYYY"
            )
        
        with col2:
            filtro_terapeuta = st.text_input("Filtrar por terapeuta")
        
        # Determinar dias do mês
        primeiro_dia = mes_ano.replace(day=1)
        if mes_ano.month == 12:
            ultimo_dia = mes_ano.replace(year=mes_ano.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            ultimo_dia = mes_ano.replace(month=mes_ano.month + 1, day=1) - datetime.timedelta(days=1)
        
        # Filtrar agendamentos do mês
        agendamentos_mes = agendamentos_df[
            (agendamentos_df['data'] >= primeiro_dia.strftime('%Y-%m-%d')) & 
            (agendamentos_df['data'] <= ultimo_dia.strftime('%Y-%m-%d'))
        ]
        
        if filtro_terapeuta:
            agendamentos_mes = agendamentos_mes[agendamentos_mes['terapeuta'].str.contains(filtro_terapeuta, case=False, na=False)]
        
        # Criar visualização de calendário
        st.markdown("<h3>Visão de Calendário</h3>", unsafe_allow_html=True)
        
        # Simulação de interface de calendário
        dias_mes = (ultimo_dia - primeiro_dia).days + 1
        semanas = []
        dia_atual = primeiro_dia
        semana_atual = []
        
        # Preencher dias vazios até o primeiro dia do mês cair no dia correto da semana
        dia_semana_inicio = primeiro_dia.weekday()
        for _ in range(dia_semana_inicio):
            semana_atual.append(None)
        
        # Preencher os dias do mês
        for _ in range(dias_mes):
            semana_atual.append(dia_atual)
            if len(semana_atual) == 7:
                semanas.append(semana_atual)
                semana_atual = []
            dia_atual = dia_atual + datetime.timedelta(days=1)
        
        # Preencher o restante da última semana se necessário
        if semana_atual:
            while len(semana_atual) < 7:
                semana_atual.append(None)
            semanas.append(semana_atual)
        
        # Exibir calendário
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        
        # Cabeçalho dos dias da semana
        cols = st.columns(7)
        for i, dia in enumerate(dias_semana):
            cols[i].markdown(f"<div style='text-align:center'><b>{dia}</b></div>", unsafe_allow_html=True)
        
        # Exibir semanas
        for semana in semanas:
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                if dia:
                    # Verificar se há agendamentos para este dia
                    agendamentos_dia = agendamentos_mes[agendamentos_mes['data'] == dia.strftime('%Y-%m-%d')]
                    num_agendamentos = len(agendamentos_dia)
                    
                    # Estilo para destacar o dia atual
                    estilo = ""
                    if dia == datetime.date.today():
                        estilo = "background-color: #E1BEE7; font-weight: bold;"
                    
                    # Exibir dia e número de agendamentos
                    cols[i].markdown(
                        f"<div style='text-align:center; padding:5px; border-radius:5px; {estilo}'>"
                        f"<b>{dia.day}</b><br/>"
                        f"{num_agendamentos} sessões"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Se houver agendamentos, exibir eles
                    if num_agendamentos > 0:
                        for _, agendamento in agendamentos_dia.iterrows():
                            # Buscar nome do paciente
                            nome_paciente = pacientes_df[pacientes_df['id'] == agendamento['paciente_id']]['nome'].iloc[0] if agendamento['paciente_id'] in pacientes_df['id'].values else "Desconhecido"
                            
                            # Cor baseada no status
                            cor_status = {
                                "Agendado": "#E3F2FD",
                                "Confirmado": "#DCEDC8",
                                "Em andamento": "#FFF9C4",
                                "Concluído": "#C8E6C9",
                                "Cancelado": "#FFCDD2",
                                "Faltou": "#FFCCBC"
                            }.get(agendamento['status'], "#ECEFF1")
                            
                            cols[i].markdown(
                                f"<div style='background-color:{cor_status}; padding:3px; margin:2px; border-radius:3px; font-size:0.8em;'>"
                                f"{agendamento['horario']} - {nome_paciente[:10]}...</div>",
                                unsafe_allow_html=True
                            )
                else:
                    # Dia vazio
                    cols[i].markdown("", unsafe_allow_html=True)
    
    with tabs[2]:
        st.markdown("<h2 class='sub-header'>Gestão de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            periodo = st.date_input(
                "Período",
                [datetime.date.today(), datetime.date.today() + datetime.timedelta(days=7)]
            )
        
        with col2:
            filtro_paciente = st.selectbox(
                "Paciente",
                options=[0] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == 0 else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "",
                key="filtro_agenda_paciente"
            )
        
        with col3:
            filtro_status = st.multiselect(
                "Status",
                options=["Agendado", "Confirmado", "Em andamento", "Concluído", "Cancelado", "Faltou"]
            )
        
        # Aplicar filtros
        if len(periodo) == 2:
            inicio, fim = periodo
            agendamentos_filtrados = agendamentos_df[
                (agendamentos_df['data'] >= inicio.strftime('%Y-%m-%d')) & 
                (agendamentos_df['data'] <= fim.strftime('%Y-%m-%d'))
            ]
        else:
            agendamentos_filtrados = agendamentos_df.copy()
        
        if filtro_paciente != 0:
            agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['paciente_id'] == filtro_paciente]
        
        if filtro_status:
            agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['status'].isin(filtro_status)]
        
        # Ordenar por data e horário
        agendamentos_filtrados = agendamentos_filtrados.sort_values(['data', 'horario'])
        
        # Juntar com nomes dos pacientes
        if len(agendamentos_filtrados) > 0:
            agendamentos_completos = agendamentos_filtrados.merge(
                pacientes_df[['id', 'nome']], 
                left_on='paciente_id', 
                right_on='id', 
                suffixes=('', '_paciente')
            )
            
            # Exibir lista de agendamentos
            st.markdown("### Lista de Agendamentos")
            
            for i, agendamento in agendamentos_completos.iterrows():
                # Determinar cor baseada no status
                cor_status = {
                    "Agendado": "#E3F2FD",
                    "Confirmado": "#DCEDC8",
                    "Em andamento": "#FFF9C4",
                    "Concluído": "#C8E6C9",
                    "Cancelado": "#FFCDD2",
                    "Faltou": "#FFCCBC"
                }.get(agendamento['status'], "#ECEFF1")
                
                st.markdown(
                    f"<div style='background-color:{cor_status}; padding:10px; margin:5px; border-radius:5px;'>",
                    unsafe_allow_html=True
                )
                
                col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                
                with col1:
                    st.markdown(f"**{agendamento['data']}**<br>{agendamento['horario']}", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{agendamento['nome']}**<br>Terapeuta: {agendamento['terapeuta']}", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"**Status:** {agendamento['status']}<br>", unsafe_allow_html=True)
                    if 'observacao' in agendamento and agendamento['observacao'] and str(agendamento['observacao']) != 'nan':
                        st.markdown(f"Obs: {agendamento['observacao'][:30]}...", unsafe_allow_html=True)
                
                with col4:
                    # Botões de ação
                    if st.button("Editar", key=f"edit_{agendamento['id']}"):
                        st.session_state.editar_agendamento = agendamento['id']
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Modal de edição (simplificado)
            if 'editar_agendamento' in st.session_state and st.session_state.editar_agendamento:
                agendamento_id = st.session_state.editar_agendamento
                agendamento = agendamentos_df[agendamentos_df['id'] == agendamento_id].iloc[0]
                
                st.markdown("<h3>Editar Agendamento</h3>", unsafe_allow_html=True)
                
                with st.form("form_editar_agendamento"):
                    # Campos de edição
                    status_options = ["Agendado", "Confirmado", "Em andamento", "Concluído", "Cancelado", "Faltou"]
                    status_index = status_options.index(agendamento['status']) if agendamento['status'] in status_options else 0
                    novo_status = st.selectbox("Status", options=status_options, index=status_index)
                    
                    nova_observacao = st.text_area("Observação", value=agendamento['observacao'] if isinstance(agendamento['observacao'], str) else "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar Alterações"):
                            # Atualizar dados
                            agendamentos_df.loc[agendamentos_df['id'] == agendamento_id, 'status'] = novo_status
                            agendamentos_df.loc[agendamentos_df['id'] == agendamento_id, 'observacao'] = nova_observacao
                            
                            # Salvar alterações
                            agendamentos_df.to_csv("dados/agendamentos.csv", index=False)
                            
                            # Limpar estado e recarregar
                            st.session_state.editar_agendamento = None
                            st.success("Agendamento atualizado com sucesso!")
                            time.sleep(1)
                            st.experimental_rerun()
                    
                    with col2:
                        if st.form_submit_button("Cancelar"):
                            st.session_state.editar_agendamento = None
                            st.experimental_rerun()
        else:
            st.info("Nenhum agendamento encontrado com os filtros selecionados.")
    
    with tabs[3]:
        st.markdown("<h2 class='sub-header'>Sugestões de Agrupamentos</h2>", unsafe_allow_html=True)
        st.markdown("""
        Este sistema analisa o perfil dos pacientes e sugere possíveis agrupamentos para sessões em conjunto, 
        baseados em compatibilidade de perfil comportamental, habilidades a serem trabalhadas e nível de suporte.
        """)
        
        # Seleção de data para análise
        data_analise = st.date_input("Data para análise", value=datetime.date.today())
        
        # Simular algoritmo de compatibilidade
        if st.button("Gerar Sugestões de Agrupamentos"):
            st.markdown("### Sugestões de Agrupamentos")
            
            # Em um sistema real, isso seria um algoritmo complexo que analisaria
            # os dados de avaliação, comportamento, nível de suporte, etc.
            # Aqui vamos simular alguns resultados
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Grupo 1: Coordenação Motora Global")
            st.markdown("**Horário sugerido:** 09:00 - 10:00")
            st.markdown("**Pacientes compatíveis:**")
            st.markdown("1. Maria Silva (8 anos) - Nível de suporte 1")
            st.markdown("2. Pedro Costa (7 anos) - Nível de suporte 1")
            st.markdown("3. Lucas Oliveira (9 anos) - Nível de suporte 1")
            st.markdown("**Compatibilidade:** Alta (87%)")
            st.markdown("**Observações:** Todos os pacientes precisam desenvolver coordenação motora global e têm comportamento compatível em grupo.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Grupo 2: Equilíbrio e Praxia")
            st.markdown("**Horário sugerido:** 10:30 - 11:30")
            st.markdown("**Pacientes compatíveis:**")
            st.markdown("1. João Santos (10 anos) - Nível de suporte 2")
            st.markdown("2. Ana Oliveira (9 anos) - Nível de suporte 1")
            st.markdown("**Compatibilidade:** Média (72%)")
            st.markdown("**Observações:** Ambos precisam desenvolver equilíbrio. Ana pode ajudar a modelar comportamento para João.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Grupo 3: Coordenação Motora Fina")
            st.markdown("**Horário sugerido:** 14:00 - 15:00")
            st.markdown("**Pacientes compatíveis:**")
            st.markdown("1. Luiza Mendes (6 anos) - Nível de suporte 1")
            st.markdown("2. Gabriel Alves (7 anos) - Nível de suporte 2")
            st.markdown("3. Sofia Castro (6 anos) - Nível de suporte 1")
            st.markdown("**Compatibilidade:** Média-Alta (75%)")
            st.markdown("**Observações:** Todos precisam desenvolver coordenação motora fina. Atenção especial para Gabriel que pode precisar de mais suporte.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Oferecer opção de criar agendamentos baseados nas sugestões
            st.markdown("---")
            st.markdown("Deseja criar agendamentos baseados nestas sugestões?")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Agendar Grupo 1"):
                    st.success("Simulação: Agendamentos para Grupo 1 criados com sucesso!")
            
            with col2:
                if st.button("Agendar Grupo 2"):
                    st.success("Simulação: Agendamentos para Grupo 2 criados com sucesso!")
            
            with col3:
                if st.button("Agendar Grupo 3"):
                    st.success("Simulação: Agendamentos para Grupo 3 criados com sucesso!")import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json
import os
import base64
from PIL import Image
import io
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

# Configuração da página
st.set_page_config(
    page_title="NeuroBase - Sistema de Gestão em Psicomotricidade",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS customizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #5E35B1;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .icon-text {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .skill-tag {
        background-color: #E1BEE7;
        color: #4A148C;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        display: inline-block;
        font-size: 0.85rem;
        cursor: pointer;
    }
    .skill-tag-selected {
        background-color: #7B1FA2;
        color: white;
    }
    .metric-card {
        background-color: #EDE7F6;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .tabs-container {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Habilidades psicomotoras para seleção
HABILIDADES_PSICOMOTORAS = {
    "Tonicidade": [
        "Regulação de tônus muscular", 
        "Sustentação corporal", 
        "Preparo para ação"
    ],
    "Equilíbrio": [
        "Equilíbrio estático", 
        "Equilíbrio dinâmico", 
        "Recuperação de equilíbrio"
    ],
    "Esquema Corporal": [
        "Identificação de partes do corpo", 
        "Consciência corporal", 
        "Imagem corporal"
    ],
    "Lateralidade": [
        "Dominância lateral", 
        "Orientação direita/esquerda", 
        "Cruzamento de linha média"
    ],
    "Coordenação Motora Global": [
        "Coordenação de grandes movimentos", 
        "Saltos", 
        "Corrida", 
        "Arremessos"
    ],
    "Coordenação Motora Fina": [
        "Preensão", 
        "Manipulação de objetos pequenos", 
        "Grafomotricidade", 
        "Recorte"
    ],
    "Noção Espacial": [
        "Orientação espacial", 
        "Organização espacial", 
        "Relações espaciais"
    ],
    "Noção Temporal": [
        "Sequência temporal", 
        "Ritmo", 
        "Duração"
    ],
    "Praxia": [
        "Planejamento motor", 
        "Imitação de gestos", 
        "Sequenciamento motor"
    ],
    "Habilidades Socioemocionais": [
        "Expressão corporal", 
        "Regulação emocional", 
        "Interação social"
    ],
    "Habilidades Cognitivas": [
        "Atenção", 
        "Memória", 
        "Percepção", 
        "Resolução de problemas"
    ]
}

# Tipos de Avaliações
TIPOS_AVALIACAO = [
    "EDM - Escala de Desenvolvimento Motor (Rosa Neto)",
    "TGMD-2 - Test of Gross Motor Development",
    "FAMA - Ferramenta de Avaliação Motora para Autismo",
    "Bateria Psicomotora de Vítor da Fonseca",
    "Escala de Equilíbrio de Berg",
    "Protocolo de Avaliação de Coordenação Motora Fina",
    "Avaliação Inicial",
    "Reavaliação",
    "Avaliação Personalizada"
]

# Função para carregar ou criar dados
def load_data():
    # Criar diretórios de dados se não existirem
    os.makedirs("dados", exist_ok=True)
    
    # Arquivos de dados
    pacientes_file = "dados/pacientes.csv"
    atendimentos_file = "dados/atendimentos.csv"
    avaliacoes_file = "dados/avaliacoes.csv"
    agendamentos_file = "dados/agendamentos.csv"
    
    # Carregar ou criar dados de pacientes
    if os.path.exists(pacientes_file):
        pacientes_df = pd.read_csv(pacientes_file)
    else:
        pacientes_df = pd.DataFrame({
            'id': [],
            'nome': [],
            'data_nascimento': [],
            'responsavel': [],
            'telefone': [],
            'email': [],
            'data_entrada': [],
            'diagnostico': [],
            'nivel_suporte': [],
            'foto': [],
            'preferencias': [],
            'coisas_acalmam': [],
            'nao_gosta': [],
            'gatilhos': [],
            'brinquedos_favoritos': []
        })
        pacientes_df.to_csv(pacientes_file, index=False)
    
    # Carregar ou criar dados de atendimentos
    if os.path.exists(atendimentos_file):
        atendimentos_df = pd.read_csv(atendimentos_file)
    else:
        atendimentos_df = pd.DataFrame({
            'id': [],
            'paciente_id': [],
            'data': [],
            'terapeuta': [],
            'habilidades_trabalhadas': [],
            'descricao': [],
            'evolucao': [],
            'comportamentos': []
        })
        atendimentos_df.to_csv(atendimentos_file, index=False)
    
    # Carregar ou criar dados de avaliações
    if os.path.exists(avaliacoes_file):
        avaliacoes_df = pd.read_csv(avaliacoes_file)
    else:
        avaliacoes_df = pd.DataFrame({
            'id': [],
            'paciente_id': [],
            'data': [],
            'tipo_avaliacao': [],
            'terapeuta': [],
            'resultados': [],
            'recomendacoes': [],
            'proxima_avaliacao': []
        })
        avaliacoes_df.to_csv(avaliacoes_file, index=False)
    
    # Carregar ou criar dados de agendamentos
    if os.path.exists(agendamentos_file):
        agendamentos_df = pd.read_csv(agendamentos_file)
    else:
        agendamentos_df = pd.DataFrame({
            'id': [],
            'paciente_id': [],
            'data': [],
            'horario': [],
            'terapeuta': [],
            'status': [],
            'observacao': []
        })
        agendamentos_df.to_csv(agendamentos_file, index=False)
    
    return pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df

# Carregar dados
pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df = load_data()

# Configuração de autenticação
# Para um ambiente de produção, usar banco de dados seguro
# Este é apenas um exemplo usando arquivo local
if not os.path.exists('config.yaml'):
    credentials = {
        'usernames': {
            'admin': {
                'email': 'admin@neurobase.com',
                'name': 'Administrador',
                'password': stauth.Hasher(['admin']).generate()[0]
            },
            'terapeuta': {
                'email': 'terapeuta@neurobase.com',
                'name': 'Terapeuta',
                'password': stauth.Hasher(['terapeuta']).generate()[0]
            }
        }
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(credentials, file, default_flow_style=False)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['usernames'],
    'neurobase_app',
    'abcdef123456',
    cookie_expiry_days=30
)

# Função para autenticação
def autenticacao():
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status == False:
        st.error("Usuário/senha incorretos")
        return False, None
    
    elif authentication_status == None:
        st.warning("Por favor, insira seu usuário e senha")
        return False, None
    
    elif authentication_status:
        return True, username
    
    return False, None

# Função para mostrar dashboard
def mostrar_dashboard():
    st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(label="Total Pacientes", value=len(pacientes_df))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        atendimentos_hoje = len(atendimentos_df[atendimentos_df['data'] == datetime.date.today().strftime('%Y-%m-%d')])
        st.metric(label="Atendimentos Hoje", value=atendimentos_hoje)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        proximas_avaliacoes = len(avaliacoes_df[avaliacoes_df['proxima_avaliacao'] <= (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')])
        st.metric(label="Avaliações nos Próximos 30 dias", value=proximas_avaliacoes)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h2 class='sub-header'>Agenda do Dia</h2>", unsafe_allow_html=True)
    
    # Tabela de agendamentos do dia
    hoje = datetime.date.today().strftime('%Y-%m-%d')
    agendamentos_hoje = agendamentos_df[agendamentos_df['data'] == hoje]
    if len(agendamentos_hoje) > 0:
        agendamentos_hoje = agendamentos_hoje.merge(
            pacientes_df[['id', 'nome']], 
            left_on='paciente_id', 
            right_on='id', 
            suffixes=('', '_paciente')
        )
        st.dataframe(agendamentos_hoje[['horario', 'nome', 'terapeuta', 'status']])
    else:
        st.info("Não há agendamentos para hoje.")
    
    st.markdown("<h2 class='sub-header'>Alertas</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### Reavaliações Pendentes")
        st.markdown("Pacientes que precisam ser reavaliados nos próximos 30 dias:")
        
        # Exemplo de alertas de reavaliação
        alertas_reaval = """
        - Maria Silva (01/06/2025) - EDM
        - João Santos (15/06/2025) - TGMD-2
        - Ana Oliveira (20/06/2025) - Reavaliação
        """
        st.markdown(alertas_reaval)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### Alertas de Habilidades")
        st.markdown("Pacientes com déficit de trabalho em habilidades prioritárias:")
        
        # Exemplo de alertas de habilidades
        alertas_hab = """
        - Pedro Costa: Equilíbrio estático (apenas 2 sessões no último mês)
        - Luiza Mendes: Coordenação motora fina (0 sessões no último mês)
        - Gabriel Alves: Praxia (3 sessões no último mês, abaixo do recomendado)
        """
        st.markdown(alertas_hab)
        st.markdown("</div>", unsafe_allow_html=True)

# Função para mostrar pacientes
def mostrar_pacientes():
    st.markdown("<h1 class='main-header'>Pacientes</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Lista de Pacientes", "Cadastrar Novo Paciente", "Ficha do Paciente"])
    
    with tabs[0]:
        if len(pacientes_df) > 0:
            # Input para filtro
            filtro = st.text_input("Buscar paciente por nome:")
            
            if filtro:
                pacientes_filtrados = pacientes_df[pacientes_df['nome'].str.contains(filtro, case=False, na=False)]
            else:
                pacientes_filtrados = pacientes_df
            
            if len(pacientes_filtrados) > 0:
                # Exibir pacientes com opção de selecionar
                for i, paciente in pacientes_filtrados.iterrows():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if 'foto' in paciente and paciente['foto'] and str(paciente['foto']) != 'nan':
                            try:
                                foto_bytes = base64.b64decode(paciente['foto'])
                                foto_img = Image.open(io.BytesIO(foto_bytes))
                                st.image(foto_img, width=100)
                            except Exception as e:
                                st.image("https://via.placeholder.com/100x100.png?text=Foto", width=100)
                        else:
                            st.image("https://via.placeholder.com/100x100.png?text=Foto", width=100)
                    
                    with col2:
                        st.subheader(paciente['nome'])
                        if 'data_nascimento' in paciente and str(paciente['data_nascimento']) != 'nan':
                            data_nasc = datetime.datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                            idade = (datetime.datetime.now() - data_nasc).days // 365
                            st.write(f"Idade: {idade} anos")
                        if 'diagnostico' in paciente and str(paciente['diagnostico']) != 'nan':
                            st.write(f"Diagnóstico: {paciente['diagnostico']}")
                    
                    with col3:
                        if st.button("Ver Ficha", key=f"ficha_{paciente['id']}"):
                            st.session_state.paciente_selecionado = paciente['id']
                            st.experimental_rerun()
            else:
                st.info("Nenhum paciente encontrado com esse nome.")
        else:
            st.info("Não há pacientes cadastrados.")
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Cadastrar Novo Paciente</h2>", unsafe_allow_html=True)
        
        with st.form("cadastro_paciente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome completo")
                data_nascimento = st.date_input("Data de nascimento")
                responsavel = st.text_input("Nome do responsável")
                telefone = st.text_input("Telefone de contato")
                email = st.text_input("E-mail")
            
            with col2:
                diagnostico = st.text_input("Diagnóstico")
                nivel_suporte = st.selectbox("Nível de suporte (em caso de TEA)", 
                                           ["", "Nível 1", "Nível 2", "Nível 3"])
                data_entrada = st.date_input("Data de entrada na clínica")
                foto = st.file_uploader("Foto do paciente", type=["jpg", "jpeg", "png"])
            
            st.subheader("Preferências e informações importantes")
            col1, col2 = st.columns(2)
            
            with col1:
                preferencias = st.text_area("Coisas que gosta")
                coisas_acalmam = st.text_area("Coisas que o acalmam")
            
            with col2:
                nao_gosta = st.text_area("Coisas que não gosta")
                gatilhos = st.text_area("Coisas que o deixam nervoso")
            
            brinquedos_favoritos = st.text_area("Brinquedos favoritos (em ordem de preferência)")
            
            submitted = st.form_submit_button("Cadastrar Paciente")
            
            if submitted:
                # Processar a foto
                foto_base64 = None
                if foto is not None:
                    foto_bytes = foto.getvalue()
                    foto_base64 = base64.b64encode(foto_bytes).decode()
                
                # Criar novo ID
                novo_id = 1
                if len(pacientes_df) > 0:
                    novo_id = int(pacientes_df['id'].max()) + 1
                
                # Adicionar novo paciente
                novo_paciente = {
                    'id': novo_id,
                    'nome': nome,
                    'data_nascimento': data_nascimento.strftime('%Y-%m-%d'),
                    'responsavel': responsavel,
                    'telefone': telefone,
                    'email': email,
                    'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                    'diagnostico': diagnostico,
                    'nivel_suporte': nivel_suporte,
                    'foto': foto_base64,
                    'preferencias': preferencias,
                    'coisas_acalmam': coisas_acalmam,
                    'nao_gosta': nao_gosta,
                    'gatilhos': gatilhos,
                    'brinquedos_favoritos': brinquedos_favoritos
                }
                
                pacientes_df.loc[len(pacientes_df)] = novo_paciente
                pacientes_df.to_csv("dados/pacientes.csv", index=False)
                
                st.success(f"Paciente {nome} cadastrado com sucesso!")
                time.sleep(1)
                st.experimental_rerun()
    
    with tabs[2]:
        if 'paciente_selecionado' in st.session_state:
            paciente_id = st.session_state.paciente_selecionado
            paciente = pacientes_df[pacientes_df['id'] == paciente_id].iloc[0]
            
            st.markdown(f"<h2 class='sub-header'>Ficha do Paciente: {paciente['nome']}</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if 'foto' in paciente and paciente['foto'] and str(paciente['foto']) != 'nan':
                    try:
                        foto_bytes = base64.b64decode(paciente['foto'])
                        foto_img = Image.open(io.BytesIO(foto_bytes))
                        st.image(foto_img, width=200)
                    except Exception as e:
                        st.image("https://via.placeholder.com/200x200.png?text=Foto", width=200)
                else:
                    st.image("https://via.placeholder.com/200x200.png?text=Foto", width=200)
            
            with col2:
                st.markdown("### Informações Pessoais")
                if 'data_nascimento' in paciente and str(paciente['data_nascimento']) != 'nan':
                    data_nasc = datetime.datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                    idade = (datetime.datetime.now() - data_nasc).days // 365
                    st.write(f"**Idade:** {idade} anos")
                st.write(f"**Data de Nascimento:** {paciente['data_nascimento']}")
                st.write(f"**Responsável:** {paciente['responsavel']}")
                st.write(f"**Contato:** {paciente['telefone']}")
                st.write(f"**E-mail:** {paciente['email']}")
                st.write(f"**Data de Entrada:** {paciente['data_entrada']}")
                st.write(f"**Diagnóstico:** {paciente['diagnostico']}")
                if 'nivel_suporte' in paciente and paciente['nivel_suporte']:
                    st.write(f"**Nível de Suporte:** {paciente['nivel_suporte']}")
            
            st.markdown("---")
            st.markdown("### Preferências e Comportamento")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 😊 Coisas que gosta")
                if 'preferencias' in paciente:
                    st.write(paciente['preferencias'])
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 😌 Coisas que o acalmam")
                if 'coisas_acalmam' in paciente:
                    st.write(paciente['coisas_acalmam'])
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 😕 Coisas que não gosta")
                if 'nao_gosta' in paciente:
                    st.write(paciente['nao_gosta'])
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 😠 Gatilhos")
                if 'gatilhos' in paciente:
                    st.write(paciente['gatilhos'])
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### 🧸 Brinquedos favoritos (em ordem)")
            if 'brinquedos_favoritos' in paciente:
                st.write(paciente['brinquedos_favoritos'])
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Abas para histórico de atendimentos e avaliações
            paciente_tabs = st.tabs(["Atendimentos", "Avaliações", "Próximos Agendamentos"])
            
            with paciente_tabs[0]:
                atendimentos_paciente = atendimentos_df[atendimentos_df['paciente_id'] == paciente_id]
                if len(atendimentos_paciente) > 0:
                    atendimentos_paciente = atendimentos_paciente.sort_values('data', ascending=False)
                    
                    for i, atendimento in atendimentos_paciente.iterrows():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"#### {atendimento['data']} - Terapeuta: {atendimento['terapeuta']}")
                        
                        st.markdown("**Habilidades trabalhadas:**")
                        if 'habilidades_trabalhadas' in atendimento and isinstance(atendimento['habilidades_trabalhadas'], str):
                            habilidades_list = atendimento['habilidades_trabalhadas'].split(',')
                            for hab in habilidades_list:
                                st.markdown(f"<span class='skill-tag'>{hab.strip()}</span>", unsafe_allow_html=True)
                        
                        st.markdown("**Evolução:**")
                        if 'evolucao' in atendimento:
                            st.write(atendimento['evolucao'])
                        
                        if 'comportamentos' in atendimento and isinstance(atendimento['comportamentos'], str) and atendimento['comportamentos']:
                            st.markdown("**Comportamentos:**")
                            st.write(atendimento['comportamentos'])
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Não há registros de atendimentos para este paciente.")
            
            with paciente_tabs[1]:
                avaliacoes_paciente = avaliacoes_df[avaliacoes_df['paciente_id'] == paciente_id]
                if len(avaliacoes_paciente) > 0:
                    avaliacoes_paciente = avaliacoes_paciente.sort_values('data', ascending=False)
                    
                    for i, avaliacao in avaliacoes_paciente.iterrows():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"#### {avaliacao['data']} - {avaliacao['tipo_avaliacao']}")
                        st.markdown(f"Terapeuta: {avaliacao['terapeuta']}")
                        
                        st.markdown("**Resultados:**")
                        if 'resultados' in avaliacao:
                            st.write(avaliacao['resultados'])
                        
                        st.markdown("**Recomendações:**")
                        if 'recomendacoes' in avaliacao:
                            st.write(avaliacao['recomendacoes'])
                        
                        if 'proxima_avaliacao' in avaliacao:
                            st.markdown(f"**Próxima avaliação programada:** {avaliacao['proxima_avaliacao']}")
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Não há registros de avaliações para este paciente.")
            
            with paciente_tabs[2]:
                hoje = datetime.date.today().strftime('%Y-%m-%d')
                agendamentos_futuros = agendamentos_df[(agendamentos_df['paciente_id'] == paciente_id) & 
                                                    (agendamentos_df['data'] >= hoje)]
                
                if len(agendamentos_futuros) > 0:
                    agendamentos_futuros = agendamentos_futuros.sort_values('data')
                    st.dataframe(agendamentos_futuros[['data', 'horario', 'terapeuta', 'status', 'observacao']])
                else:
                    st.info("Não há agendamentos futuros para este paciente.")

# Função para mostrar atendimentos
def mostrar_atendimentos():
    st.markdown("<h1 class='main-header'>Registro de Atendimentos</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Novo Atendimento", "Histórico de Atendimentos"])
    
    with tabs[0]:
        st.markdown("<h2 class='sub-header'>Registrar Novo Atendimento</h2>", unsafe_allow_html=True)
        
        # Formulário de registro de atendimento
        with st.form("form_atendimento"):
            # Seleção de paciente
            paciente_id = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else ""
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_atendimento = st.date_input("Data do Atendimento")
                terapeuta = st.text_input("Terapeuta Responsável")
            
            # Sistema de seleção de habilidades trabalhadas
            st.markdown("### Habilidades trabalhadas")
            
            # Lista para armazenar habilidades selecionadas
            if 'habilidades_selecionadas' not in st.session_state:
                st.session_state.habilidades_selecionadas = []
            
            # Interface para seleção de habilidades por categoria
            categorias = list(HABILIDADES_PSICOMOTORAS.keys())
            categoria_selecionada = st.selectbox("Categoria de Habilidade", categorias)
            
            if categoria_selecionada:
                habilidades_categoria = HABILIDADES_PSICOMOTORAS[categoria_selecionada]
                
                st.markdown("Selecione as habilidades trabalhadas nesta sessão:")
                cols = st.columns(3)
                for i, habilidade in enumerate(habilidades_categoria):
                    col_idx = i % 3
                    with cols[col_idx]:
                        key = f"{categoria_selecionada}_{habilidade}"
                        if st.checkbox(habilidade, key=key):
                            if habilidade not in st.session_state.habilidades_selecionadas:
                                st.session_state.habilidades_selecionadas.append(habilidade)
                        elif habilidade in st.session_state.habilidades_selecionadas:
                            st.session_state.habilidades_selecionadas.remove(habilidade)
            
            st.markdown("### Habilidades selecionadas:")
            habilidades_html = ""
            for hab in st.session_state.habilidades_selecionadas:
                habilidades_html += f"<span class='skill-tag skill-tag-selected'>{hab}</span>"
            
            st.markdown(habilidades_html, unsafe_allow_html=True)
            
            # Limpar seleção
            if st.button("Limpar todas as habilidades"):
                st.session_state.habilidades_selecionadas = []
                st.experimental_rerun()
            
            # Descrição e evolução do atendimento
            st.markdown("### Detalhes do Atendimento")
            descricao = st.text_area("Descrição das atividades realizadas", height=100)
            evolucao = st.text_area("Evolução observada", height=150)
            comportamentos = st.text_area("Comportamentos observados", height=100)
            
            submitted = st.form_submit_button("Registrar Atendimento")
            
            if submitted:
                # Verificar dados obrigatórios
                if not paciente_id or not data_atendimento or not terapeuta:
                    st.error("Por favor, preencha os campos obrigatórios: paciente, data e terapeuta.")
                else:
                    # Criar novo ID
                    novo_id = 1
                    if len(atendimentos_df) > 0:
                        novo_id = int(atendimentos_df['id'].max()) + 1
                    
                    # Adicionar novo atendimento
                    novo_atendimento = {
                        'id': novo_id,
                        'paciente_id': paciente_id,
                        'data': data_atendimento.strftime('%Y-%m-%d'),
                        'terapeuta': terapeuta,
                        'habilidades_trabalhadas': ', '.join(st.session_state.habilidades_selecionadas),
                        'descricao': descricao,
                        'evolucao': evolucao,
                        'comportamentos': comportamentos
                    }
                    
                    atendimentos_df.loc[len(atendimentos_df)] = novo_atendimento
                    atendimentos_df.to_csv("dados/atendimentos.csv", index=False)
                    
                    # Limpar habilidades selecionadas
                    st.session_state.habilidades_selecionadas = []
                    
                    st.success(f"Atendimento registrado com sucesso!")
                    time.sleep(1)
                    st.experimental_rerun()
    
    with tabs[1]:
        st.markdown("<h2 class='sub-header'>Histórico de Atendimentos</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            paciente_filtro = st.selectbox(
                "Filtrar por Paciente",
                options=[0] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == 0 else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else ""
            )
        
        with col2:
            periodo = st.date_input(
                "Período (Início, Fim)",
                [datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()],
                max_value=datetime.date.today()
            )
        
        # Aplicar filtros
        if paciente_filtro != 0:
            atendimentos_filtrados = atendimentos_df[atendimentos_df['paciente_id'] == paciente_filtro]
        else:
            atendimentos_filtrados = atendimentos_df.copy()
        
        # Filtrar por período
        if len(periodo) == 2:
            inicio, fim = periodo
            atendimentos_filtrados = atendimentos_filtrados[
                (atendimentos_filtrados['data'] >= inicio.strftime('%Y-%m-%d')) & 
                (atendimentos_filtrados['data'] <= fim.strftime('%Y-%m-%d'))
            ]
        
        # Exibir resultados
        if len(atendimentos_filtrados) > 0:
            atendimentos_filtrados = atendimentos_filtrados.sort_values('data', ascending=False)
            
            # Juntar com nomes dos pacientes
            atendimentos_completos = atendimentos_filtrados.merge(
                pacientes_df[['id', 'nome']], 
                left_on='paciente_id', 
                right_on='id', 
                suffixes=('', '_paciente')
            )
            
            for i, atendimento in atendimentos_completos.iterrows():
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"#### {atendimento['data']} - {atendimento['nome']}")
                st.markdown(f"Terapeuta: {atendimento['terapeuta']}")
                
                st.markdown("**Habilidades trabalhadas:**")
                if 'habilidades_trabalhadas' in atendimento and isinstance(atendimento['habilidades_trabalhadas'], str):
                    habilidades_list = atendimento['habilidades_trabalhadas'].split(',')
                    habilidades_html = ""
                    for hab in habilidades_list:
                        habilidades_html += f"<span class='skill-tag'>{hab.strip()}</span>"
                    st.markdown(habilidades_html, unsafe_allow_html=True)
                
                with st.expander("Ver detalhes do atendimento"):
                    st.markdown("**Descrição das atividades:**")
                    if 'descricao' in atendimento:
                        st.write(atendimento['descricao'])
                    
                    st.markdown("**Evolução observada:**")
                    if 'evolucao' in atendimento:
                        st.write(atendimento['evolucao'])
                    
                    if 'comportamentos' in atendimento and isinstance(atendimento['comportamentos'], str) and atendimento['comportamentos']:
                        st.markdown("**Comportamentos observados:**")
                        st.write(atendimento['comportamentos'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum atendimento encontrado com os filtros selecionados.")