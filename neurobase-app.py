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

# Níveis de desenvolvimento (para avaliações)
NIVEIS_DESENVOLVIMENTO = [
    "Muito inferior",
    "Inferior",
    "Normal baixo",
    "Normal médio",
    "Normal alto",
    "Superior",
    "Muito superior"
]

# Status de agendamento
STATUS_AGENDAMENTO = [
    "Agendado", 
    "Confirmado", 
    "Em andamento", 
    "Concluído", 
    "Cancelado", 
    "Faltou"
]

# Cores para status
CORES_STATUS = {
    "Agendado": "#E3F2FD",
    "Confirmado": "#DCEDC8",
    "Em andamento": "#FFF9C4",
    "Concluído": "#C8E6C9",
    "Cancelado": "#FFCDD2",
    "Faltou": "#FFCCBC"
}

###############################
# FUNÇÕES DO BANCO DE DADOS
###############################

def inicializar_banco_dados():
    """Inicializa o banco de dados SQLite se não existir"""
    
    # Criar diretório de dados se não existir
    os.makedirs("dados", exist_ok=True)
    
    # Conectar ao banco de dados (ou criar se não existir)
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Criar tabela de pacientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        data_nascimento TEXT,
        responsavel TEXT,
        telefone TEXT,
        email TEXT,
        data_entrada TEXT,
        diagnostico TEXT,
        nivel_suporte TEXT,
        foto TEXT,
        preferencias TEXT,
        coisas_acalmam TEXT,
        nao_gosta TEXT,
        gatilhos TEXT,
        brinquedos_favoritos TEXT,
        data_cadastro TEXT,
        ultima_atualizacao TEXT
    )
    ''')
    
    # Criar tabela de atendimentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS atendimentos (
        id TEXT PRIMARY KEY,
        paciente_id TEXT NOT NULL,
        data TEXT NOT NULL,
        terapeuta TEXT NOT NULL,
        habilidades_trabalhadas TEXT,
        descricao TEXT,
        evolucao TEXT,
        comportamentos TEXT,
        data_registro TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    # Criar tabela de avaliações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id TEXT PRIMARY KEY,
        paciente_id TEXT NOT NULL,
        data TEXT NOT NULL,
        tipo_avaliacao TEXT,
        terapeuta TEXT,
        resultados TEXT,
        recomendacoes TEXT,
        proxima_avaliacao TEXT,
        areas_avaliadas TEXT,
        pontuacao TEXT,
        data_registro TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    # Criar tabela de agendamentos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agendamentos (
        id TEXT PRIMARY KEY,
        paciente_id TEXT NOT NULL,
        data TEXT NOT NULL,
        horario TEXT NOT NULL,
        terapeuta TEXT NOT NULL,
        status TEXT,
        observacao TEXT,
        data_registro TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
    )
    ''')
    
    # Criar tabela de logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        usuario TEXT,
        acao TEXT NOT NULL,
        tabela TEXT NOT NULL,
        registro_id TEXT,
        detalhes TEXT
    )
    ''')
    
    # Criar tabela de backup
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        usuario TEXT,
        arquivo TEXT,
        detalhes TEXT
    )
    ''')

    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL,
        ativo INTEGER NOT NULL DEFAULT 1,
        data_cadastro TEXT,
        ultimo_acesso TEXT
    )
    ''')
    
    # Criar usuários padrão se não existirem
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Criar usuário admin
        admin_id = str(uuid.uuid4())
        senha_admin = hashlib.sha256("admin".encode()).hexdigest()
        cursor.execute('''
        INSERT INTO usuarios (id, nome, email, senha_hash, perfil, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (admin_id, "Administrador", "admin@neurobase.com", senha_admin, "admin", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Criar usuário terapeuta
        terapeuta_id = str(uuid.uuid4())
        senha_terapeuta = hashlib.sha256("terapeuta".encode()).hexdigest()
        cursor.execute('''
        INSERT INTO usuarios (id, nome, email, senha_hash, perfil, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (terapeuta_id, "Terapeuta", "terapeuta@neurobase.com", senha_terapeuta, "terapeuta", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # Fazer commit das alterações e fechar conexão
    conn.commit()
    conn.close()
    
    return True

def registrar_log(usuario, acao, tabela, registro_id, detalhes=None):
    """Registra uma ação no log do sistema"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    log_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
    INSERT INTO logs (id, timestamp, usuario, acao, tabela, registro_id, detalhes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (log_id, timestamp, usuario, acao, tabela, registro_id, detalhes))
    
    conn.commit()
    conn.close()
    
    return True

def carregar_pacientes():
    """Carrega todos os pacientes do banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    pacientes_df = pd.read_sql("SELECT * FROM pacientes", conn)
    conn.close()
    return pacientes_df

def carregar_atendimentos():
    """Carrega todos os atendimentos do banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    atendimentos_df = pd.read_sql("SELECT * FROM atendimentos", conn)
    conn.close()
    return atendimentos_df

def carregar_avaliacoes():
    """Carrega todas as avaliações do banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    avaliacoes_df = pd.read_sql("SELECT * FROM avaliacoes", conn)
    conn.close()
    return avaliacoes_df

def carregar_agendamentos():
    """Carrega todos os agendamentos do banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    agendamentos_df = pd.read_sql("SELECT * FROM agendamentos", conn)
    conn.close()
    return agendamentos_df

def inserir_paciente(dados_paciente):
    """Insere um novo paciente no banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Gerar ID único
    paciente_id = str(uuid.uuid4())
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Preparar consulta
    campos = ', '.join(dados_paciente.keys()) + ', id, data_cadastro, ultima_atualizacao'
    placeholders = ', '.join(['?'] * len(dados_paciente)) + ', ?, ?, ?'
    
    # Executar consulta
    query = f"INSERT INTO pacientes ({campos}) VALUES ({placeholders})"
    valores = list(dados_paciente.values()) + [paciente_id, agora, agora]
    
    cursor.execute(query, valores)
    conn.commit()
    
    # Registrar log
    usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
    registrar_log(usuario, 'Inserir', 'pacientes', paciente_id, f"Novo paciente: {dados_paciente['nome']}")
    
    conn.close()
    
    return paciente_id

def inserir_atendimento(dados_atendimento):
    """Insere um novo atendimento no banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Gerar ID único
    atendimento_id = str(uuid.uuid4())
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Adicionar campos adicionais
    dados_completos = dados_atendimento.copy()
    dados_completos['id'] = atendimento_id
    dados_completos['data_registro'] = agora
    
    # Preparar consulta
    campos = ', '.join(dados_completos.keys())
    placeholders = ', '.join(['?'] * len(dados_completos))
    
    # Executar consulta
    query = f"INSERT INTO atendimentos ({campos}) VALUES ({placeholders})"
    valores = list(dados_completos.values())
    
    cursor.execute(query, valores)
    conn.commit()
    
    # Registrar log
    usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
    registrar_log(usuario, 'Inserir', 'atendimentos', atendimento_id, f"Novo atendimento: Paciente {dados_atendimento['paciente_id']}")
    
    conn.close()
    
    return atendimento_id

def inserir_avaliacao(dados_avaliacao):
    """Insere uma nova avaliação no banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Gerar ID único
    avaliacao_id = str(uuid.uuid4())
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Adicionar campos adicionais
    dados_completos = dados_avaliacao.copy()
    dados_completos['id'] = avaliacao_id
    dados_completos['data_registro'] = agora
    
    # Preparar consulta
    campos = ', '.join(dados_completos.keys())
    placeholders = ', '.join(['?'] * len(dados_completos))
    
    # Executar consulta
    query = f"INSERT INTO avaliacoes ({campos}) VALUES ({placeholders})"
    valores = list(dados_completos.values())
    
    cursor.execute(query, valores)
    conn.commit()
    
    # Registrar log
    usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
    registrar_log(usuario, 'Inserir', 'avaliacoes', avaliacao_id, f"Nova avaliação: Paciente {dados_avaliacao['paciente_id']}")
    
    conn.close()
    
    return avaliacao_id

def inserir_agendamento(dados_agendamento):
    """Insere um novo agendamento no banco de dados"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Gerar ID único
    agendamento_id = str(uuid.uuid4())
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Adicionar campos adicionais
    dados_completos = dados_agendamento.copy()
    dados_completos['id'] = agendamento_id
    dados_completos['data_registro'] = agora
    
    # Preparar consulta
    campos = ', '.join(dados_completos.keys())
    placeholders = ', '.join(['?'] * len(dados_completos))
    
    # Executar consulta
    query = f"INSERT INTO agendamentos ({campos}) VALUES ({placeholders})"
    valores = list(dados_completos.values())
    
    cursor.execute(query, valores)
    conn.commit()
    
    # Registrar log
    usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
    registrar_log(usuario, 'Inserir', 'agendamentos', agendamento_id, f"Novo agendamento: Paciente {dados_agendamento['paciente_id']}")
    
    conn.close()
    
    return agendamento_id

def atualizar_agendamento(agendamento_id, dados_atualizados):
    """Atualiza um agendamento existente"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Preparar consulta de atualização
    set_clause = ', '.join([f"{campo} = ?" for campo in dados_atualizados.keys()])
    query = f"UPDATE agendamentos SET {set_clause} WHERE id = ?"
    
    # Executar consulta
    valores = list(dados_atualizados.values()) + [agendamento_id]
    cursor.execute(query, valores)
    conn.commit()
    
    # Registrar log
    usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
    registrar_log(usuario, 'Atualizar', 'agendamentos', agendamento_id, f"Atualização de agendamento: {', '.join(dados_atualizados.keys())}")
    
    conn.close()
    
    return True

def backup_banco_dados():
    """Cria um backup do banco de dados"""
    import shutil
    import time
    
    # Criar diretório de backup se não existir
    os.makedirs("dados/backup", exist_ok=True)
    
    # Nome do arquivo de backup
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_file = f"dados/backup/neurobase_{timestamp}.db"
    
    # Fazer cópia do banco de dados
    try:
        shutil.copy2('dados/neurobase.db', backup_file)
        
        # Registrar backup no banco
        conn = sqlite3.connect('dados/neurobase.db')
        cursor = conn.cursor()
        
        backup_id = str(uuid.uuid4())
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        usuario = st.session_state.usuario if 'usuario' in st.session_state else 'Sistema'
        
        cursor.execute('''
        INSERT INTO backups (id, timestamp, usuario, arquivo, detalhes)
        VALUES (?, ?, ?, ?, ?)
        ''', (backup_id, agora, usuario, backup_file, "Backup automático"))
        
        conn.commit()
        conn.close()
        
        return True, backup_file
    except Exception as e:
        return False, str(e)

def migrar_dados_csv_para_sqlite():
    """Migra dados de arquivos CSV para o banco SQLite (se necessário)"""
    # Verificar se arquivos CSV existem
    pacientes_file = "dados/pacientes.csv"
    atendimentos_file = "dados/atendimentos.csv"
    avaliacoes_file = "dados/avaliacoes.csv"
    agendamentos_file = "dados/agendamentos.csv"
    
    arquivos = [
        (pacientes_file, "pacientes"), 
        (atendimentos_file, "atendimentos"),
        (avaliacoes_file, "avaliacoes"),
        (agendamentos_file, "agendamentos")
    ]
    
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    for arquivo, tabela in arquivos:
        if os.path.exists(arquivo):
            try:
                # Carregar dados do CSV
                df = pd.read_csv(arquivo)
                
                # Verificar se a tabela já tem dados
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                
                if count == 0 and len(df) > 0:
                    # Adicionar ID UUID se não existir
                    if 'id' in df.columns and not isinstance(df['id'].iloc[0], str):
                        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                    
                    # Adicionar campos de data se necessário
                    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if tabela == "pacientes":
                        if 'data_cadastro' not in df.columns:
                            df['data_cadastro'] = agora
                        if 'ultima_atualizacao' not in df.columns:
                            df['ultima_atualizacao'] = agora
                    else:
                        if 'data_registro' not in df.columns:
                            df['data_registro'] = agora
                    
                    # Inserir dados na tabela SQLite
                    for _, row in df.iterrows():
                        # Limpar NaN
                        row_dict = {k: ('' if pd.isna(v) else v) for k, v in row.to_dict().items()}
                        
                        campos = ', '.join(row_dict.keys())
                        placeholders = ', '.join(['?'] * len(row_dict))
                        valores = list(row_dict.values())
                        
                        cursor.execute(f"INSERT INTO {tabela} ({campos}) VALUES ({placeholders})", valores)
                    
                    conn.commit()
                    print(f"Migrados {len(df)} registros de {arquivo} para a tabela {tabela}")
            except Exception as e:
                print(f"Erro ao migrar dados de {arquivo}: {str(e)}")
    
    conn.close()

def validar_dados_paciente(dados):
    """Valida os dados de um paciente antes de inserir/atualizar"""
    erros = []
    
    # Validar campos obrigatórios
    if not dados.get('nome'):
        erros.append("Nome é obrigatório")
    
    # Validar formatos
    if 'email' in dados and dados['email']:
        if '@' not in dados['email']:
            erros.append("E-mail inválido")
    
    if 'telefone' in dados and dados['telefone']:
        # Remover caracteres não numéricos para validação
        telefone_limpo = ''.join(c for c in dados['telefone'] if c.isdigit())
        if len(telefone_limpo) < 10:
            erros.append("Telefone inválido (mínimo 10 dígitos)")
    
    # Validar datas
    try:
        if 'data_nascimento' in dados and dados['data_nascimento']:
            datetime.strptime(dados['data_nascimento'], '%Y-%m-%d')
    except ValueError:
        erros.append("Data de nascimento inválida")
    
    try:
        if 'data_entrada' in dados and dados['data_entrada']:
            datetime.strptime(dados['data_entrada'], '%Y-%m-%d')
    except ValueError:
        erros.append("Data de entrada inválida")
    
    return erros

def verificar_login(email, senha):
    """Verifica as credenciais de login"""
    conn = sqlite3.connect('dados/neurobase.db')
    cursor = conn.cursor()
    
    # Codificar senha para comparação
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    # Verificar credenciais
    cursor.execute('''
    SELECT id, nome, email, perfil FROM usuarios 
    WHERE email = ? AND senha_hash = ? AND ativo = 1
    ''', (email, senha_hash))
    
    usuario = cursor.fetchone()
    
    if usuario:
        # Atualizar último acesso
        cursor.execute('''
        UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), usuario[0]))
        conn.commit()
        
        # Registrar log de login
        registrar_log(email, 'Login', 'usuarios', usuario[0], "Login bem-sucedido")
        
        usuario_dict = {
            'id': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'perfil': usuario[3]
        }
        
        conn.close()
        return True, usuario_dict
    
    conn.close()
    return False, None

