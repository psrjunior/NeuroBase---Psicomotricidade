        st.markdown("<h2 class='section-header'>Histórico de Atendimentos</h2>", unsafe_allow_html=True)
        
        # Filtros para busca
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por paciente
            patients = get_patients()
            patient_options = [(p['id'], p['name']) for p in patients]
            patient_options.insert(0, ("all", "Todos os pacientes"))
            
            filter_patient = st.selectbox(
                "Filtrar por paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="hist_filter_patient"
            )
        
        with col2:
            filter_therapist = st.text_input("Filtrar por terapeuta")
        
        with col3:
            filter_period = st.date_input(
                "Período",
                value=[datetime.now() - timedelta(days=30), datetime.now()],
                key="hist_filter_period"
            )
        
        # Obter todas as sessões
        conn = sqlite3.connect('data/neurobase.db')
        cursor = conn.cursor()
        
        query = """
        SELECT s.*, p.name as patient_name 
        FROM sessions s
        JOIN patients p ON s.patient_id = p.id
        WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if filter_patient != "all":
            query += " AND s.patient_id = ?"
            params.append(filter_patient)
        
        if filter_therapist:
            query += " AND s.therapist LIKE ?"
            params.append(f"%{filter_therapist}%")
        
        if len(filter_period) == 2:
            start_date, end_date = filter_period
            query += " AND s.date BETWEEN ? AND ?"
            params.extend([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
        
        query += " ORDER BY s.date DESC"
        
        cursor.execute(query, params)
        
        # Converter resultado para lista de dicionários
        columns = [column[0] for column in cursor.description]
        sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        # Exibir resultados
        if sessions:
            st.markdown(f"Exibindo {len(sessions)} atendimentos")
            
            for session in sessions:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**Data:** {session['date']}")
                    st.markdown(f"**Paciente:** {session['patient_name']}")
                    st.markdown(f"**Terapeuta:** {session['therapist']}")
                
                with col2:
                    # Habilidades trabalhadas
                    st.markdown("**Habilidades trabalhadas:**")
                    if session.get('skills_worked'):
                        skills_html = ""
                        for skill in session['skills_worked'].split(','):
                            skill = skill.strip()
                            if skill:
                                skills_html += f"<span class='skill-tag'>{skill}</span>"
                        
                        st.markdown(skills_html, unsafe_allow_html=True)
                
                # Detalhes da sessão
                with st.expander("Ver detalhes"):
                    if session.get('description'):
                        st.markdown("**Descrição das atividades:**")
                        st.markdown(session['description'])
                    
                    if session.get('evolution'):
                        st.markdown("**Evolução observada:**")
                        st.markdown(session['evolution'])
                    
                    if session.get('behaviors'):
                        st.markdown("**Comportamentos observados:**")
                        st.markdown(session['behaviors'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum atendimento encontrado com os filtros selecionados.")
    
    with tab3:
        st.markdown("<h2 class='section-header'>Análise de Habilidades</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por paciente
            patients = get_patients()
            patient_options = [(p['id'], p['name']) for p in patients]
            patient_options.insert(0, ("all", "Todos os pacientes"))
            
            analysis_patient = st.selectbox(
                "Selecione o paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="analysis_patient"
            )
        
        with col2:
            analysis_period = st.selectbox(
                "Período de análise",
                options=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"]
            )
        
        # Botão para gerar análise
        if st.button("Analisar Habilidades"):
            # Determinar período de análise
            days = 30  # Padrão: último mês
            
            if analysis_period == "Últimos 3 meses":
                days = 90
            elif analysis_period == "Últimos 6 meses":
                days = 180
            elif analysis_period == "Último ano":
                days = 365
            
            # Obter dados para análise
            if analysis_patient == "all":
                # Análise para todos os pacientes
                skill_frequency = analyze_skills_frequency(patient_id=None, days=days)
                
                st.markdown("### Frequência de Habilidades Trabalhadas")
                st.markdown(f"Período: últimos {days} dias")
                
                if skill_frequency:
                    # Ordenar habilidades por frequência
                    sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
                    
                    # Criar DataFrame para visualização
                    df = pd.DataFrame(sorted_skills, columns=['Habilidade', 'Frequência'])
                    
                    # Limitar para as 15 habilidades mais trabalhadas
                    if len(df) > 15:
                        df = df.head(15)
                    
                    # Criar gráfico
                    fig = px.bar(
                        df,
                        x='Frequência',
                        y='Habilidade',
                        orientation='h',
                        title='Habilidades Mais Trabalhadas',
                        color='Frequência',
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(
                        xaxis_title='Número de Sessões',
                        yaxis_title='',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Agrupar por categoria
                    category_counts = {}
                    
                    for skill, count in skill_frequency.items():
                        # Encontrar categoria da habilidade
                        found = False
                        for category, skills in PSICOMOTOR_SKILLS.items():
                            if skill in skills:
                                if category in category_counts:
                                    category_counts[category] += count
                                else:
                                    category_counts[category] = count
                                found = True
                                break
                        
                        # Se não encontrou em nenhuma categoria
                        if not found:
                            if "Outras" in category_counts:
                                category_counts["Outras"] += count
                            else:
                                category_counts["Outras"] = count
                    
                    # Criar DataFrame para categorias
                    df_categories = pd.DataFrame(
                        sorted(category_counts.items(), key=lambda x: x[1], reverse=True),
                        columns=['Categoria', 'Frequência']
                    )
                    
                    # Criar gráfico de pizza para categorias
                    fig_pie = px.pie(
                        df_categories,
                        values='Frequência',
                        names='Categoria',
                        title='Distribuição por Categoria de Habilidade'
                    )
                    
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Não há dados suficientes para análise no período selecionado.")
            else:
                # Análise para um paciente específico
                # Obter nome do paciente
                patient_name = next((p[1] for p in patient_options if p[0] == analysis_patient), "")
                
                # Obter frequência de habilidades
                skill_frequency = analyze_skills_frequency(patient_id=analysis_patient, days=days)
                
                st.markdown(f"### Análise para: {patient_name}")
                st.markdown(f"Período: últimos {days} dias")
                
                if skill_frequency:
                    # Criar DataFrame para frequência
                    df_skills = pd.DataFrame(
                        sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True),
                        columns=['Habilidade', 'Frequência']
                    )
                    
                    # Criar gráfico de barras
                    fig = px.bar(
                        df_skills,
                        x='Frequência',
                        y='Habilidade',
                        orientation='h',
                        title='Habilidades Trabalhadas',
                        color='Frequência',
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(
                        xaxis_title='Número de Sessões',
                        yaxis_title='',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparar com necessidades do paciente
                    comparison = compare_skills_with_needs(analysis_patient, days)
                    
                    if comparison:
                        st.markdown("### Comparação com Necessidades Avaliadas")
                        
                        # Criar DataFrame para comparação
                        comparison_data = []
                        
                        for skill, data in comparison.items():
                            comparison_data.append({
                                'Habilidade': skill,
                                'Prioridade': data['priority'],
                                'Frequência': data['frequency'],
                                'Adequação (%)': round(data['adequacy'], 1)
                            })
                        
                        df_comparison = pd.DataFrame(comparison_data)
                        
                        # Ordenar por adequação (crescente)
                        df_comparison = df_comparison.sort_values('Adequação (%)')
                        
                        # Criar gráfico de barras para comparação
                        fig_comp = go.Figure()
                        
                        fig_comp.add_trace(go.Bar(
                            x=df_comparison['Habilidade'],
                            y=df_comparison['Prioridade'],
                            name='Prioridade',
                            marker_color='#7B1FA2'
                        ))
                        
                        fig_comp.add_trace(go.Bar(
                            x=df_comparison['Habilidade'],
                            y=df_comparison['Frequência'],
                            name='Frequência',
                            marker_color='#4CAF50'
                        ))
                        
                        fig_comp.update_layout(
                            title='Prioridades vs. Frequência',
                            xaxis_tickangle=-45,
                            barmode='group',
                            height=400
                        )
                        
                        st.plotly_chart(fig_comp, use_container_width=True)
                        
                        # Identificar áreas com baixa adequação
                        low_adequacy = df_comparison[df_comparison['Adequação (%)'] < 50]
                        
                        if not low_adequacy.empty:
                            st.markdown("### Recomendações")
                            st.markdown("As seguintes habilidades precisam de maior atenção:")
                            
                            for _, row in low_adequacy.iterrows():
                                st.markdown(f"""
                                <div class='warning-alert'>
                                    <strong>{row['Habilidade']}</strong> - Adequação: {row['Adequação (%)']}%
                                    <br>
                                    Esta habilidade tem prioridade {row['Prioridade']} mas foi trabalhada apenas {row['Frequência']} vezes.
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("As habilidades estão sendo trabalhadas adequadamente conforme as prioridades identificadas.")
                        
                        # Mostrar tabela de dados
                        st.markdown("### Dados Detalhados")
                        st.dataframe(df_comparison)
                    else:
                        st.warning("Não foi possível comparar com necessidades do paciente. Verifique se há avaliações registradas.")
                else:
                    st.info("Não há dados de atendimentos para este paciente no período selecionado.")

