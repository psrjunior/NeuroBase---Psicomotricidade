import streamlit as st
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