def obter_dados_backup():
    """Obtém a lista de backups disponíveis"""
    conn = sqlite3.connect('dados/neurobase.db')
    backups_df = pd.read_sql('''
    SELECT id, timestamp, usuario, arquivo, detalhes FROM backups
    ORDER BY timestamp DESC
    ''', conn)
    conn.close()
    return backups_df

###############################
# FUNÇÕES DA INTERFACE
###############################

def autenticacao():
    """Interface de autenticação do sistema"""
    st.markdown("<h1 class='main-header'>NeuroBase - Sistema de Gestão em Psicomotricidade</h1>", unsafe_allow_html=True)
    
    if 'autenticado' in st.session_state and st.session_state.autenticado:
        return True
    
    # Criar colunas para centralizar o formulário de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Login")
        
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if email and senha:
                    autenticado, usuario = verificar_login(email, senha)
                    
                    if autenticado:
                        st.session_state.autenticado = True
                        st.session_state.usuario = usuario['nome']
                        st.session_state.usuario_id = usuario['id']
                        st.session_state.usuario_email = usuario['email']
                        st.session_state.perfil = usuario['perfil']
                        
                        # Mensagem de sucesso e redirecionamento
                        st.success(f"Bem-vindo, {usuario['nome']}!")
                        time.sleep(1)
                        st.experimental_rerun()
                        return True
                    else:
                        st.error("E-mail ou senha incorretos.")
                else:
                    st.error("Por favor, preencha todos os campos.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='version-info'>NeuroBase v" + APP_VERSION + "</div>", unsafe_allow_html=True)
    return False