def evaluations_page():
    """Exibe a página de avaliações"""
    st.markdown("<h1 class='main-header'>Avaliações</h1>", unsafe_allow_html=True)
    
    # Tabs para diferentes seções
    tab1, tab2, tab3 = st.tabs(["Nova Avaliação", "Lista de Avaliações", "Acompanhamento de Evolução"])
    
    with tab1:
        st.markdown("<h2 class='section-header'>Registrar Nova Avaliação</h2>", unsafe_allow_html=True)
        
        # Verificar se há um paciente pré-selecionado
        patient_preselected = False
        if 'new_evaluation' in st.session_state:
            patient_id = st.session_state.new_evaluation
            patient_preselected = True
            # Limpar estado após uso
            del st.session_state.new_evaluation
        
        # Obter lista de pacientes
        patients = get_patients()
        patient_options = [(p['id'], p['name']) for p in patients]
        
        with st.form("evaluation_form"):
            # Seleção de paciente
            if patient_preselected:
                # Encontrar índice do paciente na lista
                selected_index = next((i for i, p in enumerate(patient_options) if p[0] == patient_id), 0)
                patient_id = st.selectbox(
                    "Paciente*",
                    options=[p[0] for p in patient_options],
                    format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                    index=selected_index
                )
            else:
                patient_id = st.selectbox(
                    "Paciente*",
                    options=[p[0] for p in patient_options],
                    format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), "")
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                evaluation_date = st.date_input("Data da Avaliação*", value=datetime.now())
                evaluation_type = st.selectbox("Tipo de Avaliação*", options=EVALUATION_TYPES)
            
            with col2:
                therapist = st.text_input("Avaliador*", value=st.session_state.user['name'] if 'user' in st.session_state else "")
                next_evaluation = st.date_input("Data para próxima avaliação", value=datetime.now() + timedelta(days=365))
            
            # Áreas avaliadas
            st.markdown("### Áreas Avaliadas")
            
            # Dicionário para armazenar áreas e níveis
            evaluated_areas = {}
            scores = {}
            
            # Interface para avaliação de habilidades por categoria
            for category, skills in PSICOMOTOR_SKILLS.items():
                with st.expander(f"Avaliar: {category}"):
                    for skill in skills:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{skill}**")
                        
                        with col2:
                            level = st.selectbox(
                                "Nível",
                                options=[""] + DEVELOPMENT_LEVELS,
                                key=f"level_{skill.replace(' ', '_')}"
                            )
                            
                            if level:
                                evaluated_areas[skill] = level
                                # Mapear nível para pontuação (1-7)
                                scores[skill] = DEVELOPMENT_LEVELS.index(level) + 1
            
            # Resultados e recomendações
            st.markdown("### Resultados e Recomendações")
            results = st.text_area("Resultados da avaliação", height=150)
            recommendations = st.text_area("Recomendações", height=150)
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Registrar Avaliação")
            
            if submitted:
                # Verificar campos obrigatórios
                if not patient_id or not evaluation_date or not evaluation_type or not therapist:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    # Preparar dados para inserção
                    evaluation_data = {
                        'patient_id': patient_id,
                        'date': evaluation_date.strftime('%Y-%m-%d'),
                        'evaluation_type': evaluation_type,
                        'therapist': therapist,
                        'results': results,
                        'recommendations': recommendations,
                        'next_evaluation': next_evaluation.strftime('%Y-%m-%d'),
                        'evaluated_areas': json.dumps(evaluated_areas),
                        'scores': json.dumps(scores)
                    }
                    
                    # Inserir no banco de dados
                    try:
                        evaluation_id = add_evaluation(evaluation_data)
                        
                        # Registrar atividade
                        if 'user' in st.session_state:
                            patient_name = next((p[1] for p in patient_options if p[0] == patient_id), "")
                            log_activity(
                                st.session_state.user['id'],
                                'add',
                                'evaluations',
                                evaluation_id,
                                f"Adicionou avaliação para: {patient_name}"
                            )
                        
                        st.success("Avaliação registrada com sucesso!")
                        time.sleep(1)
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar avaliação: {str(e)}")
    
    with tab2:
        st.markdown("<h2 class='section-header'>Lista de Avaliações</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por paciente
            patients = get_patients()
            patient_options = [(p['id'], p['name']) for p in patients]
            patient_options.insert(0, ("all", "Todos os pacientes"))
            
            filter_patient = st.selectbox(
                "Filtrar por paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="eval_filter_patient"
            )
        
        with col2:
            filter_type = st.selectbox(
                "Filtrar por tipo",
                options=["Todos"] + EVALUATION_TYPES
            )
        
        with col3:
            filter_period = st.date_input(
                "Período",
                value=[datetime.now() - timedelta(days=365), datetime.now()],
                key="eval_filter_period"
            )
        
        # Obter todas as avaliações
        conn = sqlite3.connect('data/neurobase.db')
        cursor = conn.cursor()
        
        query = """
        SELECT e.*, p.name as patient_name 
        FROM evaluations e
        JOIN patients p ON e.patient_id = p.id
        WHERE 1=1
        """
        params = []
        
        # Aplicar filtros
        if filter_patient != "all":
            query += " AND e.patient_id = ?"
            params.append(filter_patient)
        
        if filter_type != "Todos":
            query += " AND e.evaluation_type = ?"
            params.append(filter_type)
        
        if len(filter_period) == 2:
            start_date, end_date = filter_period
            query += " AND e.date BETWEEN ? AND ?"
            params.extend([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
        
        query += " ORDER BY e.date DESC"
        
        cursor.execute(query, params)
        
        # Converter resultado para lista de dicionários
        columns = [column[0] for column in cursor.description]
        evaluations = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        # Processar JSON para dicionários
        for evaluation in evaluations:
            if 'evaluated_areas' in evaluation and evaluation['evaluated_areas']:
                try:
                    evaluation['evaluated_areas'] = json.loads(evaluation['evaluated_areas'])
                except:
                    evaluation['evaluated_areas'] = {}
            
            if 'scores' in evaluation and evaluation['scores']:
                try:
                    evaluation['scores'] = json.loads(evaluation['scores'])
                except:
                    evaluation['scores'] = {}
        
        # Exibir resultados
        if evaluations:
            st.markdown(f"Exibindo {len(evaluations)} avaliações")
            
            for evaluation in evaluations:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**Data:** {evaluation['date']}")
                    st.markdown(f"**Tipo:** {evaluation['evaluation_type']}")
                    
                    if evaluation.get('next_evaluation'):
                        st.markdown(f"**Próxima avaliação:** {evaluation['next_evaluation']}")
                
                with col2:
                    st.markdown(f"**Paciente:** {evaluation['patient_name']}")
                    st.markdown(f"**Avaliador:** {evaluation['therapist']}")
                    
                    # Mostrar áreas avaliadas (até 5)
                    if evaluation.get('evaluated_areas') and isinstance(evaluation['evaluated_areas'], dict):
                        st.markdown("**Áreas avaliadas:**")
                        
                        areas_html = ""
                        count = 0
                        
                        for area, level in evaluation['evaluated_areas'].items():
                            if count < 5:
                                # Mapear níveis para cores
                                level_colors = {
                                    "Muito inferior": "#F44336",
                                    "Inferior": "#FF9800",
                                    "Normal baixo": "#FFC107",
                                    "Normal médio": "#4CAF50",
                                    "Normal alto": "#2196F3",
                                    "Superior": "#673AB7",
                                    "Muito superior": "#3F51B5"
                                }
                                
                                color = level_colors.get(level, "#9E9E9E")
                                areas_html += f"<span style='margin-right:8px;'><strong>{area}:</strong> <span style='color:{color};'>{level}</span></span>"
                                count += 1
                        
                        if len(evaluation['evaluated_areas']) > 5:
                            areas_html += f"<span>... e mais {len(evaluation['evaluated_areas']) - 5} áreas</span>"
                        
                        st.markdown(areas_html, unsafe_allow_html=True)
                
                # Detalhes da avaliação
                with st.expander("Ver resultados completos"):
                    if evaluation.get('results'):
                        st.markdown("**Resultados:**")
                        st.markdown(evaluation['results'])
                    
                    if evaluation.get('recommendations'):
                        st.markdown("**Recomendações:**")
                        st.markdown(evaluation['recommendations'])
                    
                    # Mostrar todas as áreas avaliadas
                    if evaluation.get('evaluated_areas') and isinstance(evaluation['evaluated_areas'], dict):
                        st.markdown("**Todas as áreas avaliadas:**")
                        
                        # Criar DataFrame para visualização
                        areas_df = pd.DataFrame(
                            {
                                "Área": list(evaluation['evaluated_areas'].keys()),
                                "Nível": list(evaluation['evaluated_areas'].values())
                            }
                        )
                        
                        st.dataframe(areas_df)
                        
                        # Criar gráfico se houver scores
                        if evaluation.get('scores') and isinstance(evaluation['scores'], dict):
                            scores_df = pd.DataFrame(
                                {
                                    "Área": list(evaluation['scores'].keys()),
                                    "Pontuação": list(evaluation['scores'].values())
                                }
                            )
                            
                            fig = px.bar(
                                scores_df,
                                x="Pontuação",
                                y="Área",
                                orientation='h',
                                title="Pontuações por Área",
                                color="Pontuação",
                                color_continuous_scale="Viridis"
                            )
                            
                            fig.update_layout(
                                xaxis_title="Pontuação",
                                yaxis_title="",
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhuma avaliação encontrada com os filtros selecionados.")
    
    with tab3:
        st.markdown("<h2 class='section-header'>Acompanhamento de Evolução</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente
        patients = get_patients()
        patient_options = [(p['id'], p['name']) for p in patients]
        
        evolution_patient = st.selectbox(
            "Selecione o paciente",
            options=[p[0] for p in patient_options],
            format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), "")
        )
        
        if st.button("Analisar Evolução"):
            # Obter nome do paciente
            patient_name = next((p[1] for p in patient_options if p[0] == evolution_patient), "")
            
            # Obter avaliações do paciente
            evaluations = get_patient_evaluations(evolution_patient)
            
            if len(evaluations) > 1:  # Precisa de pelo menos 2 avaliações para comparar
                st.markdown(f"### Evolução de {patient_name}")
                
                # Organizar avaliações por data
                evaluations.sort(key=lambda x: x['date'])
                
                # Extrair dados de evolução
                evolution_data = {}
                
                for evaluation in evaluations:
                    if 'scores' in evaluation and evaluation['scores'] and isinstance(evaluation['scores'], dict):
                        for area, score in evaluation['scores'].items():
                            if area not in evolution_data:
                                evolution_data[area] = []
                            
                            evolution_data[area].append({
                                'date': evaluation['date'],
                                'score': score
                            })
                
                # Criar gráficos de evolução
                if evolution_data:
                    # Selecionar áreas para visualização
                    areas_to_show = st.multiselect(
                        "Selecione as áreas para visualizar",
                        options=list(evolution_data.keys()),
                        default=list(evolution_data.keys())[:5]  # Default: primeiras 5 áreas
                    )
                    
                    if areas_to_show:
                        # Criar gráfico de linhas para cada área selecionada
                        fig = go.Figure()
                        
                        for area in areas_to_show:
                            if area in evolution_data:
                                dates = [item['date'] for item in evolution_data[area]]
                                scores = [item['score'] for item in evolution_data[area]]
                                
                                fig.add_trace(go.Scatter(
                                    x=dates,
                                    y=scores,
                                    mode='lines+markers',
                                    name=area
                                ))
                        
                        fig.update_layout(
                            title='Evolução por Área',
                            xaxis_title='Data',
                            yaxis_title='Pontuação',
                            height=500,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calcular percentual de evolução
                        st.markdown("### Percentual de Evolução")
                        
                        evolution_percentages = {}
                        
                        for area in evolution_data:
                            if len(evolution_data[area]) >= 2:
                                first = evolution_data[area][0]['score']
                                last = evolution_data[area][-1]['score']
                                
                                if first > 0:  # Evitar divisão por zero
                                    percentage = ((last - first) / first) * 100
                                    evolution_percentages[area] = percentage
                        
                        if evolution_percentages:
                            # Criar DataFrame para visualização
                            percentages_df = pd.DataFrame(
                                {
                                    "Área": list(evolution_percentages.keys()),
                                    "Evolução (%)": [round(p, 1) for p in evolution_percentages.values()]
                                }
                            )
                            
                            # Ordenar por percentual de evolução
                            percentages_df = percentages_df.sort_values("Evolução (%)", ascending=False)
                            
                            # Criar gráfico de barras
                            fig_perc = px.bar(
                                percentages_df,
                                x="Área",
                                y="Evolução (%)",
                                title="Percentual de Evolução por Área",
                                color="Evolução (%)",
                                color_continuous_scale="RdYlGn"  # Red-Yellow-Green
                            )
                            
                            fig_perc.update_layout(
                                xaxis_title="",
                                yaxis_title="Evolução (%)",
                                height=400,
                                xaxis={'categoryorder':'total descending'}
                            )
                            
                            st.plotly_chart(fig_perc, use_container_width=True)
                            
                            # Mostrar tabela com dados
                            st.dataframe(percentages_df)
                            
                            # Identificar áreas com pouca ou nenhuma evolução
                            low_evolution = percentages_df[percentages_df["Evolução (%)"] <= 0]
                            
                            if not low_evolution.empty:
                                st.markdown("### Áreas que precisam de atenção")
                                
                                for _, row in low_evolution.iterrows():
                                    st.markdown(f"""
                                    <div class='warning-alert'>
                                        <strong>{row['Área']}</strong> - Evolução: {row['Evolução (%)']}%
                                        <br>
                                        Esta área não apresentou evolução ou teve declínio.
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.info("Não há dados suficientes para calcular percentuais de evolução.")
                    else:
                        st.info("Selecione pelo menos uma área para visualizar.")
                else:
                    st.warning("Não foi possível extrair dados de evolução das avaliações.")
            else:
                st.info("São necessárias pelo menos duas avaliações para analisar a evolução.")

def appointments_page():
    """Exibe a página de agendamentos"""
    st.markdown("<h1 class='main-header'>Agendamentos</h1>", unsafe_allow_html=True)
    
    # Tabs para diferentes seções
    tab1, tab2, tab3, tab4 = st.tabs(["Novo Agendamento", "Calendário", "Gestão de Agendamentos", "Agrupamentos Sugeridos"])
    
    with tab1:
        st.markdown("<h2 class='section-header'>Agendar Nova Sessão</h2>", unsafe_allow_html=True)
        
        # Verificar se há um paciente pré-selecionado
        patient_preselected = False
        if 'new_appointment' in st.session_state:
            patient_id = st.session_state.new_appointment
            patient_preselected = True
            # Limpar estado após uso
            del st.session_state.new_appointment
        
        # Obter lista de pacientes
        patients = get_patients()
        patient_options = [(p['id'], p['name']) for p in patients]
        
        with st.form("appointment_form"):
            # Seleção de paciente
            if patient_preselected:
                # Encontrar índice do paciente na lista
                selected_index = next((i for i, p in enumerate(patient_options) if p[0] == patient_id), 0)
                patient_id = st.selectbox(
                    "Paciente*",
                    options=[p[0] for p in patient_options],
                    format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                    index=selected_index
                )
            else:
                patient_id = st.selectbox(
                    "Paciente*",
                    options=[p[0] for p in patient_options],
                    format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), "")
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                appointment_date = st.date_input("Data da Sessão*", value=datetime.now())
                appointment_time = st.time_input("Horário*", value=datetime.now().time().replace(second=0, microsecond=0))
            
            with col2:
                therapist = st.text_input("Terapeuta*", value=st.session_state.user['name'] if 'user' in st.session_state else "")
                status = st.selectbox("Status*", options=SCHEDULE_STATUS)
            
            observation = st.text_area("Observações", height=100)
            
            # Opções adicionais
            col1, col2 = st.columns(2)
            
            with col1:
                google_cal = st.checkbox("Gerar evento no Google Calendar")
            
            with col2:
                notify_whatsapp = st.checkbox("Notificar via WhatsApp")
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Agendar Sessão")
            
            if submitted:
                # Verificar campos obrigatórios
                if not patient_id or not appointment_date or not appointment_time or not therapist or not status:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    # Preparar dados para inserção
                    appointment_data = {
                        'patient_id': patient_id,
                        'date': appointment_date.strftime('%Y-%m-%d'),
                        'time': appointment_time.strftime('%H:%M'),
                        'therapist': therapist,
                        'status': status,
                        'observation': observation
                    }
                    
                    # Inserir no banco de dados
                    try:
                        appointment_id = add_appointment(appointment_data)
                        
                        # Registrar atividade
                        if 'user' in st.session_state:
                            patient_name = next((p[1] for p in patient_options if p[0] == patient_id), "")
                            log_activity(
                                st.session_state.user['id'],
                                'add',
                                'appointments',
                                appointment_id,
                                f"Agendou sessão para: {patient_name}"
                            )
                        
                        success_msg = "Sessão agendada com sucesso!"
                        
                        if google_cal:
                            success_msg += " (Google Calendar: simulado)"
                        
                        if notify_whatsapp:
                            success_msg += " (WhatsApp: simulado)"
                        
                        st.success(success_msg)
                        time.sleep(1)
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao agendar sessão: {str(e)}")
    
    with tab2:
        st.markdown("<h2 class='section-header'>Calendário de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Seleção de mês e filtros
        col1, col2 = st.columns(2)
        
        with col1:
            selected_month = st.date_input(
                "Selecione o mês",
                value=datetime.now().replace(day=1),
                format="MM/YYYY"
            )
        
        with col2:
            filter_therapist = st.text_input("Filtrar por terapeuta")
        
        # Determinar dias do mês
        first_day = selected_month.replace(day=1)
        
        # Último dia do mês
        if selected_month.month == 12:
            last_day = selected_month.replace(year=selected_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = selected_month.replace(month=selected_month.month + 1, day=1) - timedelta(days=1)
        
        # Obter agendamentos do mês
        month_start = first_day.strftime('%Y-%m-%d')
        month_end = last_day.strftime('%Y-%m-%d')
        
        appointments = get_appointments(start_date=month_start, end_date=month_end)
        
        # Aplicar filtro de terapeuta
        if filter_therapist:
            appointments = [a for a in appointments if filter_therapist.lower() in a['therapist'].lower()]
        
        # Agrupar agendamentos por dia
        appointments_by_day = {}
        
        for appointment in appointments:
            date = appointment['date']
            
            if date not in appointments_by_day:
                appointments_by_day[date] = []
            
            appointments_by_day[date].append(appointment)
        
        # Construir calendário
        # Determinar o dia da semana do primeiro dia do mês (0 = segunda, 6 = domingo)
        first_weekday = first_day.weekday()
        
        # Criar lista de dias no mês
        days_in_month = (last_day - first_day).days + 1
        
        # Criar matriz de semanas
        weeks = []
        current_week = [None] * first_weekday
        
        for day in range(1, days_in_month + 1):
            current_date = first_day.replace(day=day)
            current_week.append(current_date)
            
            # Se chegou ao domingo ou é o último dia do mês, iniciar nova semana
            if current_date.weekday() == 6 or day == days_in_month:
                # Completar a última semana se necessário
                if len(current_week) < 7:
                    current_week.extend([None] * (7 - len(current_week)))
                
                weeks.append(current_week)
                current_week = []
        
        # Exibir calendário
        st.markdown("### Visão Mensal")
        
        # Cabeçalho dos dias da semana
        weekdays = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        
        cols = st.columns(7)
        for i, weekday in enumerate(weekdays):
            cols[i].markdown(f"<div class='calendar-day-header'>{weekday}</div>", unsafe_allow_html=True)
        
        # Exibir semanas
        for week in weeks:
            cols = st.columns(7)
            
            for i, day in enumerate(week):
                if day:
                    date_str = day.strftime('%Y-%m-%d')
                    today = datetime.now().date()
                    
                    # Verificar se é o dia atual
                    is_today = day.date() == today
                    
                    # Verificar se há agendamentos para este dia
                    day_appointments = appointments_by_day.get(date_str, [])
                    
                    # Estilo dependendo se é o dia atual
                    day_class = "calendar-day-today" if is_today else "calendar-day"
                    
                    with cols[i]:
                        st.markdown(f"<div class='{day_class}'>", unsafe_allow_html=True)
                        
                        # Número do dia
                        st.markdown(f"<div style='font-weight:bold; font-size:1.2em;'>{day.day}</div>", unsafe_allow_html=True)
                        
                        # Contagem de agendamentos
                        if day_appointments:
                            st.markdown(f"<div style='margin-bottom:5px;'>{len(day_appointments)} sessões</div>", unsafe_allow_html=True)
                            
                            # Listar os 3 primeiros agendamentos
                            for j, appointment in enumerate(day_appointments[:3]):
                                status_style = f"background-color:{STATUS_COLORS.get(appointment['status'], '#ECEFF1')}; padding:2px 5px; border-radius:3px; font-size:0.8em; margin-bottom:2px; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"
                                
                                st.markdown(f"""
                                <div style="{status_style}">
                                    {appointment['time']} - {appointment['patient_name'][:10]}...
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Indicar se há mais agendamentos
                            if len(day_appointments) > 3:
                                st.markdown(f"<div style='font-size:0.8em;'>+ {len(day_appointments) - 3} mais</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    # Dia vazio (fora do mês atual)
                    cols[i].markdown("<div class='calendar-day'></div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h2 class='section-header'>Gestão de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_period = st.date_input(
                "Período",
                value=[datetime.now(), datetime.now() + timedelta(days=7)]
            )
        
        with col2:
            # Filtro por paciente
            patient_options = [(p['id'], p['name']) for p in patients]
            patient_options.insert(0, ("all", "Todos os pacientes"))
            
            filter_patient = st.selectbox(
                "Paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="apt_filter_patient"
            )
        
        with col3:
            filter_status = st.multiselect(
                "Status",
                options=SCHEDULE_STATUS,
                default=[]
            )
        
        # Obter agendamentos com filtros
        if len(filter_period) == 2:
            start_date, end_date = filter_period
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Construir filtros para consulta
            patient_id = None if filter_patient == "all" else filter_patient
            status_filter = filter_status if filter_status else None
            
            appointments = get_appointments(
                start_date=start_date_str,
                end_date=end_date_str,
                patient_id=patient_id,
                status=status_filter
            )
            
            if appointments:
                st.markdown(f"Exibindo {len(appointments)} agendamentos")
                
                for appointment in appointments:
                    status_class = f"status-{appointment['status'].lower().replace(' ', '-')}"
                    
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns([1.5, 3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{appointment['date']}**<br>{appointment['time']}", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**{appointment['patient_name']}**<br>Terapeuta: {appointment['therapist']}", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"**Status:** <span class='{status_class}'>{appointment['status']}</span>", unsafe_allow_html=True)
                        
                        if appointment.get('observation'):
                            # Limitar observação para exibição
                            obs_display = appointment['observation']
                            if len(obs_display) > 50:
                                obs_display = obs_display[:50] + "..."
                            
                            st.markdown(f"<span style='color:#666;'>Obs: {obs_display}</span>", unsafe_allow_html=True)
                    
                    with col4:
                        # Botão para editar
                        if st.button("Editar", key=f"edit_apt_{appointment['id']}"):
                            st.session_state.edit_appointment = appointment['id']
                            st.experimental_rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Modal de edição
                if 'edit_appointment' in st.session_state:
                    appointment_id = st.session_state.edit_appointment
                    
                    # Buscar dados do agendamento
                    selected_appointment = next((a for a in appointments if a['id'] == appointment_id), None)
                    
                    if selected_appointment:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("### Editar Agendamento")
                        
                        with st.form("edit_appointment_form"):
                            # Campos para edição
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Converter string para date
                                date_obj = datetime.strptime(selected_appointment['date'], '%Y-%m-%d').date()
                                edit_date = st.date_input("Data", value=date_obj)
                                
                                # Converter string para time
                                time_obj = datetime.strptime(selected_appointment['time'], '%H:%M').time()
                                edit_time = st.time_input("Horário", value=time_obj)
                            
                            with col2:
                                edit_therapist = st.text_input("Terapeuta", value=selected_appointment['therapist'])
                                
                                # Encontrar índice do status atual
                                status_index = SCHEDULE_STATUS.index(selected_appointment['status']) if selected_appointment['status'] in SCHEDULE_STATUS else 0
                                edit_status = st.selectbox("Status", options=SCHEDULE_STATUS, index=status_index)
                            
                            edit_observation = st.text_area("Observações", value=selected_appointment.get('observation', ''), height=100)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                save_btn = st.form_submit_button("Salvar Alterações")
                            
                            with col2:
                                cancel_btn = st.form_submit_button("Cancelar")
                            
                            if save_btn:
                                # Preparar dados para atualização
                                updated_data = {
                                    'date': edit_date.strftime('%Y-%m-%d'),
                                    'time': edit_time.strftime('%H:%M'),
                                    'therapist': edit_therapist,
                                    'status': edit_status,
                                    'observation': edit_observation
                                }
                                
                                # Atualizar no banco de dados
                                try:
                                    update_appointment(appointment_id, updated_data)
                                    
                                    # Registrar atividade
                                    if 'user' in st.session_state:
                                        log_activity(
                                            st.session_state.user['id'],
                                            'update',
                                            'appointments',
                                            appointment_id,
                                            f"Atualizou agendamento para: {selected_appointment['patient_name']}"
                                        )
                                    
                                    # Limpar estado de edição
                                    del st.session_state.edit_appointment
                                    
                                    st.success("Agendamento atualizado com sucesso!")
                                    time.sleep(1)
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Erro ao atualizar agendamento: {str(e)}")
                            
                            elif cancel_btn:
                                # Limpar estado de edição
                                del st.session_state.edit_appointment
                                st.experimental_rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Nenhum agendamento encontrado com os filtros selecionados.")
    
    with tab4:
        st.markdown("<h2 class='section-header'>Agrupamentos Sugeridos</h2>", unsafe_allow_html=True)
        
        st.markdown("""
        Este sistema analisa o perfil dos pacientes e sugere possíveis agrupamentos para sessões em conjunto, 
        baseados em compatibilidade de perfil comportamental, habilidades a serem trabalhadas e nível de suporte.
        """)
        
        # Data para análise
        analysis_date = st.date_input("Data para análise", value=datetime.now())
        
        if st.button("Gerar Sugestões de Agrupamentos"):
            # Obter sugestões
            groups = suggest_groups()
            
            if groups:
                st.markdown("### Sugestões de Agrupamentos")
                
                for i, group in enumerate(groups):
                    # Gerar cor para o grupo baseado no diagnóstico
                    diagnosis_colors = {
                        "Transtorno do Espectro Autista": "#E1BEE7",  # Roxo claro
                        "TEA": "#E1BEE7",
                        "TDAH": "#BBDEFB",  # Azul claro
                        "Atraso": "#C8E6C9",  # Verde claro
                        "Síndrome": "#FFE0B2",  # Laranja claro
                        "Outro": "#F5F5F5"  # Cinza claro
                    }
                    
                    # Encontrar cor baseada em parte do diagnóstico
                    color = "#F5F5F5"  # Padrão
                    for key, value in diagnosis_colors.items():
                        if key in group['diagnosis']:
                            color = value
                            break
                    
                    st.markdown(f"""
                    <div class='card' style='border-left: 5px solid {color};'>
                        <h3>{group['name']}</h3>
                        <p><strong>Compatibilidade:</strong> {group['compatibility']}%</p>
                        <p><strong>Faixa etária:</strong> {group['age_range']} anos</p>
                        <p><strong>Foco principal:</strong> {group['skill_focus']}</p>
                        
                        <h4>Pacientes compatíveis:</h4>
                        <ul>
                    """, unsafe_allow_html=True)
                    
                    for patient in group['patients']:
                        st.markdown(f"""
                        <li>{patient['name']} ({patient.get('age', '?')} anos) - {patient.get('support_level', 'Não especificado')}</li>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Opções para criar agendamentos
                st.markdown("### Ações")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Agendar Grupos Selecionados"):
                        st.success("Simulação: Agendamentos em grupo criados com sucesso!")
                
                with col2:
                    report_format = st.selectbox(
                        "Formato do relatório",
                        options=["PDF", "Excel", "Word"]
                    )
                    
                    if st.button("Exportar Relatório"):
                        st.success(f"Simulação: Relatório exportado em formato {report_format}!")
            else:
                st.info("Não foi possível gerar sugestões de agrupamento com os dados atuais.")

def reports_page():
    """Exibe a página de relatórios"""
    st.markdown("<h1 class='main-header'>Relatórios</h1>", unsafe_allow_html=True)
    
    # Tabs para diferentes relatórios
    tab1, tab2, tab3, tab4 = st.tabs([
        "Relatório de Evolução", 
        "Relatório de Frequência", 
        "Relatório de Habilidades",
        "Compartilhar via WhatsApp"
    ])
    
    with tab1:  # Relatório de Evolução
        st.markdown("<h2 class='section-header'>Gerar Relatório de Evolução</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente
        patients = get_patients()
        patient_options = [(p['id'], p['name']) for p in patients]
        
        patient_id = st.selectbox(
            "Selecione o Paciente",
            options=[p[0] for p in patient_options],
            format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
            key="report_patient"
        )
        
        # Seleção de período
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Data Inicial", value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("Data Final", value=datetime.now())
        
        # Opções do relatório
        report_options = st.multiselect(
            "Incluir no relatório",
            options=[
                "Dados pessoais",
                "Resumo de atendimentos",
                "Gráficos de evolução",
                "Avaliações do período",
                "Habilidades trabalhadas",
                "Recomendações"
            ],
            default=[
                "Dados pessoais",
                "Resumo de atendimentos",
                "Habilidades trabalhadas"
            ]
        )
        
        if st.button("Gerar Relatório de Evolução"):
            if patient_id and report_options:
                # Obter dados do paciente
                patient = get_patient(patient_id)
                
                if patient:
                    # Obter nome do paciente
                    patient_name = patient['name']
                    
                    # Obter sessões do período
                    conn = sqlite3.connect('data/neurobase.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                    SELECT * FROM sessions 
                    WHERE patient_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                    """, (patient_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                    
                    columns = [column[0] for column in cursor.description]
                    sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    # Obter avaliações do período
                    cursor.execute("""
                    SELECT * FROM evaluations 
                    WHERE patient_id = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                    """, (patient_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
                    
                    columns = [column[0] for column in cursor.description]
                    evaluations = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    conn.close()
                    
                    # Criar o relatório
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    
                    # Cabeçalho do relatório
                    st.markdown(f"<h2>Relatório de Evolução - {patient_name}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p>Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
                    
                    # Dados pessoais
                    if "Dados pessoais" in report_options:
                        st.markdown("### Dados Pessoais")
                        
                        # Calcular idade
                        if patient.get('birth_date'):
                            try:
                                birth_date = datetime.strptime(patient['birth_date'], '%Y-%m-%d')
                                age = (datetime.now() - birth_date).days // 365
                                st.markdown(f"**Idade:** {age} anos")
                            except:
                                pass
                        
                        st.markdown(f"**Diagnóstico:** {patient.get('diagnosis', 'Não informado')}")
                        
                        if patient.get('support_level'):
                            st.markdown(f"**Nível de Suporte:** {patient['support_level']}")
                    
                    # Resumo de atendimentos
                    if "Resumo de atendimentos" in report_options:
                        st.markdown("### Resumo de Atendimentos")
                        st.markdown(f"**Total de atendimentos no período:** {len(sessions)}")
                        
                        if sessions:
                            st.markdown("#### Evolução observada")
                            
                            for session in sessions:
                                st.markdown(f"**Sessão {session['date']}:**")
                                
                                if session.get('evolution'):
                                    st.markdown(session['evolution'])
                                else:
                                    st.markdown("*Sem registro de evolução*")
                    
                    # Habilidades trabalhadas
                    if "Habilidades trabalhadas" in report_options and sessions:
                        st.markdown("### Habilidades Trabalhadas")
                        
                        # Contar frequência de habilidades
                        skill_counts = {}
                        
                        for session in sessions:
                            if session.get('skills_worked'):
                                skills = [s.strip() for s in session['skills_worked'].split(',') if s.strip()]
                                
                                for skill in skills:
                                    if skill in skill_counts:
                                        skill_counts[skill] += 1
                                    else:
                                        skill_counts[skill] = 1
                        
                        if skill_counts:
                            # Ordenar por frequência
                            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
                            
                            # Criar DataFrame para visualização
                            df = pd.DataFrame(sorted_skills, columns=['Habilidade', 'Frequência'])
                            
                            # Limitar para as 10 habilidades mais trabalhadas
                            if len(df) > 10:
                                df = df.head(10)
                            
                            # Criar gráfico
                            fig = px.bar(
                                df,
                                x='Frequência',
                                y='Habilidade',
                                orientation='h',
                                title='Habilidades Mais Trabalhadas',
                                color='Frequência',
                                color_continuous_scale='Viridis'
                            )
                            
                            fig.update_layout(
                                xaxis_title='Número de Sessões',
                                yaxis_title='',
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Gráficos de evolução
                    if "Gráficos de evolução" in report_options:
                        st.markdown("### Gráficos de Evolução")
                        
                        # Obter todas as avaliações do paciente (para ter mais dados)
                        all_evaluations = get_patient_evaluations(patient_id)
                        
                        if len(all_evaluations) > 1:  # Precisa de pelo menos 2 avaliações
                            # Organizar avaliações por data
                            all_evaluations.sort(key=lambda x: x['date'])
                            
                            # Filtrar apenas avaliações dentro ou próximas ao período
                            # (para ter mais contexto)
                            period_start = (start_date - timedelta(days=30)).strftime('%Y-%m-%d')
                            period_end = (end_date + timedelta(days=30)).strftime('%Y-%m-%d')
                            
                            period_evaluations = [e for e in all_evaluations if e['date'] >= period_start and e['date'] <= period_end]
                            
                            if len(period_evaluations) > 1:
                                # Extrair dados de evolução
                                evolution_data = {}
                                
                                for evaluation in period_evaluations:
                                    if 'scores' in evaluation and evaluation['scores'] and isinstance(evaluation['scores'], dict):
                                        scores = evaluation['scores']
                                        if isinstance(scores, str):
                                            try:
                                                scores = json.loads(scores)
                                            except:
                                                scores = {}
                                        
                                        for area, score in scores.items():
                                            if area not in evolution_data:
                                                evolution_data[area] = []
                                            
                                            evolution_data[area].append({
                                                'date': evaluation['date'],
                                                'score': score
                                            })
                                
                                # Criar gráficos para áreas com pelo menos 2 avaliações
                                areas_with_data = [area for area, data in evolution_data.items() if len(data) > 1]
                                
                                if areas_with_data:
                                    # Limitar para 5 áreas principais
                                    areas_to_show = areas_with_data[:5]
                                    
                                    # Criar gráfico de linhas
                                    fig = go.Figure()
                                    
                                    for area in areas_to_show:
                                        dates = [item['date'] for item in evolution_data[area]]
                                        scores = [item['score'] for item in evolution_data[area]]
                                        
                                        fig.add_trace(go.Scatter(
                                            x=dates,
                                            y=scores,
                                            mode='lines+markers',
                                            name=area
                                        ))
                                    
                                    fig.update_layout(
                                        title='Evolução por Área',
                                        xaxis_title='Data',
                                        yaxis_title='Pontuação',
                                        height=400,
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        )
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Não há dados suficientes para gerar gráficos de evolução.")
                            else:
                                st.info("Não há avaliações suficientes para gerar gráficos de evolução.")
                        else:
                            st.info("São necessárias pelo menos duas avaliações para analisar a evolução.")
                    
                    # Avaliações do período
                    if "Avaliações do período" in report_options:
                        st.markdown("### Avaliações no Período")
                        
                        if evaluations:
                            for evaluation in evaluations:
                                st.markdown(f"#### {evaluation['date']} - {evaluation['evaluation_type']}")
                                
                                st.markdown("**Resultados:**")
                                if evaluation.get('results'):
                                    st.markdown(evaluation['results'])
                                else:
                                    st.markdown("*Sem registro de resultados*")
                                
                                st.markdown("**Recomendações:**")
                                if evaluation.get('recommendations'):
                                    st.markdown(evaluation['recommendations'])
                                else:
                                    st.markdown("*Sem registro de recomendações*")
                        else:
                            st.info("Não foram realizadas avaliações no período selecionado.")
                    
                    # Recomendações
                    if "Recomendações" in report_options:
                        st.markdown("### Recomendações para o Próximo Período")
                        recommendations = st.text_area("Adicione recomendações para o próximo período", height=150)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Botões de exportação
                    st.markdown("### Exportar Relatório")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            "Exportar como PDF",
                            data="Simulação de PDF do relatório",
                            file_name=f"Relatorio_{patient_name}_{start_date.strftime('%d%m%Y')}_{end_date.strftime('%d%m%Y')}.pdf",
                            mime="application/pdf"
                        )
                    
                    with col2:
                        st.download_button(
                            "Exportar como Word",
                            data="Simulação de DOCX do relatório",
                            file_name=f"Relatorio_{patient_name}_{start_date.strftime('%d%m%Y')}_{end_date.strftime('%d%m%Y')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    
                    with col3:
                        if st.button("Enviar por E-mail"):
                            st.success("Simulação: Relatório enviado por e-mail para o responsável!")
                else:
                    st.error("Paciente não encontrado.")
            else:
                st.error("Por favor, selecione um paciente e pelo menos uma opção para o relatório.")
    
    with tab2:  # Relatório de Frequência
        st.markdown("<h2 class='section-header'>Relatório de Frequência</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            month_year = st.date_input(
                "Selecione o mês",
                value=datetime.now().replace(day=1),
                format="MM/YYYY",
                key="freq_month"
            )
        
        with col2:
            # Filtro por paciente
            patient_options = [(p['id'], p['name']) for p in patients]
            patient_options.insert(0, ("all", "Todos os pacientes"))
            
            freq_patient = st.selectbox(
                "Paciente (opcional)",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="freq_patient"
            )
        
        if st.button("Gerar Relatório de Frequência"):
            # Determinar dias do mês
            first_day = month_year.replace(day=1)
            
            # Último dia do mês
            if month_year.month == 12:
                last_day = month_year.replace(year=month_year.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = month_year.replace(month=month_year.month + 1, day=1) - timedelta(days=1)
            
            # Obter agendamentos do mês
            month_start = first_day.strftime('%Y-%m-%d')
            month_end = last_day.strftime('%Y-%m-%d')
            
            # Filtros para consulta
            patient_id = None if freq_patient == "all" else freq_patient
            
            appointments = get_appointments(
                start_date=month_start,
                end_date=month_end,
                patient_id=patient_id
            )
            
            if appointments:
                st.markdown("<h3>Relatório de Frequência</h3>", unsafe_allow_html=True)
                
                # Calcular estatísticas
                status_counts = {}
                for status in SCHEDULE_STATUS:
                    status_counts[status] = 0
                
                for appointment in appointments:
                    status = appointment['status']
                    status_counts[status] += 1
                
                total = len(appointments)
                
                # Exibir estatísticas
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                
                # Título do relatório
                month_name = month_year.strftime("%B de %Y")
                if freq_patient != "all":
                    patient_name = next((p[1] for p in patient_options if p[0] == freq_patient), "")
                    st.markdown(f"<h3>Frequência de {patient_name} em {month_name}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3>Frequência Geral em {month_name}</h3>", unsafe_allow_html=True)
                
                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Sessões", total)
                
                with col2:
                    attended_rate = status_counts["Concluído"] / total * 100 if total > 0 else 0
                    st.metric("Taxa de Presença", f"{attended_rate:.1f}%")
                
                with col3:
                    missed_rate = status_counts["Faltou"] / total * 100 if total > 0 else 0
                    st.metric("Taxa de Faltas", f"{missed_rate:.1f}%")
                
                with col4:
                    canceled_rate = status_counts["Cancelado"] / total * 100 if total > 0 else 0
                    st.metric("Taxa de Cancelamentos", f"{canceled_rate:.1f}%")
                
                # Gráfico de frequência
                # Filtrar status com contagem > 0
                status_data = {k: v for k, v in status_counts.items() if v > 0}
                
                if status_data:
                    fig = px.pie(
                        names=list(status_data.keys()),
                        values=list(status_data.values()),
                        title="Distribuição de Status",
                        color=list(status_data.keys()),
                        color_discrete_map={status: color for status, color in zip(SCHEDULE_STATUS, px.colors.qualitative.Pastel)}
                    )
                    
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Lista de faltas
                if status_counts["Faltou"] > 0:
                    st.markdown("<h3>Detalhamento de Faltas</h3>", unsafe_allow_html=True)
                    
                    # Filtrar faltas
                    missed_appointments = [a for a in appointments if a['status'] == "Faltou"]
                    
                    for appointment in missed_appointments:
                        st.markdown(f"""
                        <div style='background-color:#FFEBEE; padding:10px; margin:5px; border-radius:5px;'>
                            <strong>{appointment['date']} às {appointment['time']}</strong> - {appointment['patient_name']} (Terapeuta: {appointment['therapist']})
                            {f"<br><em>Observação: {appointment['observation']}</em>" if appointment.get('observation') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                
                # Oferecer download do relatório
                st.download_button(
                    "Exportar Relatório de Frequência",
                    data="Simulação de relatório de frequência",
                    file_name=f"Frequencia_{month_year.strftime('%m%Y')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("Não há dados de agendamento para o período selecionado.")
    
    with tab3:  # Relatório de Habilidades
        st.markdown("<h2 class='section-header'>Relatório de Habilidades</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de paciente
            patient_options = [(p['id'], p['name']) for p in patients]
            
            skills_patient = st.selectbox(
                "Selecione o Paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="skills_patient"
            )
        
        with col2:
            skills_period = st.selectbox(
                "Período de Análise",
                options=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"]
            )
        
        if st.button("Analisar Habilidades"):
            # Determinar período de análise
            days = 30  # Padrão: último mês
            
            if skills_period == "Últimos 3 meses":
                days = 90
            elif skills_period == "Últimos 6 meses":
                days = 180
            elif skills_period == "Último ano":
                days = 365
            
            # Obter nome do paciente
            patient_name = next((p[1] for p in patient_options if p[0] == skills_patient), "")
            
            # Obter habilidades trabalhadas
            skill_frequency = analyze_skills_frequency(patient_id=skills_patient, days=days)
            
            # Obter comparação com necessidades
            comparison = compare_skills_with_needs(skills_patient, days)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            st.markdown(f"<h3>Análise de Habilidades para {patient_name}</h3>", unsafe_allow_html=True)
            st.markdown(f"Período: últimos {days} dias")
            
            if skill_frequency:
                # Criar DataFrame para visualização
                df = pd.DataFrame(
                    sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True),
                    columns=['Habilidade', 'Frequência']
                )
                
                # Limitar para as 15 habilidades mais trabalhadas
                if len(df) > 15:
                    df = df.head(15)
                
                # Criar gráfico
                fig = px.bar(
                    df,
                    x='Frequência',
                    y='Habilidade',
                    orientation='h',
                    title='Habilidades Mais Trabalhadas',
                    color='Frequência',
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(
                    xaxis_title='Número de Sessões',
                    yaxis_title='',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Comparar com necessidades do paciente
                if comparison:
                    st.markdown("### Comparação com Necessidades Avaliadas")
                    
                    # Criar DataFrame para comparação
                    comparison_data = []
                    
                    for skill, data in comparison.items():
                        comparison_data.append({
                            'Habilidade': skill,
                            'Prioridade': data['priority'],
                            'Frequência': data['frequency'],
                            'Adequação (%)': round(data['adequacy'], 1)
                        })
                    
                    df_comparison = pd.DataFrame(comparison_data)
                    
                    # Ordenar por adequação (crescente)
                    df_comparison = df_comparison.sort_values('Adequação (%)')
                    
                    # Criar gráfico de barras para comparação
                    fig_comp = go.Figure()
                    
                    fig_comp.add_trace(go.Bar(
                        x=df_comparison['Habilidade'],
                        y=df_comparison['Prioridade'],
                        name='Prioridade',
                        marker_color='#7B1FA2'
                    ))
                    
                    fig_comp.add_trace(go.Bar(
                        x=df_comparison['Habilidade'],
                        y=df_comparison['Frequência'],
                        name='Frequência',
                        marker_color='#4CAF50'
                    ))
                    
                    fig_comp.update_layout(
                        title='Prioridades vs. Frequência',
                        xaxis_tickangle=-45,
                        barmode='group',
                        height=400
                    )
                    
                    st.plotly_chart(fig_comp, use_container_width=True)
                    
                    # Identificar áreas com baixa adequação
                    low_adequacy = df_comparison[df_comparison['Adequação (%)'] < 50]
                    
                    if not low_adequacy.empty:
                        st.markdown("### Recomendações")
                        st.markdown("As seguintes habilidades precisam de maior atenção:")
                        
                        for _, row in low_adequacy.iterrows():
                            st.markdown(f"""
                            <div class='warning-alert'>
                                <strong>{row['Habilidade']}</strong> - Adequação: {row['Adequação (%)']}%
                                <br>
                                Esta habilidade tem prioridade {row['Prioridade']} mas foi trabalhada apenas {row['Frequência']} vezes.
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("As habilidades estão sendo trabalhadas adequadamente conforme as prioridades identificadas.")
                else:
                    st.warning("Não foi possível comparar com necessidades do paciente. Verifique se há avaliações registradas.")
            else:
                st.info("Não há dados de atendimentos para este paciente no período selecionado.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Botões de exportação
            st.markdown("### Exportar Relatório")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "Exportar como PDF",
                    data="Simulação de PDF do relatório de habilidades",
                    file_name=f"Habilidades_{patient_name}.pdf",
                    mime="application/pdf"
                )
            
            with col2:
                st.download_button(
                    "Exportar como Excel",
                    data="Simulação de XLSX do relatório de habilidades",
                    file_name=f"Habilidades_{patient_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with tab4:  # Compartilhar via WhatsApp
        st.markdown("<h2 class='section-header'>Compartilhar Relatórios via WhatsApp</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente e tipo de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleção de paciente
            patient_options = [(p['id'], p['name']) for p in patients]
            
            whatsapp_patient = st.selectbox(
                "Selecione o Paciente",
                options=[p[0] for p in patient_options],
                format_func=lambda x: next((p[1] for p in patient_options if p[0] == x), ""),
                key="whatsapp_patient"
            )
        
        with col2:
            report_type = st.selectbox(
                "Tipo de Relatório",
                options=[
                    "Evolução Mensal",
                    "Evolução Trimestral",
                    "Relatório de Avaliação",
                    "Relatório de Frequência",
                    "Relatório Personalizado"
                ]
            )
        
        # Opções para grupos de WhatsApp
        st.markdown("### Opções de Envio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            recipient = st.radio(
                "Destinatário",
                options=[
                    "Grupo da família",
                    "Responsável direto",
                    "Equipe multidisciplinar",
                    "Personalizado"
                ]
            )
        
        with col2:
            if recipient == "Personalizado":
                whatsapp_number = st.text_input("Número de WhatsApp (com DDD)")
            
            include_attachments = st.checkbox("Incluir anexos (gráficos e tabelas)")
        
        # Mensagem personalizada
        st.markdown("### Mensagem Personalizada (opcional)")
        custom_message = st.text_area("Adicione uma mensagem personalizada ao relatório")
        
        if st.button("Enviar Relatório via WhatsApp"):
            if whatsapp_patient:
                # Obter nome do paciente
                patient_name = next((p[1] for p in patient_options if p[0] == whatsapp_patient), "")
                
                # Simulação de envio
                st.success(f"Simulação: Relatório {report_type} de {patient_name} enviado com sucesso para {recipient}!")
                
                # Exibir prévia da mensagem
                st.markdown("### Prévia da Mensagem")
                
                st.markdown("""
                <div style='background-color:#E1F5FE; padding:15px; border-radius:10px;'>
                """, unsafe_allow_html=True)
                
                st.markdown(f"*Relatório {report_type} - {patient_name}*")
                st.markdown("Prezado(a) responsável,")
                st.markdown(f"Segue o relatório de {report_type} do paciente {patient_name}.")
                
                if custom_message:
                    st.markdown(f"*Nota do terapeuta:*\n{custom_message}")
                
                st.markdown("Atenciosamente,\nEquipe de Psicomotricidade")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Mostrar QR Code simulado
                st.markdown("### QR Code para Download")
                
                # Inserir imagem placeholder para QR code
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Relatorio", width=150)
                
                st.markdown("*Escaneie o QR Code acima para visualizar ou baixar o relatório completo*")
            else:
                st.error("Por favor, selecione um paciente para enviar o relatório.")

def settings_page():
    """Exibe a página de configurações"""
    st.markdown("<h1 class='main-header'>Configurações</h1>", unsafe_allow_html=True)
    
    # Verificar se usuário é administrador
    is_admin = 'perfil' in st.session_state and st.session_state.perfil == 'admin'
    
    # Tabs para diferentes configurações
    if is_admin:
        tab1, tab2, tab3, tab4 = st.tabs(["Sistema", "Backup e Restauração", "Usuários", "Sobre"])
    else:
        tab1, tab4 = st.tabs(["Preferências Pessoais", "Sobre"])
    
    with tab1:  # Sistema ou Preferências Pessoais
        if is_admin:
            st.markdown("<h2 class='section-header'>Configurações do Sistema</h2>", unsafe_allow_html=True)
            
            # Opções gerais
            st.markdown("### Opções Gerais")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email_notifications = st.checkbox("Ativar notificações por e-mail", value=True)
                whatsapp_notifications = st.checkbox("Ativar notificações por WhatsApp", value=True)
            
            with col2:
                auto_backup = st.checkbox("Ativar backup automático diário", value=True)
                retention_days = st.number_input("Dias de retenção de backups", min_value=7, value=30)
            
            # Personalização
            st.markdown("### Personalização")
            
            theme_color = st.selectbox(
                "Tema de cores",
                options=["Roxo (Padrão)", "Azul", "Verde", "Vermelho"]
            )
            
            logo = st.file_uploader("Logo personalizada", type=["png", "jpg", "jpeg"])
            
            clinic_name = st.text_input("Nome da clínica", value="NeuroBase Psicomotricidade")
            
            # Integração
            st.markdown("### Integrações")
            
            google_integration = st.checkbox("Integrar com Google Calendar", value=False)
            if google_integration:
                google_api_key = st.text_input("Google API Key", type="password")
            
            whatsapp_integration = st.checkbox("Integrar com WhatsApp Business API", value=False)
            if whatsapp_integration:
                whatsapp_api_key = st.text_input("WhatsApp Business API Key", type="password")
            
            # Salvar configurações
            if st.button("Salvar Configurações"):
                st.success("Configurações salvas com sucesso!")
        else:
            st.markdown("<h2 class='section-header'>Preferências Pessoais</h2>", unsafe_allow_html=True)
            
            # Preferências de interface
            st.markdown("### Interface")
            
            theme_preference = st.selectbox(
                "Tema",
                options=["Claro", "Escuro", "Sistema"]
            )
            
            date_format = st.selectbox(
                "Formato de data",
                options=["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"]
            )
            
            # Notificações
            st.markdown("### Notificações")
            
            email_reminders = st.checkbox("Receber lembretes por e-mail", value=True)
            desktop_notifications = st.checkbox("Ativar notificações de desktop", value=True)
            
            # Salvar preferências
            if st.button("Salvar Preferências"):
                st.success("Preferências salvas com sucesso!")
    
    if is_admin:
        with tab2:  # Backup e Restauração
            st.markdown("<h2 class='section-header'>Backup e Restauração</h2>", unsafe_allow_html=True)
            
            # Backup manual
            st.markdown("### Backup Manual")
            
            if st.button("Criar Backup Agora"):
                success, backup_path = create_backup()
                
                if success:
                    st.success(f"Backup criado com sucesso: {backup_path}")
                else:
                    st.error(f"Erro ao criar backup: {backup_path}")
            
            # Simulação de backups disponíveis
            st.markdown("### Backups Disponíveis")
            
            # Criar dados simulados
            backups = []
            for i in range(5):
                backups.append({
                    'id': str(uuid.uuid4()),
                    'timestamp': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f"{1 + i * 0.5:.1f} MB",
                    'user': "Administrador" if i % 2 == 0 else "Sistema",
                    'file': f"data/backups/neurobase_{(datetime.now() - timedelta(days=i)).strftime('%Y%m%d_%H%M%S')}.db"
                })
            
            # Exibir backups
            for backup in backups:
                st.markdown(f"""
                <div class='card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <strong>{backup['timestamp']}</strong><br>
                            Tamanho: {backup['size']}<br>
                            Criado por: {backup['user']}
                        </div>
                        <div>
                            <button style='background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 4px; margin-right: 5px;'>
                                Restaurar
                            </button>
                            <button style='background-color: #F44336; color: white; border: none; padding: 5px 10px; border-radius: 4px;'>
                                Excluir
                            </button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Exportação de dados
            st.markdown("### Exportação de Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exportar Todos os Dados (CSV)"):
                    st.success("Simulação: Dados exportados para CSV com sucesso!")
            
            with col2:
                if st.button("Exportar Todos os Dados (JSON)"):
                    st.success("Simulação: Dados exportados para JSON com sucesso!")
            
            # Importação de dados
            st.markdown("### Importação de Dados")
            
            import_file = st.file_uploader("Selecione arquivo para importar", type=["csv", "json", "xlsx"])
            
            if import_file:
                import_type = st.selectbox(
                    "Tipo de importação",
                    options=["Pacientes", "Atendimentos", "Avaliações", "Agendamentos", "Todos"]
                )
                
                if st.button("Iniciar Importação"):
                    st.success(f"Simulação: Importação de {import_type} iniciada com sucesso!")
                    st.info("O processo de importação pode levar alguns minutos dependendo do tamanho do arquivo.")
        
        with tab3:  # Usuários
            st.markdown("<h2 class='section-header'>Gerenciamento de Usuários</h2>", unsafe_allow_html=True)
            
            # Lista de usuários (simulada)
            st.markdown("### Usuários do Sistema")
            
            # Criar dados simulados
            users = [
                {"id": "1", "name": "Administrador", "email": "admin@neurobase.com", "role": "admin", "last_login": "2025-05-14 09:15:22"},
                {"id": "2", "name": "Terapeuta", "email": "terapeuta@neurobase.com", "role": "terapeuta", "last_login": "2025-05-14 08:30:15"},
                {"id": "3", "name": "Luciana Oliveira", "email": "luciana@neurobase.com", "role": "terapeuta", "last_login": "2025-05-13 16:45:05"},
                {"id": "4", "name": "Carlos Santos", "email": "carlos@neurobase.com", "role": "terapeuta", "last_login": "2025-05-12 10:20:33"},
            ]
            
            # Exibir usuários em cards
            for user in users:
                st.markdown(f"""
                <div class='card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <strong>{user['name']}</strong><br>
                            E-mail: {user['email']}<br>
                            Perfil: {user['role'].capitalize()}<br>
                            Último acesso: {user['last_login']}
                        </div>
                        <div>
                            <button style='background-color: #2196F3; color: white; border: none; padding: 5px 10px; border-radius: 4px; margin-right: 5px;'>
                                Editar
                            </button>
                            <button style='background-color: #F44336; color: white; border: none; padding: 5px 10px; border-radius: 4px;'>
                                Desativar
                            </button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Adicionar novo usuário
            st.markdown("### Adicionar Novo Usuário")
            
            with st.form("new_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Nome completo*")
                    new_email = st.text_input("E-mail*")
                
                with col2:
                    new_password = st.text_input("Senha*", type="password")
                    new_role = st.selectbox("Perfil*", options=["terapeuta", "admin"])
                
                st.markdown("(*) Campos obrigatórios")
                submit_user = st.form_submit_button("Adicionar Usuário")
                
                if submit_user:
                    if new_name and new_email and new_password:
                        st.success(f"Usuário {new_name} adicionado com sucesso!")
                    else:
                        st.error("Por favor, preencha todos os campos obrigatórios.")
    
    with tab4:  # Sobre
        st.markdown("<h2 class='section-header'>Sobre o Sistema</h2>", unsafe_allow_html=True)
        
        # Logo
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.image(APP_LOGO, width=200)
        
        # Informações do sistema
        st.markdown(f"### NeuroBase v{APP_VERSION}")
        st.markdown("**Sistema Integrado de Gestão em Psicomotricidade**")
        
        st.markdown("""
        O NeuroBase é uma plataforma completa para clínicas e profissionais da área de psicomotricidade, 
        oferecendo ferramentas para o gerenciamento eficiente de pacientes, atendimentos, avaliações e agendamentos.
        """)
        
        st.markdown("#### Desenvolvido por")
        st.markdown("Equipe NeuroBase")
        
        st.markdown("#### Recursos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - Cadastro e gerenciamento de pacientes
            - Registro de atendimentos
            - Avaliações e acompanhamento
            - Agendamentos com integração a agenda
            """)
        
        with col2:
            st.markdown("""
            - Relatórios automatizados
            - Compartilhamento via WhatsApp
            - Análise de habilidades trabalhadas
            - Sugestão de agrupamentos
            """)
        
        st.markdown("#### Informações Técnicas")
        st.markdown(f"- Versão: {APP_VERSION}")
        st.markdown(f"- Data da última atualização: 14 de maio de 2025")
        st.markdown(f"- Plataforma: Python + Streamlit")
        st.markdown(f"- Banco de dados: SQLite")
        
        # Versão e copyright
        st.markdown("---")
        st.markdown("© 2025 NeuroBase - Todos os direitos reservados")

# Função principal
def main():
    """Função principal do aplicativo"""
    # Inicializar banco de dados
    setup_database()
    
    # Verificar estado de autenticação
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Página de login se não estiver autenticado
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Menu lateral
    with st.sidebar:
        # Logo e informações do usuário
        st.image(APP_LOGO, width=100)
        
        st.markdown(f"### Olá, {st.session_state.user['name']}")
        st.markdown(f"**Perfil:** {st.session_state.user['role'].capitalize()}")
        st.markdown("---")
        
        # Menu de navegação
        selected = st.selectbox(
            "Menu",
            options=[
                "Dashboard",
                "Pacientes",
                "Atendimentos",
                "Avaliações",
                "Agendamentos",
                "Relatórios",
                "Configurações"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Botão de logout
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.experimental_rerun()
        
        # Versão do sistema
        st.markdown(f"<div class='version-info'>v{APP_VERSION}</div>", unsafe_allow_html=True)
    
    # Exibir página selecionada
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Pacientes":
        patients_page()
    elif selected == "Atendimentos":
        sessions_page()
    elif selected == "Avaliações":
        evaluations_page()
    elif selected == "Agendamentos":
        appointments_page()
    elif selected == "Relatórios":
        reports_page()
    elif selected == "Configurações":
        settings_page()

if __name__ == "__main__":
    main()import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json
import os
import base64
from PIL import Image
import io
import matplotlib.pyplot as plt
import time
import hashlib
import sqlite3
import uuid
import yaml
from yaml.loader import SafeLoader
from datetime import datetime, timedelta

# Versão do aplicativo
APP_VERSION = "1.0.1"

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
    .version-info {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 0.7rem;
        color: #9E9E9E;
    }
    .stAlert {
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Constantes
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

NIVEIS_DESENVOLVIMENTO = [
    "Muito inferior",
    "Inferior",
    "Normal baixo",
    "Normal médio",
    "Normal alto",
    "Superior",
    "Muito superior"
]

STATUS_AGENDAMENTO = [
    "Agendado", 
    "Confirmado", 
    "Em andamento", 
    "Concluído", 
    "Cancelado", 
    "Faltou"
]

CORES_STATUS = {
    "Agendado": "#E3F2FD",
    "Confirmado": "#DCEDC8",
    "Em andamento": "#FFF9C4",
    "Concluído": "#C8E6C9",
    "Cancelado": "#FFCDD2",
    "Faltou": "#FFCCBC"
}

# Funções de dados simulados (para demonstração)
def gerar_dados_demonstracao():
    # Criar diretório de dados
    os.makedirs("dados", exist_ok=True)
    
    # Dados de pacientes
    pacientes = []
    for i in range(5):
        pacientes.append({
            'id': str(uuid.uuid4()),
            'nome': f"Paciente Teste {i+1}",
            'data_nascimento': (datetime.now() - timedelta(days=365*10 - i*500)).strftime('%Y-%m-%d'),
            'responsavel': f"Responsável {i+1}",
            'telefone': f"(11) 9999-888{i}",
            'email': f"paciente{i+1}@teste.com",
            'data_entrada': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
            'diagnostico': "TEA" if i % 2 == 0 else "TDAH",
            'nivel_suporte': "Nível 1" if i < 3 else "Nível 2",
            'preferencias': f"Preferências do paciente {i+1}",
            'coisas_acalmam': f"Coisas que acalmam {i+1}",
            'nao_gosta': f"Coisas que não gosta {i+1}",
            'gatilhos': f"Gatilhos do paciente {i+1}",
            'brinquedos_favoritos': f"Brinquedos favoritos {i+1}"
        })
    
    # Dados de atendimentos
    atendimentos = []
    for i in range(15):
        paciente_idx = i % 5
        atendimentos.append({
            'id': str(uuid.uuid4()),
            'paciente_id': pacientes[paciente_idx]['id'],
            'data': (datetime.now() - timedelta(days=i*3)).strftime('%Y-%m-%d'),
            'terapeuta': "Terapeuta Demo",
            'habilidades_trabalhadas': "Equilíbrio estático, Coordenação motora fina",
            'descricao': f"Descrição do atendimento {i+1}",
            'evolucao': f"Evolução observada no atendimento {i+1}",
            'comportamentos': f"Comportamentos do atendimento {i+1}"
        })
    
    # Dados de avaliações
    avaliacoes = []
    for i in range(5):
        paciente_idx = i % 5
        avaliacoes.append({
            'id': str(uuid.uuid4()),
            'paciente_id': pacientes[paciente_idx]['id'],
            'data': (datetime.now() - timedelta(days=i*15)).strftime('%Y-%m-%d'),
            'tipo_avaliacao': TIPOS_AVALIACAO[i % len(TIPOS_AVALIACAO)],
            'terapeuta': "Avaliador Demo",
            'resultados': f"Resultados da avaliação {i+1}",
            'recomendacoes': f"Recomendações da avaliação {i+1}",
            'proxima_avaliacao': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'areas_avaliadas': json.dumps({"Equilíbrio estático": "Normal médio", "Coordenação motora fina": "Normal baixo"}),
            'pontuacao': json.dumps({"Equilíbrio estático": 4, "Coordenação motora fina": 3})
        })
    
    # Dados de agendamentos
    agendamentos = []
    for i in range(10):
        paciente_idx = i % 5
        agendamentos.append({
            'id': str(uuid.uuid4()),
            'paciente_id': pacientes[paciente_idx]['id'],
            'data': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
            'horario': f"{8 + i%8}:00",
            'terapeuta': "Terapeuta Demo",
            'status': STATUS_AGENDAMENTO[i % len(STATUS_AGENDAMENTO)],
            'observacao': f"Observação do agendamento {i+1}"
        })
    
    return pacientes, atendimentos, avaliacoes, agendamentos

# Simplificação: Usar dados simulados para demonstração
def carregar_dados():
    """Carrega os dados para o aplicativo (simplificado para demonstração)"""
    # Criar dados simulados para demonstração
    pacientes, atendimentos, avaliacoes, agendamentos = gerar_dados_demonstracao()
    
    # Converter para DataFrames
    pacientes_df = pd.DataFrame(pacientes)
    atendimentos_df = pd.DataFrame(atendimentos)
    avaliacoes_df = pd.DataFrame(avaliacoes)
    agendamentos_df = pd.DataFrame(agendamentos)
    
    return pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df

# Função de autenticação simplificada
def fazer_login(email, senha):
    """Verifica as credenciais de login (simplificado para demonstração)"""
    usuarios = {
        "admin@neurobase.com": {
            "senha": "admin",
            "nome": "Administrador",
            "perfil": "admin"
        },
        "terapeuta@neurobase.com": {
            "senha": "terapeuta",
            "nome": "Terapeuta",
            "perfil": "terapeuta"
        }
    }
    
    if email in usuarios and usuarios[email]["senha"] == senha:
        return True, usuarios[email]
    
    return False, None

# Componentes de interface
def mostrar_dashboard(pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df):
    """Exibe o dashboard principal"""
    st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(label="Total Pacientes", value=len(pacientes_df))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        hoje = datetime.now().strftime('%Y-%m-%d')
        atendimentos_hoje = len(atendimentos_df[atendimentos_df['data'] == hoje])
        st.metric(label="Atendimentos Hoje", value=atendimentos_hoje)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        proximas_avaliacoes = len(avaliacoes_df)
        st.metric(label="Avaliações Pendentes", value=proximas_avaliacoes)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        agendamentos_pendentes = len(agendamentos_df[agendamentos_df['status'].isin(['Agendado', 'Confirmado'])])
        st.metric(label="Agendamentos Pendentes", value=agendamentos_pendentes)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Agenda do dia
    st.markdown("<h2 class='sub-header'>Agenda do Dia</h2>", unsafe_allow_html=True)
    
    # Tabela de agendamentos do dia
    hoje = datetime.now().strftime('%Y-%m-%d')
    agendamentos_hoje = agendamentos_df[agendamentos_df['data'] == hoje]
    
    if len(agendamentos_hoje) > 0:
        # Juntar com nomes dos pacientes
        agendamentos_hoje = pd.merge(
            agendamentos_hoje,
            pacientes_df[['id', 'nome']],
            left_on='paciente_id',
            right_on='id',
            how='left',
            suffixes=('', '_paciente')
        )
        
        for i, agendamento in agendamentos_hoje.iterrows():
            cor_status = CORES_STATUS.get(agendamento['status'], "#ECEFF1")
            
            st.markdown(
                f"<div style='background-color:{cor_status}; padding:10px; margin:5px; border-radius:5px;'>",
                unsafe_allow_html=True
            )
            
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**{agendamento['horario']}**")
            
            with col2:
                nome_paciente = agendamento['nome'] if 'nome' in agendamento else "Paciente não encontrado"
                st.markdown(f"**{nome_paciente}**")
                st.markdown(f"Terapeuta: {agendamento['terapeuta']}")
            
            with col3:
                st.markdown(f"**Status:** {agendamento['status']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Não há agendamentos para hoje.")

def mostrar_pacientes(pacientes_df):
    """Exibe a lista de pacientes"""
    st.markdown("<h1 class='main-header'>Pacientes</h1>", unsafe_allow_html=True)
    
    # Filtro por nome
    filtro_nome = st.text_input("Buscar por nome:")
    
    # Aplicar filtro
    pacientes_filtrados = pacientes_df
    if filtro_nome:
        pacientes_filtrados = pacientes_filtrados[pacientes_filtrados['nome'].str.contains(filtro_nome, case=False, na=False)]
    
    # Exibir lista de pacientes
    if len(pacientes_filtrados) > 0:
        for i, paciente in pacientes_filtrados.iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image("https://via.placeholder.com/100x100.png?text=Foto", width=100)
            
            with col2:
                st.subheader(paciente['nome'])
                
                # Calcular idade
                if 'data_nascimento' in paciente and paciente['data_nascimento']:
                    try:
                        data_nasc = datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                        idade = (datetime.now() - data_nasc).days // 365
                        st.write(f"Idade: {idade} anos")
                    except:
                        st.write("Data de nascimento não disponível")
                
                st.write(f"Diagnóstico: {paciente['diagnostico']}")
                st.write(f"Nível de Suporte: {paciente['nivel_suporte']}")
            
            with st.expander("Ver detalhes"):
                st.markdown("### Informações pessoais")
                st.write(f"Responsável: {paciente['responsavel']}")
                st.write(f"Contato: {paciente['telefone']}")
                st.write(f"E-mail: {paciente['email']}")
                
                st.markdown("### Preferências")
                st.write(f"**Gosta de:** {paciente['preferencias']}")
                st.write(f"**Não gosta de:** {paciente['nao_gosta']}")
                st.write(f"**O que o acalma:** {paciente['coisas_acalmam']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum paciente encontrado com esse nome.")

def mostrar_atendimentos(atendimentos_df, pacientes_df):
    """Exibe os atendimentos"""
    st.markdown("<h1 class='main-header'>Atendimentos</h1>", unsafe_allow_html=True)
    
    # Filtro por paciente
    paciente_id = st.selectbox(
        "Filtrar por paciente:",
        options=["Todos"] + pacientes_df['id'].tolist(),
        format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado"
    )
    
    # Aplicar filtro
    atendimentos_filtrados = atendimentos_df
    if paciente_id != "Todos":
        atendimentos_filtrados = atendimentos_filtrados[atendimentos_filtrados['paciente_id'] == paciente_id]
    
    # Ordenar por data (mais recente primeiro)
    atendimentos_filtrados = atendimentos_filtrados.sort_values('data', ascending=False)
    
    # Exibir atendimentos
    if len(atendimentos_filtrados) > 0:
        # Juntar com nomes dos pacientes
        atendimentos_completos = pd.merge(
            atendimentos_filtrados,
            pacientes_df[['id', 'nome']],
            left_on='paciente_id',
            right_on='id',
            how='left',
            suffixes=('', '_paciente')
        )
        
        for i, atendimento in atendimentos_completos.iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Data:** {atendimento['data']}")
            
            with col2:
                nome_paciente = atendimento['nome'] if 'nome' in atendimento else "Paciente não encontrado"
                st.markdown(f"**Paciente:** {nome_paciente}")
                st.markdown(f"**Terapeuta:** {atendimento['terapeuta']}")
                
                # Habilidades trabalhadas
                st.markdown("**Habilidades trabalhadas:**")
                if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas']:
                    habs = atendimento['habilidades_trabalhadas'].split(',')
                    for hab in habs:
                        st.markdown(f"<span class='skill-tag'>{hab.strip()}</span>", unsafe_allow_html=True)
            
            with st.expander("Ver detalhes"):
                st.markdown("**Descrição:**")
                st.write(atendimento['descricao'])
                
                st.markdown("**Evolução:**")
                st.write(atendimento['evolucao'])
                
                if 'comportamentos' in atendimento and atendimento['comportamentos']:
                    st.markdown("**Comportamentos:**")
                    st.write(atendimento['comportamentos'])
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum atendimento encontrado com os filtros selecionados.")

def mostrar_avaliacoes(avaliacoes_df, pacientes_df):
    """Exibe as avaliações"""
    st.markdown("<h1 class='main-header'>Avaliações</h1>", unsafe_allow_html=True)
    
    # Filtro por paciente
    paciente_id = st.selectbox(
        "Filtrar por paciente:",
        options=["Todos"] + pacientes_df['id'].tolist(),
        format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
        key="filtro_avaliacoes"
    )
    
    # Aplicar filtro
    avaliacoes_filtradas = avaliacoes_df
    if paciente_id != "Todos":
        avaliacoes_filtradas = avaliacoes_filtradas[avaliacoes_filtradas['paciente_id'] == paciente_id]
    
    # Ordenar por data (mais recente primeiro)
    avaliacoes_filtradas = avaliacoes_filtradas.sort_values('data', ascending=False)
    
    # Exibir avaliações
    if len(avaliacoes_filtradas) > 0:
        # Juntar com nomes dos pacientes
        avaliacoes_completas = pd.merge(
            avaliacoes_filtradas,
            pacientes_df[['id', 'nome']],
            left_on='paciente_id',
            right_on='id',
            how='left',
            suffixes=('', '_paciente')
        )
        
        for i, avaliacao in avaliacoes_completas.iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Data:** {avaliacao['data']}")
                st.markdown(f"**Tipo:** {avaliacao['tipo_avaliacao']}")
            
            with col2:
                nome_paciente = avaliacao['nome'] if 'nome' in avaliacao else "Paciente não encontrado"
                st.markdown(f"**Paciente:** {nome_paciente}")
                st.markdown(f"**Avaliador:** {avaliacao['terapeuta']}")
                
                if 'proxima_avaliacao' in avaliacao and avaliacao['proxima_avaliacao']:
                    st.markdown(f"**Próxima avaliação:** {avaliacao['proxima_avaliacao']}")
            
            with st.expander("Ver resultados"):
                # Áreas avaliadas
                if 'areas_avaliadas' in avaliacao and avaliacao['areas_avaliadas']:
                    st.markdown("### Áreas Avaliadas")
                    try:
                        areas = json.loads(avaliacao['areas_avaliadas'])
                        for area, nivel in areas.items():
                            st.markdown(f"- **{area}:** {nivel}")
                    except:
                        st.write("Erro ao carregar áreas avaliadas")
                
                st.markdown("### Resultados")
                st.write(avaliacao['resultados'])
                
                st.markdown("### Recomendações")
                st.write(avaliacao['recomendacoes'])
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhuma avaliação encontrada com os filtros selecionados.")

def mostrar_agendamentos(agendamentos_df, pacientes_df):
    """Exibe os agendamentos"""
    st.markdown("<h1 class='main-header'>Agendamentos</h1>", unsafe_allow_html=True)
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        data_filtro = st.date_input("Filtrar por data:", value=datetime.now())
    
    with col2:
        paciente_id = st.selectbox(
            "Filtrar por paciente:",
            options=["Todos"] + pacientes_df['id'].tolist(),
            format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
            key="filtro_agendamentos"
        )
    
    # Aplicar filtros
    agendamentos_filtrados = agendamentos_df
    
    # Filtro por data
    agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['data'] == data_filtro.strftime('%Y-%m-%d')]
    
    # Filtro por paciente
    if paciente_id != "Todos":
        agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['paciente_id'] == paciente_id]
    
    # Ordenar por horário
    agendamentos_filtrados = agendamentos_filtrados.sort_values('horario')
    
    # Exibir agendamentos
    if len(agendamentos_filtrados) > 0:
        # Juntar com nomes dos pacientes
        agendamentos_completos = pd.merge(
            agendamentos_filtrados,
            pacientes_df[['id', 'nome']],
            left_on='paciente_id',
            right_on='id',
            how='left',
            suffixes=('', '_paciente')
        )
        
        for i, agendamento in agendamentos_completos.iterrows():
            cor_status = CORES_STATUS.get(agendamento['status'], "#ECEFF1")
            
            st.markdown(
                f"<div style='background-color:{cor_status}; padding:10px; margin:5px; border-radius:5px;'>",
                unsafe_allow_html=True
            )
            
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"**{agendamento['horario']}**")
            
            with col2:
                nome_paciente = agendamento['nome'] if 'nome' in agendamento else "Paciente não encontrado"
                st.markdown(f"**{nome_paciente}**")
                st.markdown(f"Terapeuta: {agendamento['terapeuta']}")
                
                if 'observacao' in agendamento and agendamento['observacao']:
                    st.markdown(f"Obs: {agendamento['observacao']}")
            
            with col3:
                st.markdown(f"**Status:** {agendamento['status']}")
                
                # Menu de status (simulado)
                novo_status = st.selectbox(
                    "Alterar status:",
                    options=STATUS_AGENDAMENTO,
                    index=STATUS_AGENDAMENTO.index(agendamento['status']),
                    key=f"status_{agendamento['id']}"
                )
                
                if novo_status != agendamento['status']:
                    if st.button("Salvar", key=f"salvar_{agendamento['id']}"):
                        st.success(f"Status alterado para: {novo_status}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum agendamento encontrado para a data selecionada.")

def mostrar_relatorios(pacientes_df, atendimentos_df, avaliacoes_df):
    """Exibe a seção de relatórios"""
    st.markdown("<h1 class='main-header'>Relatórios</h1>", unsafe_allow_html=True)
    
    # Selecionar paciente
    paciente_id = st.selectbox(
        "Selecione o paciente:",
        options=pacientes_df['id'].tolist(),
        format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado"
    )
    
    # Selecionar período
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input("Data inicial:", value=datetime.now() - timedelta(days=30))
    
    with col2:
        data_fim = st.date_input("Data final:", value=datetime.now())
    
    # Opções do relatório
    opcoes_relatorio = st.multiselect(
        "Incluir no relatório:",
        options=["Dados pessoais", "Resumo de atendimentos", "Avaliações", "Habilidades trabalhadas", "Gráficos de evolução"],
        default=["Dados pessoais", "Resumo de atendimentos", "Habilidades trabalhadas"]
    )
    
    # Gerar relatório
    if st.button("Gerar Relatório"):
        # Buscar dados do paciente
        paciente = pacientes_df[pacientes_df['id'] == paciente_id].iloc[0]
        
        # Filtrar atendimentos do período
        atendimentos_periodo = atendimentos_df[
            (atendimentos_df['paciente_id'] == paciente_id) &
            (atendimentos_df['data'] >= data_inicio.strftime('%Y-%m-%d')) &
            (atendimentos_df['data'] <= data_fim.strftime('%Y-%m-%d'))
        ]
        
        # Criar relatório
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>Relatório de {paciente['nome']}</h2>", unsafe_allow_html=True)
        st.markdown(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        if "Dados pessoais" in opcoes_relatorio:
            st.markdown("### Dados Pessoais")
            st.markdown(f"**Nome:** {paciente['nome']}")
            
            # Calcular idade
            if 'data_nascimento' in paciente and paciente['data_nascimento']:
                try:
                    data_nasc = datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                    idade = (datetime.now() - data_nasc).days // 365
                    st.markdown(f"**Idade:** {idade} anos")
                except:
                    pass
            
            st.markdown(f"**Diagnóstico:** {paciente['diagnostico']}")
            st.markdown(f"**Nível de Suporte:** {paciente['nivel_suporte']}")
        
        if "Resumo de atendimentos" in opcoes_relatorio:
            st.markdown("### Resumo de Atendimentos")
            st.markdown(f"Total de atendimentos no período: {len(atendimentos_periodo)}")
            
            if len(atendimentos_periodo) > 0:
                for i, atendimento in atendimentos_periodo.iterrows():
                    st.markdown(f"#### Sessão do dia {atendimento['data']}")
                    st.markdown(f"Terapeuta: {atendimento['terapeuta']}")
                    st.markdown(f"Evolução: {atendimento['evolucao']}")
        
        if "Habilidades trabalhadas" in opcoes_relatorio and len(atendimentos_periodo) > 0:
            st.markdown("### Habilidades Trabalhadas")
            
            # Contar frequência de habilidades
            habilidades_contagem = {}
            
            for i, atendimento in atendimentos_periodo.iterrows():
                if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas']:
                    habilidades = [h.strip() for h in atendimento['habilidades_trabalhadas'].split(',')]
                    
                    for hab in habilidades:
                        if hab in habilidades_contagem:
                            habilidades_contagem[hab] += 1
                        else:
                            habilidades_contagem[hab] = 1
            
            # Criar gráfico de habilidades
            if habilidades_contagem:
                # Ordenar por frequência
                habilidades_ordenadas = sorted(habilidades_contagem.items(), key=lambda x: x[1], reverse=True)
                
                # Criar gráfico
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Limitar para 10 primeiras
                top_habilidades = habilidades_ordenadas[:10]
                habs, frequencias = zip(*top_habilidades)
                
                ax.barh(habs, frequencias, color='purple')
                ax.set_xlabel('Número de Sessões')
                ax.set_title('Habilidades Mais Trabalhadas no Período')
                plt.tight_layout()
                st.pyplot(fig)
        
        if "Avaliações" in opcoes_relatorio:
            st.markdown("### Avaliações no Período")
            
            # Filtrar avaliações do período
            avaliacoes_periodo = avaliacoes_df[
                (avaliacoes_df['paciente_id'] == paciente_id) &
                (avaliacoes_df['data'] >= data_inicio.strftime('%Y-%m-%d')) &
                (avaliacoes_df['data'] <= data_fim.strftime('%Y-%m-%d'))
            ]
            
            if len(avaliacoes_periodo) > 0:
                for i, avaliacao in avaliacoes_periodo.iterrows():
                    st.markdown(f"#### {avaliacao['data']} - {avaliacao['tipo_avaliacao']}")
                    st.markdown(f"Avaliador: {avaliacao['terapeuta']}")
                    st.markdown(f"Resultados: {avaliacao['resultados']}")
                    st.markdown(f"Recomendações: {avaliacao['recomendacoes']}")
            else:
                st.info("Não foram realizadas avaliações no período selecionado.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Botões de exportação (simulados)
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "Exportar como PDF",
                data="Simulação de PDF",
                file_name=f"Relatorio_{paciente['nome']}.pdf",
                mime="application/pdf"
            )
        
        with col2:
            st.download_button(
                "Exportar como DOCX",
                data="Simulação de DOCX",
                file_name=f"Relatorio_{paciente['nome']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

def pagina_login():
    """Exibe a página de login"""
    st.markdown("<h1 class='main-header'>NeuroBase - Sistema de Gestão em Psicomotricidade</h1>", unsafe_allow_html=True)
    
    # Layout centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Login")
        
        # Formulário de login
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            if email and senha:
                sucesso, usuario = fazer_login(email, senha)
                
                if sucesso:
                    # Armazenar informações do usuário na sessão
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario["nome"]
                    st.session_state.perfil = usuario["perfil"]
                    st.session_state.email = email
                    
                    st.success(f"Bem-vindo, {usuario['nome']}!")
                    # Redirecionamento será feito pelo loop principal
                else:
                    st.error("E-mail ou senha incorretos")
            else:
                st.error("Por favor, preencha todos os campos")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Informações de login para demonstração
        st.markdown("### Credenciais para demonstração:")
        st.markdown("**Administrador**:  \nE-mail: admin@neurobase.com  \nSenha: admin")
        st.markdown("**Terapeuta**:  \nE-mail: terapeuta@neurobase.com  \nSenha: terapeuta")
    
    # Rodapé
    st.markdown("<div class='version-info'>NeuroBase v" + APP_VERSION + "</div>", unsafe_allow_html=True)

def main():
    """Função principal do aplicativo"""
    # Inicializar estado da sessão se necessário
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    # Verificar autenticação
    if not st.session_state.autenticado:
        pagina_login()
        return
    
    # Se chegou aqui, está autenticado
    # Carregar dados
    pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df = carregar_dados()
    
    # Barra lateral para navegação
    st.sidebar.markdown(f"### Bem-vindo, {st.session_state.usuario}!")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Pacientes", "Atendimentos", "Avaliações", "Agendamentos", "Relatórios"]
    )
    
    st.sidebar.markdown("---")
    
    # Botão de logout
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.perfil = None
        st.session_state.email = None
        st.success("Logout realizado com sucesso!")
        st.stop()
    
    # Exibir página selecionada
    if menu == "Dashboard":
        mostrar_dashboard(pacientes_df, atendimentos_df, avaliacoes_df, agendamentos_df)
    elif menu == "Pacientes":
        mostrar_pacientes(pacientes_df)
    elif menu == "Atendimentos":
        mostrar_atendimentos(atendimentos_df, pacientes_df)
    elif menu == "Avaliações":
        mostrar_avaliacoes(avaliacoes_df, pacientes_df)
    elif menu == "Agendamentos":
        mostrar_agendamentos(agendamentos_df, pacientes_df)
    elif menu == "Relatórios":
        mostrar_relatorios(pacientes_df, atendimentos_df, avaliacoes_df)

# Executar o aplicativo
if __name__ == "__main__":
    main()
