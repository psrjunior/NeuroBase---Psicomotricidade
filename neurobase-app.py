import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
from PIL import Image
# Placeholder for external integrations
def sync_with_google_calendar(appt): pass
def send_whatsapp_report(patient_id, report): pass

# Config
db_path = 'data/neurobase.db'

st.set_page_config(page_title="NeuroBase - Psicomotricidade", page_icon="🧠", layout="wide")

# --------- DB ---------
def get_conn():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with get_conn() as conn:
        c = conn.cursor()
        # Patients
        c.execute('''CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            birth_date TEXT,
            diagnosis TEXT,
            support_level TEXT,
            anamnesis TEXT,
            preferences TEXT,
            calming TEXT,
            dislikes TEXT,
            triggers TEXT
        )''')
        # Stamps
        c.execute('''CREATE TABLE IF NOT EXISTS stamps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            image BLOB,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Sessions
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            therapist TEXT,
            skills TEXT,
            notes TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Evaluations
        c.execute('''CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            eval_type TEXT,
            therapist TEXT,
            results TEXT,
            recommendations TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Test results
        c.execute('''CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            test_name TEXT,
            raw_scores TEXT,
            interpreted_scores TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Appointments
        c.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            time TEXT,
            therapist TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Attendance calls
        c.execute('''CREATE TABLE IF NOT EXISTS attendance_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            call_date TEXT,
            type TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )''')
        # Suggested groups
        c.execute('''CREATE TABLE IF NOT EXISTS suggested_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            params TEXT,
            patients TEXT
        )''')
        conn.commit()

# Fetch helpers
def fetch_all(table, **filters):
    sql = f"SELECT * FROM {table}"
    params = []
    if filters:
        clauses = [f"{k}=?" for k in filters]
        params = list(filters.values())
        sql += " WHERE " + " AND ".join(clauses)
    with get_conn() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]

# JSON parse
def parse_json(s):
    try:
        return json.loads(s)
    except:
        return []

# --------- Pages ---------

def patients_page():
    st.title("Pacientes")
    if st.button("Novo Paciente"):
        st.session_state.show_new_patient = True
    if st.session_state.get('show_new_patient'):
        with st.form("form_patient"):
            name = st.text_input("Nome")
            birth = st.date_input("Data de Nascimento")
            diag = st.text_input("Diagnóstico")
            support = st.selectbox("Nível de Suporte", ["Nível 1","Nível 2","Nível 3"])
            anam = st.text_area("Anamnese")
            prefs = st.text_area("Preferências")
            calm = st.text_area("Coisas que acalmam")
            dis = st.text_area("Coisas que não gosta")
            trig = st.text_area("Gatilhos")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                with get_conn() as conn:
                    conn.execute("INSERT INTO patients (name,birth_date,diagnosis,support_level,anamnesis,preferences,calming,dislikes,triggers) VALUES (?,?,?,?,?,?,?,?,?)",
                                 (name, birth.strftime('%Y-%m-%d'), diag, support, anam, prefs, calm, dis, trig))
                    conn.commit()
                st.success("Paciente criado")
                st.session_state.show_new_patient = False
    # List patients
    for p in fetch_all('patients'):
        with st.expander(p['name']):
            st.write(f"📅 Nascimento: {p['birth_date']}")
            st.write(f"📋 Diagnóstico: {p['diagnosis']}")
            st.write(f"📒 Anamnese: {p['anamnesis']}")


def sessions_page():
    st.title("Atendimentos")
    patients = fetch_all('patients')
    patient_map = {p['id']:p['name'] for p in patients}
    if st.button("Nova Sessão"):
        st.session_state.show_new_session = True
    if st.session_state.get('show_new_session'):
        with st.form("form_session"):
            pid = st.selectbox("Paciente", options=[p['id'] for p in patients], format_func=lambda x:patient_map[x])
            date = st.date_input("Data")
            therapist = st.text_input("Terapeuta")
            skills = st.text_area("Habilidades Trabalhadas (vírgula-separadas)")
            notes = st.text_area("Notas/Descrição")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                with get_conn() as conn:
                    conn.execute("INSERT INTO sessions (patient_id,date,therapist,skills,notes) VALUES (?,?,?,?,?)",
                                 (pid, date.strftime('%Y-%m-%d'), therapist, skills, notes))
                    conn.commit()
                st.success("Sessão registrada")
                st.session_state.show_new_session = False
    # List sessions
    sessions = fetch_all('sessions')
    for s in sessions:
        with st.expander(f"{s['date']} - {patient_map.get(s['patient_id'],'')}"):
            st.write(f"Terapeuta: {s['therapist']}")
            st.write(f"Habilidades: {s['skills']}")
            st.write(f"Notas: {s['notes']}")


def evaluations_page():
    st.title("Avaliações")
    patients = fetch_all('patients')
    pmap = {p['id']:p['name'] for p in patients}
    if st.button("Nova Avaliação"):
        st.session_state.show_new_eval = True
    if st.session_state.get('show_new_eval'):
        with st.form("form_eval"):
            pid = st.selectbox("Paciente", [p['id'] for p in patients], format_func=lambda x:pmap[x])
            date = st.date_input("Data")
            etype = st.text_input("Tipo de Avaliação")
            therapist = st.text_input("Avaliador")
            results = st.text_area("Resultados")
            recs = st.text_area("Recomendações")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                with get_conn() as conn:
                    conn.execute("INSERT INTO evaluations (patient_id,date,eval_type,therapist,results,recommendations) VALUES (?,?,?,?,?,?)",
                                 (pid, date.strftime('%Y-%m-%d'), etype, therapist, results, recs))
                    conn.commit()
                st.success("Avaliação registrada")
                st.session_state.show_new_eval = False
    # List evaluations
    evals = fetch_all('evaluations')
    for e in evals:
        with st.expander(f"{e['date']} - {pmap.get(e['patient_id'],'')}"):
            st.write(f"Tipo: {e['eval_type']}")
            st.write(f"Avaliador: {e['therapist']}")
            st.write(f"Resultados: {e['results']}")
            st.write(f"Recomendações: {e['recommendations']}")


def tests_page():
    st.title("Testes Padronizados")
    patients = fetch_all('patients')
    pmap = {p['id']:p['name'] for p in patients}
    if st.button("Novo Resultado de Teste"):
        st.session_state.show_new_test = True
    if st.session_state.get('show_new_test'):
        with st.form("form_test"):
            pid = st.selectbox("Paciente", [p['id'] for p in patients], format_func=lambda x:pmap[x])
            date = st.date_input("Data")
            tname = st.text_input("Nome do Teste")
            raw = st.text_area("Raw Scores JSON")
            interp = st.text_area("Interpreted Scores JSON")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                with get_conn() as conn:
                    conn.execute("INSERT INTO test_results (patient_id,date,test_name,raw_scores,interpreted_scores) VALUES (?,?,?,?,?)",
                                 (pid, date.strftime('%Y-%m-%d'), tname, raw, interp))
                    conn.commit()
                st.success("Resultado de teste registrado")
                st.session_state.show_new_test = False
    # List tests
    tests = fetch_all('test_results')
    for t in tests:
        with st.expander(f"{t['date']} - {pmap.get(t['patient_id'],'')}: {t['test_name']}"):
            st.write(f"Raw: {t['raw_scores']}")
            st.write(f"Interpreted: {t['interpreted_scores']}")


def appointments_page():
    st.title("Agendamentos")
    patients = fetch_all('patients')
    pmap = {p['id']:p['name'] for p in patients}
    if st.button("Novo Agendamento"):
        st.session_state.show_new_appt = True
    if st.session_state.get('show_new_appt'):
        with st.form("form_appt"):
            pid = st.selectbox("Paciente", [p['id'] for p in patients], format_func=lambda x:pmap[x])
            date = st.date_input("Data")
            time = st.time_input("Hora")
            therapist = st.text_input("Terapeuta")
            status = st.selectbox("Status", ["Agendado","Confirmado","Concluído","Cancelado","Faltou"])
            notes = st.text_area("Notas")
            submitted = st.form_submit_button("Salvar")
            if submitted:
                with get_conn() as conn:
                    conn.execute("INSERT INTO appointments (patient_id,date,time,therapist,status,notes) VALUES (?,?,?,?,?,?)",
                                 (pid, date.strftime('%Y-%m-%d'), time.strftime('%H:%M'), therapist, status, notes))
                    conn.commit()
                st.success("Agendamento criado")
                st.session_state.show_new_appt = False
    # List appts
    appts = fetch_all('appointments')
    for a in appts:
        with st.expander(f"{a['date']} {a['time']} - {pmap.get(a['patient_id'],'')}"):
            st.write(f"Terapeuta: {a['therapist']}")
            st.write(f"Status: {a['status']}")
            st.write(f"Notas: {a['notes']}")


def grouping_page():
    st.title("Grupos Sugeridos")
    if st.button("Gerar Grupos"):
        patients = fetch_all('patients')
        # Simple grouping by diagnosis
        groups = {}
        for p in patients:
            groups.setdefault(p['diagnosis'], []).append(p['name'])
        for diag, names in groups.items():
            st.subheader(f"Grupo: {diag}")
            st.write(names)


def reminders_page():
    st.title("Lembretes e Chamadas")
    calls = fetch_all('attendance_calls')
    st.write(calls)
    # Automatic calls for missed sessions could be added here


def reports_page():
    st.title("Relatórios e Envio")
    patients = fetch_all('patients')
    pmap = {p['id']:p['name'] for p in patients}
    pid = st.selectbox("Paciente para relatório", [p['id'] for p in patients], format_func=lambda x:pmap[x])
    if st.button("Enviar Relatório via WhatsApp"):
        send_whatsapp_report(pid, {})
        st.success("Relatório enviado!")


def main():
    init_db()
    st.sidebar.title("NeuroBase")
    choice = st.sidebar.selectbox("Menu", [
        "Pacientes","Atendimentos","Avaliações","Testes",
        "Agendamentos","Grupos","Lembretes","Relatórios"
    ])
    if choice=="Pacientes": patients_page()
    elif choice=="Atendimentos": sessions_page()
    elif choice=="Avaliações": evaluations_page()
    elif choice=="Testes": tests_page()
    elif choice=="Agendamentos": appointments_page()
    elif choice=="Grupos": grouping_page()
    elif choice=="Lembretes": reminders_page()
    elif choice=="Relatórios": reports_page()

if __name__=="__main__":
    main()