def mostrar_dashboard():
    """Exibe o dashboard principal"""
    st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Carregar dados
    pacientes_df = carregar_pacientes()
    atendimentos_df = carregar_atendimentos()
    avaliacoes_df = carregar_avaliacoes()
    agendamentos_df = carregar_agendamentos()
    
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
        data_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        proximas_avaliacoes = len(avaliacoes_df[avaliacoes_df['proxima_avaliacao'] <= data_limite])
        st.metric(label="Avaliações Próx. 30 dias", value=proximas_avaliacoes)
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
    
    # Alertas e informações
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h2 class='sub-header'>Reavaliações Pendentes</h2>", unsafe_allow_html=True)
        
        # Identificar pacientes que precisam de reavaliação
        avaliacoes_com_proxima = avaliacoes_df[~avaliacoes_df['proxima_avaliacao'].isna()]
        avaliacoes_pendentes = avaliacoes_com_proxima[avaliacoes_com_proxima['proxima_avaliacao'] <= data_limite]
        
        if len(avaliacoes_pendentes) > 0:
            # Juntar com nomes dos pacientes
            avaliacoes_pendentes = pd.merge(
                avaliacoes_pendentes,
                pacientes_df[['id', 'nome']],
                left_on='paciente_id',
                right_on='id',
                how='left',
                suffixes=('', '_paciente')
            )
            
            for i, avaliacao in avaliacoes_pendentes.iterrows():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                nome_paciente = avaliacao['nome'] if 'nome' in avaliacao else "Paciente não encontrado"
                st.markdown(f"**{nome_paciente}** - {avaliacao['proxima_avaliacao']}")
                st.markdown(f"Tipo: {avaliacao['tipo_avaliacao']}")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Não há reavaliações pendentes nos próximos 30 dias.")
    
    with col2:
        st.markdown("<h2 class='sub-header'>Estatísticas de Atendimentos</h2>", unsafe_allow_html=True)
        
        # Calcular estatísticas de atendimentos dos últimos 30 dias
        data_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        atendimentos_recentes = atendimentos_df[atendimentos_df['data'] >= data_inicio]
        
        if len(atendimentos_recentes) > 0:
            # Contar habilidades trabalhadas
            habilidades_count = {}
            
            for _, atendimento in atendimentos_recentes.iterrows():
                if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas']:
                    habilidades = [h.strip() for h in str(atendimento['habilidades_trabalhadas']).split(',') if h.strip()]
                    for hab in habilidades:
                        if hab in habilidades_count:
                            habilidades_count[hab] += 1
                        else:
                            habilidades_count[hab] = 1
            
            # Mostrar as 5 habilidades mais trabalhadas
            if habilidades_count:
                habilidades_sorted = sorted(habilidades_count.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # Criar gráfico
                fig, ax = plt.subplots(figsize=(10, 4))
                habs, counts = zip(*habilidades_sorted)
                ax.barh(habs, counts, color='purple')
                ax.set_xlabel('Número de Sessões')
                ax.set_title('Habilidades Mais Trabalhadas (30 dias)')
                st.pyplot(fig)
            else:
                st.info("Não há dados suficientes para análise de habilidades.")
        else:
            st.info("Não há atendimentos registrados nos últimos 30 dias.")

def mostrar_pacientes():
    """Exibe a seção de gerenciamento de pacientes"""
    st.markdown("<h1 class='main-header'>Pacientes</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Lista de Pacientes", "Cadastrar Novo Paciente", "Ficha do Paciente"])
    
    # Carregar dados dos pacientes
    pacientes_df = carregar_pacientes()
    
    with tabs[0]:  # Lista de Pacientes
        st.markdown("<h2 class='sub-header'>Lista de Pacientes</h2>", unsafe_allow_html=True)
        
        # Filtros de busca
        col1, col2 = st.columns(2)
        with col1:
            filtro_nome = st.text_input("Buscar por nome:", key="filtro_nome_paciente")
        
        with col2:
            filtro_diagnostico = st.text_input("Filtrar por diagnóstico:", key="filtro_diagnostico")
        
        # Aplicar filtros
        pacientes_filtrados = pacientes_df
        
        if filtro_nome:
            pacientes_filtrados = pacientes_filtrados[pacientes_filtrados['nome'].str.contains(filtro_nome, case=False, na=False)]
        
        if filtro_diagnostico:
            pacientes_filtrados = pacientes_filtrados[pacientes_filtrados['diagnostico'].str.contains(filtro_diagnostico, case=False, na=False)]
        
        # Exibir pacientes
        if len(pacientes_filtrados) > 0:
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
                    
                    if 'data_nascimento' in paciente and paciente['data_nascimento'] and str(paciente['data_nascimento']) != 'nan':
                        try:
                            data_nasc = datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                            idade = (datetime.now() - data_nasc).days // 365
                            st.write(f"Idade: {idade} anos")
                        except:
                            st.write("Data de nascimento não disponível")
                    
                    if 'diagnostico' in paciente and paciente['diagnostico'] and str(paciente['diagnostico']) != 'nan':
                        st.write(f"Diagnóstico: {paciente['diagnostico']}")
                
                with col3:
                    if st.button("Ver Ficha", key=f"ver_ficha_{paciente['id']}"):
                        st.session_state.paciente_selecionado = paciente['id']
                        st.experimental_rerun()
        else:
            st.info("Nenhum paciente encontrado com os filtros selecionados.")
    
    with tabs[1]:  # Cadastrar Novo Paciente
        st.markdown("<h2 class='sub-header'>Cadastrar Novo Paciente</h2>", unsafe_allow_html=True)
        
        with st.form("form_cadastro_paciente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome completo*")
                data_nascimento = st.date_input("Data de nascimento")
                responsavel = st.text_input("Nome do responsável")
                telefone = st.text_input("Telefone de contato")
                email = st.text_input("E-mail")
            
            with col2:
                diagnostico = st.text_input("Diagnóstico")
                nivel_suporte = st.selectbox("Nível de suporte (em caso de TEA)", 
                                           ["", "Nível 1", "Nível 2", "Nível 3"])
                data_entrada = st.date_input("Data de entrada na clínica", value=datetime.now())
                foto = st.file_uploader("Foto do paciente", type=["jpg", "jpeg", "png"])
            
            st.markdown("### Preferências e informações importantes")
            col1, col2 = st.columns(2)
            
            with col1:
                preferencias = st.text_area("Coisas que gosta")
                coisas_acalmam = st.text_area("Coisas que o acalmam")
            
            with col2:
                nao_gosta = st.text_area("Coisas que não gosta")
                gatilhos = st.text_area("Coisas que o deixam nervoso")
            
            brinquedos_favoritos = st.text_area("Brinquedos favoritos (em ordem de preferência)")
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Cadastrar Paciente")
            
            if submitted:
                # Validar dados
                dados_paciente = {
                    'nome': nome,
                    'data_nascimento': data_nascimento.strftime('%Y-%m-%d'),
                    'responsavel': responsavel,
                    'telefone': telefone,
                    'email': email,
                    'data_entrada': data_entrada.strftime('%Y-%m-%d'),
                    'diagnostico': diagnostico,
                    'nivel_suporte': nivel_suporte,
                    'preferencias': preferencias,
                    'coisas_acalmam': coisas_acalmam,
                    'nao_gosta': nao_gosta,
                    'gatilhos': gatilhos,
                    'brinquedos_favoritos': brinquedos_favoritos
                }
                
                # Processar foto
                if foto is not None:
                    foto_bytes = foto.getvalue()
                    foto_base64 = base64.b64encode(foto_bytes).decode()
                    dados_paciente['foto'] = foto_base64
                
                erros = validar_dados_paciente(dados_paciente)
                
                if erros:
                    for erro in erros:
                        st.error(erro)
                else:
                    # Inserir paciente no banco
                    paciente_id = inserir_paciente(dados_paciente)
                    
                    st.success(f"Paciente {nome} cadastrado com sucesso!")
                    time.sleep(1)
                    st.session_state.paciente_selecionado = paciente_id
                    st.experimental_rerun()
    
    with tabs[2]:  # Ficha do Paciente
        st.markdown("<h2 class='sub-header'>Ficha do Paciente</h2>", unsafe_allow_html=True)
        
        if 'paciente_selecionado' in st.session_state:
            paciente_id = st.session_state.paciente_selecionado
            
            # Buscar paciente no banco
            paciente_data = pacientes_df[pacientes_df['id'] == paciente_id]
            
            if len(paciente_data) > 0:
                paciente = paciente_data.iloc[0]
                
                st.markdown(f"<h3>{paciente['nome']}</h3>", unsafe_allow_html=True)
                
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
                    if 'data_nascimento' in paciente and paciente['data_nascimento'] and str(paciente['data_nascimento']) != 'nan':
                        try:
                            data_nasc = datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                            idade = (datetime.now() - data_nasc).days // 365
                            st.write(f"**Idade:** {idade} anos")
                        except:
                            st.write("**Data de Nascimento:** Não disponível")
                    
                    st.write(f"**Responsável:** {paciente['responsavel']}")
                    st.write(f"**Contato:** {paciente['telefone']}")
                    st.write(f"**E-mail:** {paciente['email']}")
                    st.write(f"**Data de Entrada:** {paciente['data_entrada']}")
                    st.write(f"**Diagnóstico:** {paciente['diagnostico']}")
                    if 'nivel_suporte' in paciente and paciente['nivel_suporte'] and str(paciente['nivel_suporte']) != 'nan':
                        st.write(f"**Nível de Suporte:** {paciente['nivel_suporte']}")
                
                st.markdown("---")
                st.markdown("### Preferências e Comportamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("#### 😊 Coisas que gosta")
                    if 'preferencias' in paciente and paciente['preferencias'] and str(paciente['preferencias']) != 'nan':
                        st.write(paciente['preferencias'])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("#### 😌 Coisas que o acalmam")
                    if 'coisas_acalmam' in paciente and paciente['coisas_acalmam'] and str(paciente['coisas_acalmam']) != 'nan':
                        st.write(paciente['coisas_acalmam'])
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("#### 😕 Coisas que não gosta")
                    if 'nao_gosta' in paciente and paciente['nao_gosta'] and str(paciente['nao_gosta']) != 'nan':
                        st.write(paciente['nao_gosta'])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("#### 😠 Gatilhos")
                    if 'gatilhos' in paciente and paciente['gatilhos'] and str(paciente['gatilhos']) != 'nan':
                        st.write(paciente['gatilhos'])
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 🧸 Brinquedos favoritos")
                if 'brinquedos_favoritos' in paciente and paciente['brinquedos_favoritos'] and str(paciente['brinquedos_favoritos']) != 'nan':
                    st.write(paciente['brinquedos_favoritos'])
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Carregar dados relacionados
                atendimentos_df = carregar_atendimentos()
                avaliacoes_df = carregar_avaliacoes()
                agendamentos_df = carregar_agendamentos()
                
                # Filtrar por paciente
                atendimentos_paciente = atendimentos_df[atendimentos_df['paciente_id'] == paciente_id]
                avaliacoes_paciente = avaliacoes_df[avaliacoes_df['paciente_id'] == paciente_id]
                agendamentos_paciente = agendamentos_df[agendamentos_df['paciente_id'] == paciente_id]
                
                # Abas para histórico
                paciente_tabs = st.tabs(["Atendimentos", "Avaliações", "Agendamentos"])
                
                with paciente_tabs[0]:  # Atendimentos
                    st.markdown("### Histórico de Atendimentos")
                    
                    if len(atendimentos_paciente) > 0:
                        atendimentos_paciente = atendimentos_paciente.sort_values('data', ascending=False)
                        
                        for _, atendimento in atendimentos_paciente.iterrows():
                            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"#### {atendimento['data']} - Terapeuta: {atendimento['terapeuta']}")
                            
                            st.markdown("**Habilidades trabalhadas:**")
                            if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas'] and str(atendimento['habilidades_trabalhadas']) != 'nan':
                                habilidades_list = str(atendimento['habilidades_trabalhadas']).split(',')
                                for hab in habilidades_list:
                                    st.markdown(f"<span class='skill-tag'>{hab.strip()}</span>", unsafe_allow_html=True)
                            
                            with st.expander("Ver detalhes"):
                                st.markdown("**Evolução:**")
                                if 'evolucao' in atendimento and atendimento['evolucao'] and str(atendimento['evolucao']) != 'nan':
                                    st.write(atendimento['evolucao'])
                                
                                if 'comportamentos' in atendimento and atendimento['comportamentos'] and str(atendimento['comportamentos']) != 'nan':
                                    st.markdown("**Comportamentos:**")
                                    st.write(atendimento['comportamentos'])
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("Não há registros de atendimentos para este paciente.")
                
                with paciente_tabs[1]:  # Avaliações
                    st.markdown("### Avaliações")
                    
                    if len(avaliacoes_paciente) > 0:
                        avaliacoes_paciente = avaliacoes_paciente.sort_values('data', ascending=False)
                        
                        for _, avaliacao in avaliacoes_paciente.iterrows():
                            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"#### {avaliacao['data']} - {avaliacao['tipo_avaliacao']}")
                            st.markdown(f"Terapeuta: {avaliacao['terapeuta']}")
                            
                            with st.expander("Ver resultados"):
                                st.markdown("**Resultados:**")
                                if 'resultados' in avaliacao and avaliacao['resultados'] and str(avaliacao['resultados']) != 'nan':
                                    st.write(avaliacao['resultados'])
                                
                                st.markdown("**Recomendações:**")
                                if 'recomendacoes' in avaliacao and avaliacao['recomendacoes'] and str(avaliacao['recomendacoes']) != 'nan':
                                    st.write(avaliacao['recomendacoes'])
                                
                                if 'proxima_avaliacao' in avaliacao and avaliacao['proxima_avaliacao'] and str(avaliacao['proxima_avaliacao']) != 'nan':
                                    st.markdown(f"**Próxima avaliação programada:** {avaliacao['proxima_avaliacao']}")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("Não há registros de avaliações para este paciente.")
                
                with paciente_tabs[2]:  # Agendamentos
                    st.markdown("### Próximos Agendamentos")
                    
                    hoje = datetime.now().strftime('%Y-%m-%d')
                    agendamentos_futuros = agendamentos_paciente[agendamentos_paciente['data'] >= hoje]
                    
                    if len(agendamentos_futuros) > 0:
                        agendamentos_futuros = agendamentos_futuros.sort_values('data')
                        
                        for _, agendamento in agendamentos_futuros.iterrows():
                            cor_status = CORES_STATUS.get(agendamento['status'], "#ECEFF1")
                            
                            st.markdown(
                                f"<div style='background-color:{cor_status}; padding:10px; margin:5px; border-radius:5px;'>",
                                unsafe_allow_html=True
                            )
                            
                            col1, col2, col3 = st.columns([1, 2, 1])
                            
                            with col1:
                                st.markdown(f"**{agendamento['data']}**")
                                st.markdown(f"**{agendamento['horario']}**")
                            
                            with col2:
                                st.markdown(f"Terapeuta: {agendamento['terapeuta']}")
                                if 'observacao' in agendamento and agendamento['observacao'] and str(agendamento['observacao']) != 'nan':
                                    st.markdown(f"Obs: {agendamento['observacao']}")
                            
                            with col3:
                                st.markdown(f"**Status:** {agendamento['status']}")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("### Histórico de Agendamentos")
                        agendamentos_passados = agendamentos_paciente[agendamentos_paciente['data'] < hoje]
                        
                        if len(agendamentos_passados) > 0:
                            agendamentos_passados = agendamentos_passados.sort_values('data', ascending=False)
                            st.dataframe(agendamentos_passados[['data', 'horario', 'terapeuta', 'status']])
                        else:
                            st.info("Não há histórico de agendamentos para este paciente.")
                    else:
                        st.info("Não há agendamentos futuros para este paciente.")
                        
                        st.markdown("### Histórico de Agendamentos")
                        agendamentos_passados = agendamentos_paciente[agendamentos_paciente['data'] < hoje]
                        
                        if len(agendamentos_passados) > 0:
                            agendamentos_passados = agendamentos_passados.sort_values('data', ascending=False)
                            st.dataframe(agendamentos_passados[['data', 'horario', 'terapeuta', 'status']])
                        else:
                            st.info("Não há histórico de agendamentos para este paciente.")
            else:
                st.error("Paciente não encontrado.")
        else:
            st.info("Selecione um paciente na lista para visualizar sua ficha.")

def mostrar_atendimentos():
    """Exibe a seção de gerenciamento de atendimentos"""
    st.markdown("<h1 class='main-header'>Registro de Atendimentos</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Novo Atendimento", "Histórico de Atendimentos", "Análise de Habilidades"])
    
    # Carregar dados
    pacientes_df = carregar_pacientes()
    atendimentos_df = carregar_atendimentos()
    
    with tabs[0]:  # Novo Atendimento
        st.markdown("<h2 class='sub-header'>Registrar Novo Atendimento</h2>", unsafe_allow_html=True)
        
        with st.form("form_atendimento"):
            # Seleção de paciente
            paciente_id = st.selectbox(
                "Selecione o Paciente*",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_atendimento = st.date_input("Data do Atendimento*", value=datetime.now())
                terapeuta = st.text_input("Terapeuta Responsável*", value=st.session_state.usuario if 'usuario' in st.session_state else "")
            
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
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Registrar Atendimento")
            
            if submitted:
                # Verificar campos obrigatórios
                if not paciente_id or not data_atendimento or not terapeuta:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    # Preparar dados
                    dados_atendimento = {
                        'paciente_id': paciente_id,
                        'data': data_atendimento.strftime('%Y-%m-%d'),
                        'terapeuta': terapeuta,
                        'habilidades_trabalhadas': ', '.join(st.session_state.habilidades_selecionadas),
                        'descricao': descricao,
                        'evolucao': evolucao,
                        'comportamentos': comportamentos
                    }
                    
                    # Inserir no banco
                    atendimento_id = inserir_atendimento(dados_atendimento)
                    
                    # Limpar habilidades selecionadas
                    st.session_state.habilidades_selecionadas = []
                    
                    st.success("Atendimento registrado com sucesso!")
                    time.sleep(1)
                    st.experimental_rerun()
    
    with tabs[1]:  # Histórico de Atendimentos
        st.markdown("<h2 class='sub-header'>Histórico de Atendimentos</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_paciente = st.selectbox(
                "Filtrar por Paciente",
                options=["Todos"] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado"
            )
        
        with col2:
            filtro_terapeuta = st.text_input("Filtrar por Terapeuta")
        
        with col3:
            periodo = st.date_input(
                "Período (Início, Fim)",
                [datetime.now() - timedelta(days=30), datetime.now()],
                max_value=datetime.now()
            )
        
        # Aplicar filtros
        atendimentos_filtrados = atendimentos_df
        
        if filtro_paciente != "Todos":
            atendimentos_filtrados = atendimentos_filtrados[atendimentos_filtrados['paciente_id'] == filtro_paciente]
        
        if filtro_terapeuta:
            atendimentos_filtrados = atendimentos_filtrados[atendimentos_filtrados['terapeuta'].str.contains(filtro_terapeuta, case=False, na=False)]
        
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
            atendimentos_completos = pd.merge(
                atendimentos_filtrados,
                pacientes_df[['id', 'nome']],
                left_on='paciente_id',
                right_on='id',
                how='left',
                suffixes=('', '_paciente')
            )
            
            for _, atendimento in atendimentos_completos.iterrows():
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{atendimento['data']}**")
                
                with col2:
                    nome_paciente = atendimento['nome'] if 'nome' in atendimento else "Paciente não encontrado"
                    st.markdown(f"**{nome_paciente}**")
                    st.markdown(f"Terapeuta: {atendimento['terapeuta']}")
                
                st.markdown("**Habilidades trabalhadas:**")
                if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas'] and str(atendimento['habilidades_trabalhadas']) != 'nan':
                    habilidades_list = str(atendimento['habilidades_trabalhadas']).split(',')
                    habilidades_html = ""
                    for hab in habilidades_list:
                        hab = hab.strip()
                        if hab:
                            habilidades_html += f"<span class='skill-tag'>{hab}</span>"
                    st.markdown(habilidades_html, unsafe_allow_html=True)
                
                with st.expander("Ver detalhes do atendimento"):
                    st.markdown("**Descrição das atividades:**")
                    if 'descricao' in atendimento and atendimento['descricao'] and str(atendimento['descricao']) != 'nan':
                        st.write(atendimento['descricao'])
                    
                    st.markdown("**Evolução observada:**")
                    if 'evolucao' in atendimento and atendimento['evolucao'] and str(atendimento['evolucao']) != 'nan':
                        st.write(atendimento['evolucao'])
                    
                    if 'comportamentos' in atendimento and atendimento['comportamentos'] and str(atendimento['comportamentos']) != 'nan':
                        st.markdown("**Comportamentos observados:**")
                        st.write(atendimento['comportamentos'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum atendimento encontrado com os filtros selecionados.")
    
    with tabs[2]:  # Análise de Habilidades
        st.markdown("<h2 class='sub-header'>Análise de Habilidades Trabalhadas</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            paciente_analise = st.selectbox(
                "Selecione o Paciente",
                options=["Todos"] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
                key="paciente_analise"
            )
        
        with col2:
            periodo_analise = st.selectbox(
                "Período de Análise",
                options=["Último mês", "Últimos 3 meses", "Últimos 6 meses", "Último ano"]
            )
        
        if st.button("Gerar Análise"):
            # Determinar período de análise
            hoje = datetime.now()
            if periodo_analise == "Último mês":
                data_inicio = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
            elif periodo_analise == "Últimos 3 meses":
                data_inicio = (hoje - timedelta(days=90)).strftime('%Y-%m-%d')
            elif periodo_analise == "Últimos 6 meses":
                data_inicio = (hoje - timedelta(days=180)).strftime('%Y-%m-%d')
            else:  # Último ano
                data_inicio = (hoje - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Filtrar atendimentos
            atendimentos_periodo = atendimentos_df[atendimentos_df['data'] >= data_inicio]
            
            if paciente_analise != "Todos":
                atendimentos_periodo = atendimentos_periodo[atendimentos_periodo['paciente_id'] == paciente_analise]
                paciente_nome = pacientes_df[pacientes_df['id'] == paciente_analise]['nome'].iloc[0]
                st.markdown(f"### Análise para: {paciente_nome}")
            else:
                st.markdown("### Análise para todos os pacientes")
            
            st.markdown(f"**Período:** {data_inicio} até hoje")
            st.markdown(f"**Total de atendimentos analisados:** {len(atendimentos_periodo)}")
            
            if len(atendimentos_periodo) > 0:
                # Analisar habilidades trabalhadas
                habilidades_count = {}
                
                for _, atendimento in atendimentos_periodo.iterrows():
                    if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas'] and str(atendimento['habilidades_trabalhadas']) != 'nan':
                        habilidades = [h.strip() for h in str(atendimento['habilidades_trabalhadas']).split(',') if h.strip()]
                        for hab in habilidades:
                            if hab in habilidades_count:
                                habilidades_count[hab] += 1
                            else:
                                habilidades_count[hab] = 1
                
                if habilidades_count:
                    # Ordenar por frequência
                    habilidades_sorted = sorted(habilidades_count.items(), key=lambda x: x[1], reverse=True)
                    
                    # Limitar para as 15 principais
                    top_habilidades = habilidades_sorted[:15]
                    
                    # Criar gráfico
                    fig, ax = plt.subplots(figsize=(12, 8))
                    habs, counts = zip(*top_habilidades)
                    ax.barh(habs, counts, color='purple')
                    ax.set_xlabel('Número de Sessões')
                    ax.set_title('Habilidades Mais Trabalhadas no Período')
                    st.pyplot(fig)
                    
                    # Análise por categoria
                    st.markdown("### Análise por Categoria de Habilidade")
                    
                    # Agrupar habilidades por categoria
                    categorias_count = {}
                    for hab, count in habilidades_count.items():
                        categoria_encontrada = False
                        for categoria, habilidades in HABILIDADES_PSICOMOTORAS.items():
                            if hab in habilidades:
                                if categoria in categorias_count:
                                    categorias_count[categoria] += count
                                else:
                                    categorias_count[categoria] = count
                                categoria_encontrada = True
                                break
                        
                        if not categoria_encontrada:
                            if "Outras" in categorias_count:
                                categorias_count["Outras"] += count
                            else:
                                categorias_count["Outras"] = count
                    
                    # Criar gráfico de categorias
                    if categorias_count:
                        categorias_sorted = sorted(categorias_count.items(), key=lambda x: x[1], reverse=True)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        cats, counts = zip(*categorias_sorted)
                        ax.bar(cats, counts, color='purple')
                        ax.set_ylabel('Número de Sessões')
                        ax.set_title('Categorias de Habilidades Trabalhadas')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Recomendações
                        st.markdown("### Recomendações de Balanceamento de Habilidades")
                        
                        # Encontrar categorias menos trabalhadas
                        categorias_menos_trabalhadas = categorias_sorted[-(min(3, len(categorias_sorted))):]
                        
                        st.markdown("Baseado na análise, recomenda-se aumentar o foco nas seguintes categorias:")
                        for cat, count in categorias_menos_trabalhadas:
                            st.markdown(f"- **{cat}**: Trabalhada em apenas {count} sessões")
                            st.markdown("  Habilidades específicas recomendadas:")
                            if cat in HABILIDADES_PSICOMOTORAS:
                                for hab in HABILIDADES_PSICOMOTORAS[cat][:3]:
                                    st.markdown(f"  - {hab}")
                else:
                    st.warning("Não foi possível encontrar registros de habilidades trabalhadas no período selecionado.")
            else:
                st.info("Não há atendimentos registrados no período selecionado.")

def mostrar_avaliacoes():
    """Exibe a seção de gerenciamento de avaliações"""
    st.markdown("<h1 class='main-header'>Avaliações</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Nova Avaliação", "Lista de Avaliações", "Acompanhamento"])
    
    # Carregar dados
    pacientes_df = carregar_pacientes()
    avaliacoes_df = carregar_avaliacoes()
    
    with tabs[0]:  # Nova Avaliação
        st.markdown("<h2 class='sub-header'>Registrar Nova Avaliação</h2>", unsafe_allow_html=True)
        
        with st.form("form_avaliacao"):
            # Seleção de paciente
            paciente_id = st.selectbox(
                "Selecione o Paciente*",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_avaliacao = st.date_input("Data da Avaliação*", value=datetime.now())
                tipo_avaliacao = st.selectbox("Tipo de Avaliação*", options=TIPOS_AVALIACAO)
            
            with col2:
                terapeuta = st.text_input("Avaliador*", value=st.session_state.usuario if 'usuario' in st.session_state else "")
                proxima_avaliacao = st.date_input("Data para próxima avaliação", value=datetime.now() + timedelta(days=180))
            
            # Áreas avaliadas
            st.markdown("### Áreas Avaliadas")
            
            areas_avaliadas = {}
            pontuacoes = {}
            
            for categoria, habilidades in HABILIDADES_PSICOMOTORAS.items():
                with st.expander(f"Avaliar: {categoria}"):
                    for habilidade in habilidades:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{habilidade}**")
                        with col2:
                            nivel = st.selectbox(
                                "Nível",
                                options=[""] + NIVEIS_DESENVOLVIMENTO,
                                key=f"nivel_{habilidade}"
                            )
                            if nivel:
                                areas_avaliadas[habilidade] = nivel
                                pontuacoes[habilidade] = NIVEIS_DESENVOLVIMENTO.index(nivel) + 1
            
            # Resultados e recomendações
            st.markdown("### Resultados e Recomendações")
            resultados = st.text_area("Resultados da avaliação", height=150)
            recomendacoes = st.text_area("Recomendações", height=150)
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Registrar Avaliação")
            
            if submitted:
                # Verificar campos obrigatórios
                if not paciente_id or not data_avaliacao or not tipo_avaliacao or not terapeuta:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    # Preparar dados
                    dados_avaliacao = {
                        'paciente_id': paciente_id,
                        'data': data_avaliacao.strftime('%Y-%m-%d'),
                        'tipo_avaliacao': tipo_avaliacao,
                        'terapeuta': terapeuta,
                        'resultados': resultados,
                        'recomendacoes': recomendacoes,
                        'proxima_avaliacao': proxima_avaliacao.strftime('%Y-%m-%d'),
                        'areas_avaliadas': json.dumps(areas_avaliadas),
                        'pontuacao': json.dumps(pontuacoes)
                    }
                    
                    # Inserir no banco
                    avaliacao_id = inserir_avaliacao(dados_avaliacao)
                    
                    st.success("Avaliação registrada com sucesso!")
                    time.sleep(1)
                    st.experimental_rerun()
    
    with tabs[1]:  # Lista de Avaliações
        st.markdown("<h2 class='sub-header'>Lista de Avaliações</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_paciente = st.selectbox(
                "Filtrar por Paciente",
                options=["Todos"] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
                key="filtro_paciente_avaliacoes"
            )
        
        with col2:
            filtro_tipo = st.selectbox(
                "Filtrar por Tipo",
                options=["Todos"] + TIPOS_AVALIACAO
            )
        
        with col3:
            periodo = st.date_input(
                "Período (Início, Fim)",
                [datetime.now() - timedelta(days=365), datetime.now()],
                max_value=datetime.now(),
                key="periodo_avaliacoes"
            )
        
        # Aplicar filtros
        avaliacoes_filtradas = avaliacoes_df
        
        if filtro_paciente != "Todos":
            avaliacoes_filtradas = avaliacoes_filtradas[avaliacoes_filtradas['paciente_id'] == filtro_paciente]
        
        if filtro_tipo != "Todos":
            avaliacoes_filtradas = avaliacoes_filtradas[avaliacoes_filtradas['tipo_avaliacao'] == filtro_tipo]
        
        # Filtrar por período
        if len(periodo) == 2:
            inicio, fim = periodo
            avaliacoes_filtradas = avaliacoes_filtradas[
                (avaliacoes_filtradas['data'] >= inicio.strftime('%Y-%m-%d')) & 
                (avaliacoes_filtradas['data'] <= fim.strftime('%Y-%m-%d'))
            ]
        
        # Exibir resultados
        if len(avaliacoes_filtradas) > 0:
            avaliacoes_filtradas = avaliacoes_filtradas.sort_values('data', ascending=False)
            
            # Juntar com nomes dos pacientes
            avaliacoes_completas = pd.merge(
                avaliacoes_filtradas,
                pacientes_df[['id', 'nome']],
                left_on='paciente_id',
                right_on='id',
                how='left',
                suffixes=('', '_paciente')
            )
            
            for _, avaliacao in avaliacoes_completas.iterrows():
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{avaliacao['data']}**")
                    st.markdown(f"**{avaliacao['tipo_avaliacao']}**")
                
                with col2:
                    nome_paciente = avaliacao['nome'] if 'nome' in avaliacao else "Paciente não encontrado"
                    st.markdown(f"**{nome_paciente}**")
                    st.markdown(f"Avaliador: {avaliacao['terapeuta']}")
                    
                    if 'proxima_avaliacao' in avaliacao and avaliacao['proxima_avaliacao'] and str(avaliacao['proxima_avaliacao']) != 'nan':
                        st.markdown(f"Próxima avaliação: {avaliacao['proxima_avaliacao']}")
                
                with st.expander("Ver detalhes da avaliação"):
                    if 'areas_avaliadas' in avaliacao and avaliacao['areas_avaliadas'] and str(avaliacao['areas_avaliadas']) != 'nan':
                        st.markdown("#### Áreas Avaliadas")
                        try:
                            areas = json.loads(avaliacao['areas_avaliadas'])
                            for area, nivel in areas.items():
                                st.markdown(f"- **{area}:** {nivel}")
                        except:
                            st.write("Erro ao carregar áreas avaliadas")
                    
                    st.markdown("#### Resultados")
                    if 'resultados' in avaliacao and avaliacao['resultados'] and str(avaliacao['resultados']) != 'nan':
                        st.write(avaliacao['resultados'])
                    
                    st.markdown("#### Recomendações")
                    if 'recomendacoes' in avaliacao and avaliacao['recomendacoes'] and str(avaliacao['recomendacoes']) != 'nan':
                        st.write(avaliacao['recomendacoes'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhuma avaliação encontrada com os filtros selecionados.")
    
    with tabs[2]:  # Acompanhamento
        st.markdown("<h2 class='sub-header'>Acompanhamento da Evolução</h2>", unsafe_allow_html=True)
        
        # Selecionar paciente para acompanhamento
        paciente_evolucao = st.selectbox(
            "Selecione o Paciente",
            options=pacientes_df['id'].tolist(),
            format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
            key="paciente_evolucao"
        )
        
        if st.button("Analisar Evolução"):
            # Filtrar avaliações do paciente
            avaliacoes_paciente = avaliacoes_df[avaliacoes_df['paciente_id'] == paciente_evolucao]
            
            if len(avaliacoes_paciente) > 0:
                # Ordenar por data
                avaliacoes_paciente = avaliacoes_paciente.sort_values('data')
                
                # Buscar nome do paciente
                paciente_nome = pacientes_df[pacientes_df['id'] == paciente_evolucao]['nome'].iloc[0]
                
                st.markdown(f"### Evolução de {paciente_nome}")
                
                # Extrair pontuações
                evolucao_dados = {}
                
                for _, avaliacao in avaliacoes_paciente.iterrows():
                    data = avaliacao['data']
                    
                    if 'pontuacao' in avaliacao and avaliacao['pontuacao'] and str(avaliacao['pontuacao']) != 'nan':
                        try:
                            pontuacoes = json.loads(avaliacao['pontuacao'])
                            
                            for area, pontuacao in pontuacoes.items():
                                if area not in evolucao_dados:
                                    evolucao_dados[area] = []
                                
                                evolucao_dados[area].append((data, pontuacao))
                        except:
                            continue
                
                # Criar gráficos de evolução
                if evolucao_dados:
                    for area, dados in evolucao_dados.items():
                        if len(dados) > 1:  # Só mostrar áreas com pelo menos 2 avaliações
                            st.markdown(f"#### Evolução: {area}")
                            
                            datas = [d[0] for d in dados]
                            valores = [d[1] for d in dados]
                            
                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.plot(datas, valores, marker='o', linestyle='-', color='purple')
                            ax.set_xlabel('Data')
                            ax.set_ylabel('Nível (1-7)')
                            ax.set_title(f'Evolução em {area}')
                            plt.xticks(rotation=45)
                            plt.grid(True, linestyle='--', alpha=0.7)
                            plt.tight_layout()
                            st.pyplot(fig)
                    
                    # Visão geral das áreas
                    st.markdown("### Visão Geral da Evolução")
                    
                    # Selecionar áreas com pelo menos 2 avaliações
                    areas_completas = {area: dados for area, dados in evolucao_dados.items() if len(dados) > 1}
                    
                    if areas_completas:
                        # Calcular evolução percentual
                        evolucao_percentual = {}
                        
                        for area, dados in areas_completas.items():
                            primeiro = dados[0][1]
                            ultimo = dados[-1][1]
                            
                            if primeiro > 0:  # Evitar divisão por zero
                                evolucao_percentual[area] = (ultimo - primeiro) / primeiro * 100
                            else:
                                evolucao_percentual[area] = 0
                        
                        # Criar gráfico de barras
                        fig, ax = plt.subplots(figsize=(12, 6))
                        areas = list(evolucao_percentual.keys())
                        percentuais = list(evolucao_percentual.values())
                        
                        cores = ['green' if p > 0 else 'red' for p in percentuais]
                        ax.bar(areas, percentuais, color=cores)
                        ax.set_xlabel('Áreas Avaliadas')
                        ax.set_ylabel('Evolução (%)')
                        ax.set_title('Percentual de Evolução por Área')
                        plt.xticks(rotation=45, ha='right')
                        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Recomendações baseadas na evolução
                        st.markdown("### Recomendações Baseadas na Evolução")
                        
                        # Identificar áreas com menor evolução
                        areas_ordenadas = sorted(evolucao_percentual.items(), key=lambda x: x[1])
                        areas_menor_evolucao = areas_ordenadas[:min(3, len(areas_ordenadas))]
                        
                        st.markdown("Baseado na análise de evolução, recomenda-se focar nas seguintes áreas:")
                        for area, percentual in areas_menor_evolucao:
                            st.markdown(f"- **{area}**: Evolução de {percentual:.1f}%")
                else:
                    st.info("Não há dados suficientes para análise de evolução.")
            else:
                st.info("Não há avaliações suficientes para análise de evolução.")
        else:
            st.info("Selecione um paciente e clique em 'Analisar Evolução' para visualizar o progresso.")

def mostrar_agendamentos():
    """Exibe a seção de agendamentos"""
    st.markdown("<h1 class='main-header'>Agendamentos</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Novo Agendamento", "Calendário", "Gestão de Agendamentos", "Agrupamentos Sugeridos"])
    
    # Carregar dados
    pacientes_df = carregar_pacientes()
    agendamentos_df = carregar_agendamentos()
    
    with tabs[0]:  # Novo Agendamento
        st.markdown("<h2 class='sub-header'>Agendar Nova Sessão</h2>", unsafe_allow_html=True)
        
        with st.form("form_agendamento"):
            # Seleção de paciente
            paciente_id = st.selectbox(
                "Selecione o Paciente*",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
                key="paciente_agendamento"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                data_agendamento = st.date_input("Data da Sessão*", min_value=datetime.now())
                horario = st.time_input("Horário*", value=datetime.now().time().replace(minute=0, second=0, microsecond=0))
            
            with col2:
                terapeuta = st.text_input("Terapeuta Responsável*", value=st.session_state.usuario if 'usuario' in st.session_state else "")
                status = st.selectbox("Status*", options=STATUS_AGENDAMENTO, index=0)
            
            observacao = st.text_area("Observações", height=100)
            
            # Opções adicionais
            col1, col2 = st.columns(2)
            with col1:
                gerar_gcal = st.checkbox("Gerar evento no Google Calendar")
            
            with col2:
                notificar_whatsapp = st.checkbox("Notificar responsável via WhatsApp")
            
            st.markdown("(*) Campos obrigatórios")
            submitted = st.form_submit_button("Agendar Sessão")
            
            if submitted:
                # Verificar campos obrigatórios
                if not paciente_id or not data_agendamento or not horario or not terapeuta or not status:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    # Preparar dados
                    dados_agendamento = {
                        'paciente_id': paciente_id,
                        'data': data_agendamento.strftime('%Y-%m-%d'),
                        'horario': horario.strftime('%H:%M'),
                        'terapeuta': terapeuta,
                        'status': status,
                        'observacao': observacao
                    }
                    
                    # Inserir no banco
                    agendamento_id = inserir_agendamento(dados_agendamento)
                    
                    # Mensagem de feedback
                    msg = "Sessão agendada com sucesso!"
                    
                    if gerar_gcal:
                        msg += " (Google Calendar: simulado)"
                    
                    if notificar_whatsapp:
                        msg += " (WhatsApp: simulado)"
                    
                    st.success(msg)
                    time.sleep(1)
                    st.experimental_rerun()
    
    with tabs[1]:  # Calendário
        st.markdown("<h2 class='sub-header'>Calendário de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Escolher mês e ano
        col1, col2 = st.columns(2)
        with col1:
            mes_ano = st.date_input(
                "Selecione o mês",
                value=datetime.now().replace(day=1),
                format="MM/YYYY"
            )
        
        with col2:
            filtro_terapeuta = st.text_input("Filtrar por terapeuta")
        
        # Determinar dias do mês
        primeiro_dia = mes_ano.replace(day=1)
        if mes_ano.month == 12:
            ultimo_dia = mes_ano.replace(year=mes_ano.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia = mes_ano.replace(month=mes_ano.month + 1, day=1) - timedelta(days=1)
        
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
            dia_atual = dia_atual + timedelta(days=1)
        
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
        
        # Juntar com nomes dos pacientes
        if len(agendamentos_mes) > 0:
            agendamentos_completos = pd.merge(
                agendamentos_mes,
                pacientes_df[['id', 'nome']],
                left_on='paciente_id',
                right_on='id',
                how='left',
                suffixes=('', '_paciente')
            )
        else:
            agendamentos_completos = pd.DataFrame()
        
        # Exibir semanas
        for semana in semanas:
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                if dia:
                    data_str = dia.strftime('%Y-%m-%d')
                    
                    # Verificar se há agendamentos para este dia
                    agendamentos_dia = agendamentos_completos[agendamentos_completos['data'] == data_str] if len(agendamentos_completos) > 0 else pd.DataFrame()
                    num_agendamentos = len(agendamentos_dia)
                    
                    # Estilo para destacar o dia atual
                    estilo = ""
                    if dia.date() == datetime.now().date():
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
                            nome_paciente = agendamento['nome'] if 'nome' in agendamento else "Paciente não encontrado"
                            
                            # Cor baseada no status
                            cor_status = CORES_STATUS.get(agendamento['status'], "#ECEFF1")
                            
                            # Limitar tamanho do nome para ajustar ao layout
                            nome_exibir = nome_paciente[:12] + "..." if len(nome_paciente) > 12 else nome_paciente
                            
                            cols[i].markdown(
                                f"<div style='background-color:{cor_status}; padding:3px; margin:2px; border-radius:3px; font-size:0.8em;'>"
                                f"{agendamento['horario']} - {nome_exibir}</div>",
                                unsafe_allow_html=True
                            )
                else:
                    # Dia vazio
                    cols[i].markdown("", unsafe_allow_html=True)
    
    with tabs[2]:  # Gestão de Agendamentos
        st.markdown("<h2 class='sub-header'>Gestão de Agendamentos</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            periodo = st.date_input(
                "Período",
                [datetime.now(), datetime.now() + timedelta(days=7)]
            )
        
        with col2:
            filtro_paciente = st.selectbox(
                "Paciente",
                options=["Todos"] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
                key="filtro_agenda_paciente"
            )
        
        with col3:
            filtro_status = st.multiselect(
                "Status",
                options=STATUS_AGENDAMENTO
            )
        
        # Aplicar filtros
        agendamentos_filtrados = agendamentos_df
        
        if len(periodo) == 2:
            inicio, fim = periodo
            agendamentos_filtrados = agendamentos_filtrados[
                (agendamentos_filtrados['data'] >= inicio.strftime('%Y-%m-%d')) & 
                (agendamentos_filtrados['data'] <= fim.strftime('%Y-%m-%d'))
            ]
        
        if filtro_paciente != "Todos":
            agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['paciente_id'] == filtro_paciente]
        
        if filtro_status:
            agendamentos_filtrados = agendamentos_filtrados[agendamentos_filtrados['status'].isin(filtro_status)]
        
        # Ordenar por data e horário
        agendamentos_filtrados = agendamentos_filtrados.sort_values(['data', 'horario'])
        
        # Exibir resultados
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
            
            st.markdown("### Lista de Agendamentos")
            
            for _, agendamento in agendamentos_completos.iterrows():
                # Determinar cor baseada no status
                cor_status = CORES_STATUS.get(agendamento['status'], "#ECEFF1")
                
                st.markdown(
                    f"<div style='background-color:{cor_status}; padding:10px; margin:5px; border-radius:5px;'>",
                    unsafe_allow_html=True
                )
                
                col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                
                with col1:
                    st.markdown(f"**{agendamento['data']}**<br>{agendamento['horario']}", unsafe_allow_html=True)
                
                with col2:
                    nome_paciente = agendamento['nome'] if 'nome' in agendamento else "Paciente não encontrado"
                    st.markdown(f"**{nome_paciente}**<br>Terapeuta: {agendamento['terapeuta']}", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"**Status:** {agendamento['status']}<br>", unsafe_allow_html=True)
                    if 'observacao' in agendamento and agendamento['observacao'] and str(agendamento['observacao']) != 'nan':
                        obs_curta = agendamento['observacao'][:30] + "..." if len(str(agendamento['observacao'])) > 30 else agendamento['observacao']
                        st.markdown(f"Obs: {obs_curta}", unsafe_allow_html=True)
                
                with col4:
                    # Botões de ação
                    if st.button("Editar", key=f"edit_{agendamento['id']}"):
                        st.session_state.editar_agendamento = agendamento['id']
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Modal de edição
            if 'editar_agendamento' in st.session_state and st.session_state.editar_agendamento:
                agendamento_id = st.session_state.editar_agendamento
                agendamento = agendamentos_df[agendamentos_df['id'] == agendamento_id].iloc[0]
                
                st.markdown("<h3>Editar Agendamento</h3>", unsafe_allow_html=True)
                
                with st.form("form_editar_agendamento"):
                    # Campos de edição
                    status_options = STATUS_AGENDAMENTO
                    status_index = status_options.index(agendamento['status']) if agendamento['status'] in status_options else 0
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novo_status = st.selectbox("Status", options=status_options, index=status_index)
                        nova_data = st.date_input("Data", value=datetime.strptime(agendamento['data'], '%Y-%m-%d'))
                    
                    with col2:
                        novo_terapeuta = st.text_input("Terapeuta", value=agendamento['terapeuta'])
                        novo_horario = st.time_input("Horário", value=datetime.strptime(agendamento['horario'], '%H:%M').time())
                    
                    nova_observacao = st.text_area("Observação", value=agendamento['observacao'] if isinstance(agendamento['observacao'], str) else "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar Alterações"):
                            # Preparar dados atualizados
                            dados_atualizados = {
                                'status': novo_status,
                                'data': nova_data.strftime('%Y-%m-%d'),
                                'terapeuta': novo_terapeuta,
                                'horario': novo_horario.strftime('%H:%M'),
                                'observacao': nova_observacao
                            }
                            
                            # Atualizar no banco
                            atualizar_agendamento(agendamento_id, dados_atualizados)
                            
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
    
    with tabs[3]:  # Agrupamentos Sugeridos
        st.markdown("<h2 class='sub-header'>Sugestões de Agrupamentos</h2>", unsafe_allow_html=True)
        st.markdown("""
        Este sistema analisa o perfil dos pacientes e sugere possíveis agrupamentos para sessões em conjunto, 
        baseados em compatibilidade de perfil comportamental, habilidades a serem trabalhadas e nível de suporte.
        """)
        
        # Seleção de data para análise
        data_analise = st.date_input("Data para análise", value=datetime.now())
        
        # Simular algoritmo de compatibilidade
        if st.button("Gerar Sugestões de Agrupamentos"):
            # Em um sistema real, aqui seria implementado um algoritmo que analisaria:
            # 1. Pacientes com necessidades semelhantes (baseado nas avaliações)
            # 2. Compatibilidade de faixa etária
            # 3. Compatibilidade de nível de suporte
            # 4. Compatibilidade comportamental
            
            st.markdown("### Sugestões de Agrupamentos")
            
            # Grupos simulados (para demonstração)
            grupos = [
                {
                    "nome": "Grupo 1: Coordenação Motora Global",
                    "horario": "09:00 - 10:00",
                    "pacientes": [
                        {"nome": "Maria Silva", "idade": 8, "nivel_suporte": "Nível 1"},
                        {"nome": "Pedro Costa", "idade": 7, "nivel_suporte": "Nível 1"},
                        {"nome": "Lucas Oliveira", "idade": 9, "nivel_suporte": "Nível 1"}
                    ],
                    "compatibilidade": 87,
                    "observacao": "Todos os pacientes precisam desenvolver coordenação motora global e têm comportamento compatível em grupo."
                },
                {
                    "nome": "Grupo 2: Equilíbrio e Praxia",
                    "horario": "10:30 - 11:30",
                    "pacientes": [
                        {"nome": "João Santos", "idade": 10, "nivel_suporte": "Nível 2"},
                        {"nome": "Ana Oliveira", "idade": 9, "nivel_suporte": "Nível 1"}
                    ],
                    "compatibilidade": 72,
                    "observacao": "Ambos precisam desenvolver equilíbrio. Ana pode ajudar a modelar comportamento para João."
                },
                {
                    "nome": "Grupo 3: Coordenação Motora Fina",
                    "horario": "14:00 - 15:00",
                    "pacientes": [
                        {"nome": "Luiza Mendes", "idade": 6, "nivel_suporte": "Nível 1"},
                        {"nome": "Gabriel Alves", "idade": 7, "nivel_suporte": "Nível 2"},
                        {"nome": "Sofia Castro", "idade": 6, "nivel_suporte": "Nível 1"}
                    ],
                    "compatibilidade": 75,
                    "observacao": "Todos precisam desenvolver coordenação motora fina. Atenção especial para Gabriel que pode precisar de mais suporte."
                }
            ]
            
            # Exibir sugestões
            for i, grupo in enumerate(grupos):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"#### {grupo['nome']}")
                st.markdown(f"**Horário sugerido:** {grupo['horario']}")
                st.markdown(f"**Compatibilidade:** {grupo['compatibilidade']}%")
                
                st.markdown("**Pacientes compatíveis:**")
                for paciente in grupo['pacientes']:
                    st.markdown(f"- {paciente['nome']} ({paciente['idade']} anos) - {paciente['nivel_suporte']}")
                
                st.markdown(f"**Observações:** {grupo['observacao']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Oferecer opção de criar agendamentos baseados nas sugestões
            st.markdown("---")
            st.markdown("### Ações")
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
                    st.success("Simulação: Agendamentos para Grupo 3 criados com sucesso!")

def mostrar_relatorios():
    """Exibe a seção de relatórios"""
    st.markdown("<h1 class='main-header'>Relatórios</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Relatório de Evolução", "Relatório de Frequência", "Relatório de Habilidades", "Compartilhar via WhatsApp"])
    
    # Carregar dados
    pacientes_df = carregar_pacientes()
    atendimentos_df = carregar_atendimentos()
    avaliacoes_df = carregar_avaliacoes()
    agendamentos_df = carregar_agendamentos()
    
    with tabs[0]:  # Relatório de Evolução
        st.markdown("<h2 class='sub-header'>Gerar Relatório de Evolução</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente
        paciente_id = st.selectbox(
            "Selecione o Paciente",
            options=pacientes_df['id'].tolist(),
            format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
            key="paciente_relatorio"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            periodo_inicio = st.date_input("Data Inicial", value=datetime.now() - timedelta(days=30))
        
        with col2:
            periodo_fim = st.date_input("Data Final", value=datetime.now())
        
        opcoes_relatorio = st.multiselect(
            "Incluir no relatório",
            options=["Dados pessoais", "Resumo de atendimentos", "Gráficos de evolução", "Avaliações do período", "Habilidades trabalhadas", "Recomendações"],
            default=["Dados pessoais", "Resumo de atendimentos", "Habilidades trabalhadas"]
        )
        
        if st.button("Gerar Relatório de Evolução"):
            if paciente_id and len(opcoes_relatorio) > 0:
                # Buscar dados do paciente
                paciente_data = pacientes_df[pacientes_df['id'] == paciente_id]
                
                if len(paciente_data) > 0:
                    paciente = paciente_data.iloc[0]
                    
                    # Buscar atendimentos do período
                    atendimentos_periodo = atendimentos_df[
                        (atendimentos_df['paciente_id'] == paciente_id) &
                        (atendimentos_df['data'] >= periodo_inicio.strftime('%Y-%m-%d')) &
                        (atendimentos_df['data'] <= periodo_fim.strftime('%Y-%m-%d'))
                    ]
                    
                    # Criar relatório
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<h2>Relatório de Evolução - {paciente['nome']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p>Período: {periodo_inicio.strftime('%d/%m/%Y')} a {periodo_fim.strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
                    
                    if "Dados pessoais" in opcoes_relatorio:
                        st.markdown("### Dados Pessoais")
                        st.markdown(f"**Nome:** {paciente['nome']}")
                        
                        if 'data_nascimento' in paciente and paciente['data_nascimento'] and str(paciente['data_nascimento']) != 'nan':
                            try:
                                data_nasc = datetime.strptime(paciente['data_nascimento'], '%Y-%m-%d')
                                idade = (datetime.now() - data_nasc).days // 365
                                st.markdown(f"**Idade:** {idade} anos")
                            except:
                                pass
                        
                        st.markdown(f"**Diagnóstico:** {paciente['diagnostico']}")
                        
                        if 'nivel_suporte' in paciente and paciente['nivel_suporte'] and str(paciente['nivel_suporte']) != 'nan':
                            st.markdown(f"**Nível de Suporte:** {paciente['nivel_suporte']}")
                    
                    if "Resumo de atendimentos" in opcoes_relatorio:
                        st.markdown("### Resumo de Atendimentos")
                        st.markdown(f"**Total de atendimentos no período:** {len(atendimentos_periodo)}")
                        
                        if len(atendimentos_periodo) > 0:
                            atendimentos_periodo = atendimentos_periodo.sort_values('data')
                            
                            st.markdown("#### Evolução observada")
                            for _, atendimento in atendimentos_periodo.iterrows():
                                st.markdown(f"**Sessão {atendimento['data']}:**")
                                
                                if 'evolucao' in atendimento and atendimento['evolucao'] and str(atendimento['evolucao']) != 'nan':
                                    st.markdown(atendimento['evolucao'])
                                else:
                                    st.markdown("*Sem registro de evolução*")
                    
                    if "Habilidades trabalhadas" in opcoes_relatorio and len(atendimentos_periodo) > 0:
                        st.markdown("### Habilidades Trabalhadas")
                        
                        # Contar frequência de habilidades
                        habilidades_contagem = {}
                        
                        for _, atendimento in atendimentos_periodo.iterrows():
                            if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas'] and str(atendimento['habilidades_trabalhadas']) != 'nan':
                                habilidades = [h.strip() for h in str(atendimento['habilidades_trabalhadas']).split(',') if h.strip()]
                                
                                for hab in habilidades:
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
                            
                            # Limitar para 10 primeiras
                            top_habilidades = habilidades_ordenadas[:10]
                            habs, frequencias = zip(*top_habilidades)
                            
                            ax.barh(habs, frequencias, color='purple')
                            ax.set_xlabel('Número de Sessões')
                            ax.set_title('Habilidades Mais Trabalhadas no Período')
                            plt.tight_layout()
                            st.pyplot(fig)
                    
                    if "Gráficos de evolução" in opcoes_relatorio:
                        st.markdown("### Gráficos de Evolução")
                        
                        # Buscar avaliações do período para análise de evolução
                        avaliacoes_periodo = avaliacoes_df[
                            (avaliacoes_df['paciente_id'] == paciente_id) &
                            (avaliacoes_df['data'] >= periodo_inicio.strftime('%Y-%m-%d')) &
                            (avaliacoes_df['data'] <= periodo_fim.strftime('%Y-%m-%d'))
                        ]
                        
                        if len(avaliacoes_periodo) > 1:  # Pelo menos 2 avaliações para comparar
                            st.markdown("#### Evolução nas Áreas Avaliadas")
                            
                            # Extrair pontuações
                            evolucao_dados = {}
                            
                            for _, avaliacao in avaliacoes_periodo.iterrows():
                                data = avaliacao['data']
                                
                                if 'pontuacao' in avaliacao and avaliacao['pontuacao'] and str(avaliacao['pontuacao']) != 'nan':
                                    try:
                                        pontuacoes = json.loads(avaliacao['pontuacao'])
                                        
                                        for area, pontuacao in pontuacoes.items():
                                            if area not in evolucao_dados:
                                                evolucao_dados[area] = []
                                            
                                            evolucao_dados[area].append((data, pontuacao))
                                    except:
                                        continue
                            
                            # Criar gráficos de evolução
                            if evolucao_dados:
                                for area, dados in evolucao_dados.items():
                                    if len(dados) > 1:  # Só mostrar áreas com pelo menos 2 avaliações
                                        st.markdown(f"**{area}**")
                                        
                                        datas = [d[0] for d in dados]
                                        valores = [d[1] for d in dados]
                                        
                                        fig, ax = plt.subplots(figsize=(10, 4))
                                        ax.plot(datas, valores, marker='o', linestyle='-', color='purple')
                                        ax.set_xlabel('Data')
                                        ax.set_ylabel('Nível')
                                        plt.xticks(rotation=45)
                                        plt.grid(True, linestyle='--', alpha=0.7)
                                        plt.tight_layout()
                                        st.pyplot(fig)
                            else:
                                st.info("Não há dados suficientes para gerar gráficos de evolução.")
                        else:
                            # Simulação de gráfico de evolução quando não há avaliações suficientes
                            if len(atendimentos_periodo) > 1:
                                st.info("Gráfico simulado baseado nos atendimentos (em um sistema completo, seria baseado em avaliações quantitativas)")
                                
                                fig, ax = plt.subplots(figsize=(10, 6))
                                datas = [datetime.strptime(d, '%Y-%m-%d') for d in sorted(atendimentos_periodo['data'].unique())]
                                valores = np.cumsum(np.random.rand(len(datas)) * 0.5 + 0.5)  # Simulação de progresso
                                
                                ax.plot(datas, valores, marker='o', linestyle='-', color='purple')
                                ax.set_xlabel('Data')
                                ax.set_ylabel('Nível de Habilidade (simulado)')
                                ax.set_title('Evolução das Habilidades ao Longo do Tempo')
                                plt.xticks(rotation=45)
                                plt.tight_layout()
                                st.pyplot(fig)
                            else:
                                st.info("Não há dados suficientes para gerar gráficos de evolução.")
                    
                    if "Avaliações do período" in opcoes_relatorio:
                        st.markdown("### Avaliações no Período")
                        
                        avaliacoes_periodo = avaliacoes_df[
                            (avaliacoes_df['paciente_id'] == paciente_id) &
                            (avaliacoes_df['data'] >= periodo_inicio.strftime('%Y-%m-%d')) &
                            (avaliacoes_df['data'] <= periodo_fim.strftime('%Y-%m-%d'))
                        ]
                        
                        if len(avaliacoes_periodo) > 0:
                            avaliacoes_periodo = avaliacoes_periodo.sort_values('data')
                            
                            for _, avaliacao in avaliacoes_periodo.iterrows():
                                st.markdown(f"#### {avaliacao['data']} - {avaliacao['tipo_avaliacao']}")
                                
                                st.markdown("**Resultados:**")
                                if 'resultados' in avaliacao and avaliacao['resultados'] and str(avaliacao['resultados']) != 'nan':
                                    st.markdown(avaliacao['resultados'])
                                else:
                                    st.markdown("*Sem registro de resultados*")
                                
                                st.markdown("**Recomendações:**")
                                if 'recomendacoes' in avaliacao and avaliacao['recomendacoes'] and str(avaliacao['recomendacoes']) != 'nan':
                                    st.markdown(avaliacao['recomendacoes'])
                                else:
                                    st.markdown("*Sem registro de recomendações*")
                        else:
                            st.info("Não foram realizadas avaliações no período selecionado.")
                    
                    if "Recomendações" in opcoes_relatorio:
                        st.markdown("### Recomendações para o Próximo Período")
                        recomendacoes = st.text_area("Adicione recomendações para o próximo período", height=150)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Botões de exportação
                    st.markdown("### Exportar Relatório")
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
                        if st.button("Enviar por E-mail"):
                            st.success("Simulação: Relatório enviado por e-mail para o responsável!")
                else:
                    st.error("Paciente não encontrado.")
            else:
                st.error("Por favor, selecione um paciente e pelo menos uma opção para o relatório.")
    
    with tabs[1]:  # Relatório de Frequência
        st.markdown("<h2 class='sub-header'>Relatório de Frequência</h2>", unsafe_allow_html=True)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            mes_ano_freq = st.date_input(
                "Selecione o mês",
                value=datetime.now().replace(day=1),
                format="MM/YYYY",
                key="mes_freq"
            )
        
        with col2:
            paciente_freq = st.selectbox(
                "Paciente (opcional)",
                options=["Todos"] + pacientes_df['id'].tolist(),
                format_func=lambda x: "Todos os pacientes" if x == "Todos" else pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
                key="paciente_freq"
            )
        
        if st.button("Gerar Relatório de Frequência"):
            st.markdown("<h3>Relatório de Frequência</h3>", unsafe_allow_html=True)
            
            # Determinar dias do mês
            primeiro_dia = mes_ano_freq.replace(day=1)
            if mes_ano_freq.month == 12:
                ultimo_dia = mes_ano_freq.replace(year=mes_ano_freq.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                ultimo_dia = mes_ano_freq.replace(month=mes_ano_freq.month + 1, day=1) - timedelta(days=1)
            
            # Filtrar agendamentos do mês
            agendamentos_mes = agendamentos_df[
                (agendamentos_df['data'] >= primeiro_dia.strftime('%Y-%m-%d')) & 
                (agendamentos_df['data'] <= ultimo_dia.strftime('%Y-%m-%d'))
            ]
            
            if paciente_freq != "Todos":
                agendamentos_mes = agendamentos_mes[agendamentos_mes['paciente_id'] == paciente_freq]
            
            # Calcular estatísticas
            total_agendamentos = len(agendamentos_mes)
            
            if total_agendamentos > 0:
                # Análise de status
                status_counts = {}
                
                for status in STATUS_AGENDAMENTO:
                    status_counts[status] = len(agendamentos_mes[agendamentos_mes['status'] == status])
                
                # Exibir estatísticas gerais
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                
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
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Gráfico de frequência
                fig, ax = plt.subplots(figsize=(10, 6))
                labels = status_counts.keys()
                sizes = status_counts.values()
                
                # Cores para cada status
                cores = []
                for status in labels:
                    cor = CORES_STATUS.get(status, "#ECEFF1")
                    # Converter cor de hex para RGB para poder escurecer um pouco
                    cores.append(cor)
                
                # Limpar zeros para melhor visualização
                labels_filtradas = []
                sizes_filtradas = []
                cores_filtradas = []
                
                for i, size in enumerate(sizes):
                    if size > 0:
                        labels_filtradas.append(labels[i])
                        sizes_filtradas.append(size)
                        cores_filtradas.append(cores[i])
                
                if labels_filtradas:
                    ax.pie(sizes_filtradas, labels=labels_filtradas, colors=cores_filtradas, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
                
                # Lista de faltas
                if status_counts["Faltou"] > 0:
                    st.markdown("<h3>Detalhamento de Faltas</h3>", unsafe_allow_html=True)
                    
                    faltas = agendamentos_mes[agendamentos_mes['status'] == "Faltou"]
                    
                    # Juntar com nomes dos pacientes
                    faltas_completo = pd.merge(
                        faltas,
                        pacientes_df[['id', 'nome']],
                        left_on='paciente_id',
                        right_on='id',
                        how='left',
                        suffixes=('', '_paciente')
                    )
                    
                    for _, falta in faltas_completo.iterrows():
                        nome_paciente = falta['nome'] if 'nome' in falta else "Paciente não encontrado"
                        
                        st.markdown(
                            f"<div style='background-color:#FFEBEE; padding:10px; margin:5px; border-radius:5px;'>"
                            f"**{falta['data']} às {falta['horario']}** - {nome_paciente} (Terapeuta: {falta['terapeuta']})"
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
    
    with tabs[2]:  # Relatório de Habilidades
        st.markdown("<h2 class='sub-header'>Relatório de Habilidades</h2>", unsafe_allow_html=True)
        
        # Filtros para o relatório
        col1, col2 = st.columns(2)
        
        with col1:
            paciente_hab = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
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
            hoje = datetime.now()
            if periodo_hab == "Último mês":
                data_inicio = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
            elif periodo_hab == "Últimos 3 meses":
                data_inicio = (hoje - timedelta(days=90)).strftime('%Y-%m-%d')
            elif periodo_hab == "Últimos 6 meses":
                data_inicio = (hoje - timedelta(days=180)).strftime('%Y-%m-%d')
            else:  # Último ano
                data_inicio = (hoje - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # Filtrar atendimentos do período
            atendimentos_periodo = atendimentos_df[
                (atendimentos_df['paciente_id'] == paciente_hab) &
                (atendimentos_df['data'] >= data_inicio) &
                (atendimentos_df['data'] <= hoje.strftime('%Y-%m-%d'))
            ]
            
            # Buscar dados do paciente
            paciente_data = pacientes_df[pacientes_df['id'] == paciente_hab]
            
            if len(paciente_data) > 0:
                paciente = paciente_data.iloc[0]
                
                if len(atendimentos_periodo) > 0:
                    st.markdown(f"**Paciente:** {paciente['nome']}")
                    st.markdown(f"**Período analisado:** {data_inicio} a {hoje.strftime('%Y-%m-%d')}")
                    st.markdown(f"**Total de atendimentos:** {len(atendimentos_periodo)}")
                    
                    # Analisar habilidades trabalhadas
                    habilidades_contagem = {}
                    
                    for _, atendimento in atendimentos_periodo.iterrows():
                        if 'habilidades_trabalhadas' in atendimento and atendimento['habilidades_trabalhadas'] and str(atendimento['habilidades_trabalhadas']) != 'nan':
                            habilidades = [h.strip() for h in str(atendimento['habilidades_trabalhadas']).split(',') if h.strip()]
                            
                            for hab in habilidades:
                                if hab in habilidades_contagem:
                                    habilidades_contagem[hab] += 1
                                else:
                                    habilidades_contagem[hab] = 1
                    
                    if habilidades_contagem:
                        # Ordenar por frequência
                        habilidades_ordenadas = sorted(habilidades_contagem.items(), key=lambda x: x[1], reverse=True)
                        
                        # Criar gráfico
                        fig, ax = plt.subplots(figsize=(12, 8))
                        
                        # Limitar para 15 habilidades
                        max_habs = min(15, len(habilidades_ordenadas))
                        habs, frequencias = zip(*habilidades_ordenadas[:max_habs])
                        
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
                        
                        # Buscar avaliação mais recente
                        avaliacoes_paciente = avaliacoes_df[avaliacoes_df['paciente_id'] == paciente_hab]
                        
                        if len(avaliacoes_paciente) > 0:
                            # Ordenar por data (mais recente primeiro)
                            avaliacoes_paciente = avaliacoes_paciente.sort_values('data', ascending=False)
                            avaliacao_recente = avaliacoes_paciente.iloc[0]
                            
                            # Extrair habilidades prioritárias da avaliação
                            habilidades_prioritarias = {}
                            
                            if 'areas_avaliadas' in avaliacao_recente and avaliacao_recente['areas_avaliadas'] and str(avaliacao_recente['areas_avaliadas']) != 'nan':
                                try:
                                    areas = json.loads(avaliacao_recente['areas_avaliadas'])
                                    pontuacoes = json.loads(avaliacao_recente['pontuacao']) if 'pontuacao' in avaliacao_recente and avaliacao_recente['pontuacao'] else {}
                                    
                                    for area, nivel in areas.items():
                                        # Determinar prioridade: maior para níveis mais baixos
                                        nivel_idx = NIVEIS_DESENVOLVIMENTO.index(nivel) if nivel in NIVEIS_DESENVOLVIMENTO else 0
                                        prioridade = 10 - nivel_idx  # Inverter para que níveis baixos tenham prioridade alta
                                        
                                        if area in pontuacoes:
                                            # Usar pontuação como prioridade se disponível
                                            prioridade = 10 - pontuacoes[area]
                                        
                                        habilidades_prioritarias[area] = max(1, min(10, prioridade))  # Limitar entre 1 e 10
                                except:
                                    # Simulação quando não há dados adequados
                                    for area in list(habilidades_contagem.keys())[:5]:
                                        habilidades_prioritarias[area] = np.random.randint(5, 10)
                            else:
                                # Simulação quando não há áreas avaliadas
                                for area in list(habilidades_contagem.keys())[:5]:
                                    habilidades_prioritarias[area] = np.random.randint(5, 10)
                        else:
                            # Simulação quando não há avaliações
                            for area in list(habilidades_contagem.keys())[:5]:
                                habilidades_prioritarias[area] = np.random.randint(5, 10)
                        
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
                        if dados_comparacao:
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
            else:
                st.error("Paciente não encontrado.")
    
    with tabs[3]:  # Compartilhar via WhatsApp
        st.markdown("<h2 class='sub-header'>Compartilhar Relatórios via WhatsApp</h2>", unsafe_allow_html=True)
        
        # Seleção de paciente e tipo de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            paciente_whats = st.selectbox(
                "Selecione o Paciente",
                options=pacientes_df['id'].tolist(),
                format_func=lambda x: pacientes_df[pacientes_df['id'] == x]['nome'].iloc[0] if x in pacientes_df['id'].values else "Paciente não encontrado",
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
                paciente_data = pacientes_df[pacientes_df['id'] == paciente_whats]
                
                if len(paciente_data) > 0:
                    paciente = paciente_data.iloc[0]
                    
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
                    st.error("Paciente não encontrado.")
            else:
                st.error("Por favor, selecione um paciente para enviar o relatório.")

def mostrar_configuracoes():
    """Exibe a seção de configurações do sistema"""
    st.markdown("<h1 class='main-header'>Configurações</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Sistema", "Backup e Restauração", "Usuários", "Sobre"])
    
    with tabs[0]:  # Sistema
        st.markdown("<h2 class='sub-header'>Configurações do Sistema</h2>", unsafe_allow_html=True)
        
        # Verificar se usuário tem permissão de administrador
        if 'perfil' not in st.session_state or st.session_state.perfil != 'admin':
            st.warning("Você precisa de permissões de administrador para acessar estas configurações.")
            return
        
        # Opções gerais
        st.markdown("### Opções Gerais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            notificacoes_email = st.checkbox("Ativar notificações por e-mail", value=True)
            notificacoes_whatsapp = st.checkbox("Ativar notificações por WhatsApp", value=True)
        
        with col2:
            backup_automatico = st.checkbox("Ativar backup automático diário", value=True)
            dias_retencao = st.number_input("Dias de retenção de backups", min_value=7, value=30)
        
        # Personalização
        st.markdown("### Personalização")
        
        tema_cores = st.selectbox(
            "Tema de cores",
            options=["Roxo (Padrão)", "Azul", "Verde", "Vermelho"]
        )
        
        logo = st.file_uploader("Logo personalizada", type=["png", "jpg", "jpeg"])
        
        nome_clinica = st.text_input("Nome da clínica", value="NeuroBase Psicomotricidade")
        
        # Integração
        st.markdown("### Integrações")
        
        integrar_google = st.checkbox("Integrar com Google Calendar", value=False)
        if integrar_google:
            google_api_key = st.text_input("Google API Key", type="password")
        
        integrar_whatsapp = st.checkbox("Integrar com WhatsApp Business API", value=False)
        if integrar_whatsapp:
            whatsapp_api_key = st.text_input("WhatsApp Business API Key", type="password")
        
        # Salvar configurações
        if st.button("Salvar Configurações"):
            # Aqui seria implementado o código para salvar as configurações
            st.success("Configurações salvas com sucesso!")
    
    with tabs[1]:  # Backup e Restauração
        st.markdown("<h2 class='sub-header'>Backup e Restauração</h2>", unsafe_allow_html=True)
        
        # Verificar se usuário tem permissão de administrador
        if 'perfil' not in st.session_state or st.session_state.perfil != 'admin':
            st.warning("Você precisa de permissões de administrador para acessar estas configurações.")
            return
        
        # Backup manual
        st.markdown("### Backup Manual")
        
        if st.button("Criar Backup Agora"):
            sucesso, arquivo = backup_banco_dados()
            
            if sucesso:
                st.success(f"Backup criado com sucesso: {arquivo}")
            else:
                st.error(f"Erro ao criar backup: {arquivo}")
        
        # Lista de backups
        st.markdown("### Backups Disponíveis")
        
        backups_df = obter_dados_backup()
        
        if len(backups_df) > 0:
            for _, backup in backups_df.iterrows():
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Data:** {backup['timestamp']}")
                    st.markdown(f"**Arquivo:** {backup['arquivo']}")
                    st.markdown(f"**Usuário:** {backup['usuario']}")
                
                with col2:
                    if st.button("Restaurar", key=f"restore_{backup['id']}"):
                        st.warning("Funcionalidade não implementada na demonstração")
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum backup disponível.")
        
        # Opções de exportação
        st.markdown("### Exportação de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar Todos os Dados (CSV)"):
                st.warning("Funcionalidade não implementada na demonstração")
        
        with col2:
            if st.button("Exportar Todos os Dados (JSON)"):
                st.warning("Funcionalidade não implementada na demonstração")
    
    with tabs[2]:  # Usuários
        st.markdown("<h2 class='sub-header'>Gerenciamento de Usuários</h2>", unsafe_allow_html=True)
        
        # Verificar se usuário tem permissão de administrador
        if 'perfil' not in st.session_state or st.session_state.perfil != 'admin':
            st.warning("Você precisa de permissões de administrador para acessar estas configurações.")
            return
        
        # Lista de usuários (simulada)
        st.markdown("### Usuários do Sistema")
        
        usuarios = [
            {"id": 1, "nome": "Administrador", "email": "admin@neurobase.com", "perfil": "admin", "ultimo_acesso": "2025-05-14 09:15:22"},
            {"id": 2, "nome": "Terapeuta", "email": "terapeuta@neurobase.com", "perfil": "terapeuta", "ultimo_acesso": "2025-05-14 08:30:15"},
        ]
        
        for usuario in usuarios:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{usuario['nome']}**")
                st.markdown(f"E-mail: {usuario['email']}")
            
            with col2:
                st.markdown(f"Perfil: {usuario['perfil']}")
                st.markdown(f"Último acesso: {usuario['ultimo_acesso']}")
            
            with col3:
                if st.button("Editar", key=f"edit_user_{usuario['id']}"):
                    st.warning("Funcionalidade não implementada na demonstração")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Adicionar novo usuário
        st.markdown("### Adicionar Novo Usuário")
        
        with st.form("form_novo_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_usuario = st.text_input("Nome completo")
                email_usuario = st.text_input("E-mail")
            
            with col2:
                senha_usuario = st.text_input("Senha", type="password")
                perfil_usuario = st.selectbox("Perfil", options=["terapeuta", "admin"])
            
            submitted = st.form_submit_button("Adicionar Usuário")
            
            if submitted:
                st.success(f"Usuário {nome_usuario} adicionado com sucesso!")
    
    with tabs[3]:  # Sobre
        st.markdown("<h2 class='sub-header'>Sobre o Sistema</h2>", unsafe_allow_html=True)
        
        # Informações sobre o sistema
        st.markdown(f"### NeuroBase v{APP_VERSION}")
        st.markdown("Sistema de Gestão em Psicomotricidade")
        
        st.markdown("#### Desenvolvido por")
        st.markdown("Equipe NeuroBase")
        
        st.markdown("#### Recursos")
        st.markdown("""
        - Cadastro e gerenciamento de pacientes
        - Registro de atendimentos
        - Avaliações e acompanhamento
        - Agendamentos
        - Relatórios
        - Sistema de backup
        """)
        
        st.markdown("#### Informações Técnicas")
        st.markdown(f"- Versão: {APP_VERSION}")
        st.markdown(f"- Data da última atualização: 14 de maio de 2025")
        st.markdown(f"- Plataforma: Python + Streamlit")
        st.markdown(f"- Banco de dados: SQLite")

###############################
# INICIALIZAÇÃO E EXECUÇÃO
###############################

def main():
    """Função principal de execução do aplicativo"""
    
    # Inicializar banco de dados se não existir
    inicializar_banco_dados()
    
    # Migrar dados de CSV para SQLite (se necessário)
    migrar_dados_csv_para_sqlite()
    
    # Inicializar sessão
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    # Verificar autenticação
    if not autenticacao():
        return
    
    # Configurar a barra lateral
    st.sidebar.markdown(f"### Bem-vindo, {st.session_state.usuario}!")
    st.sidebar.markdown("---")
    
    opcao_selecionada = st.sidebar.radio(
        "Navegação",
        ["Dashboard", "Pacientes", "Atendimentos", "Avaliações", "Agendamentos", "Relatórios", "Configurações"]
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair"):
        # Limpar estado da sessão e redirecionar para login
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
    
    # Mostrar a versão do sistema
    st.sidebar.markdown("<div class='version-info'>NeuroBase v" + APP_VERSION + "</div>", unsafe_allow_html=True)
    
    # Renderizar a página selecionada
    if opcao_selecionada == "Dashboard":
        mostrar_dashboard()
    elif opcao_selecionada == "Pacientes":
        mostrar_pacientes()
    elif opcao_selecionada == "Atendimentos":
        mostrar_atendimentos()
    elif opcao_selecionada == "Avaliações":
        mostrar_avaliacoes()
    elif opcao_selecionada == "Agendamentos":
        mostrar_agendamentos()
    elif opcao_selecionada == "Relatórios":
        mostrar_relatorios()
    elif opcao_selecionada == "Configurações":
        mostrar_configuracoes()

if __name__ == "__main__":
    main()
