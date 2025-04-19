import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# Configurações
SIMULAR_LOGIN = True
MEDICOS = ['Dr. Silva - Cardiologia', 'Dra. Costa - Clínica Geral', 'Dr. Oliveira - Cirurgia']

# Inicialização da sessão para pacientes
if 'PACIENTES' not in st.session_state:
    st.session_state.PACIENTES = ['Paciente 1 - Pós-Cirúrgico', 
                                 'Paciente 2 - Recuperação', 
                                 'Paciente 3 - Alta Médica']

def detectar_anomalias(df):
    try:
        if len(df) < 2:
            return df
        
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomalias_if = iso_forest.fit_predict(df[['batimento_cardiaco', 'temperatura']])
        
        n_neighbors = min(20, max(2, len(df)-1))
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.1)
        anomalias_lof = lof.fit_predict(df[['batimento_cardiaco', 'temperatura']])
        
        df['Anomalia_IF'] = anomalias_if
        df['Anomalia_LOF'] = anomalias_lof
        return df
    
    except Exception as e:
        st.error(f"Erro na detecção de anomalias: {str(e)}")
        return df

def generate_random_data(real_time=True, start=None, end=None):
    try:
        np.random.seed(int(time.time()))
        
        # Novo: Parâmetros de aleatorização
        anomaly_ratio = 0.1  # 10% de anomalias
        activity_states = [0, 1]
        activity_transition_prob = 0.2  # Probabilidade de mudar de estado
        
        base_params = {
            'temperatura': (36.5, 0.5),
            'batimento_cardiaco': (80, 15),
            'pressao_sistolica': (120, 10),
            'pressao_diastolica': (80, 5),
            'glicose': (100, 20),
            'oxigenio': (98, 1)
        }
        
        if real_time:
            now = datetime.now()
            num_points = 50
            timestamps = [now - timedelta(seconds=10*i) for i in range(num_points)]
            
            # Gerar anomalias randomizadas
            num_anomaly = max(1, int(num_points * anomaly_ratio))
            anomaly_indices = np.random.choice(num_points, num_anomaly, replace=False)
            
            data = {
                'timestamp': timestamps,
                'temperatura': np.random.normal(36.5, 0.5, num_points),
                'batimento_cardiaco': np.random.normal(80, 5, num_points).astype(int),
                # Aplicar anomalias
                'temperatura': np.where(np.isin(np.arange(num_points), anomaly_indices),
                                   np.random.normal(38.5, 0.5, num_points),
                                   np.random.normal(36.5, 0.5, num_points)),
                'batimento_cardiaco': np.where(np.isin(np.arange(num_points), anomaly_indices),
                                      np.random.normal(150, 10, num_points),
                                      np.random.normal(80, 5, num_points)).astype(int),
                # Gerar atividade física mais realista
                'atividade': self_generate_activity(num_points, activity_transition_prob)
            }
        else:
            start_dt = datetime.combine(start[0], start[1])
            end_dt = datetime.combine(end[0], end[1])
            
            if end_dt < start_dt:
                st.error("Data final deve ser após a data inicial.")
                return pd.DataFrame(), pd.DataFrame()
            
            delta = end_dt - start_dt
            total_seconds = delta.total_seconds()
            num_points = max(int(total_seconds / 60), 1)
            
            timestamps = [start_dt + timedelta(seconds=60*i) for i in range(num_points)]
            
            # Gerar anomalias randomizadas
            num_anomaly = max(1, int(num_points * anomaly_ratio))
            anomaly_indices = np.random.choice(num_points, num_anomaly, replace=False)
            
            data = {
                'timestamp': timestamps,
                'temperatura': np.where(np.isin(np.arange(num_points), anomaly_indices),
                                   np.random.normal(38.5, 0.5, num_points),
                                   np.random.normal(36.5, 0.5, num_points)),
                'batimento_cardiaco': np.where(np.isin(np.arange(num_points), anomaly_indices),
                                      np.random.normal(150, 10, num_points),
                                      np.random.normal(80, 5, num_points)).astype(int),
                'atividade': self_generate_activity(num_points, activity_transition_prob)
            }
        
        # Gerar outros parâmetros
        for param in ['pressao_sistolica', 'pressao_diastolica', 'glicose', 'oxigenio']:
            data[param] = np.random.normal(base_params[param][0], base_params[param][1], num_points).astype(int)
        
        data['dispositivo_estado'] = ['Ativo'] * num_points
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Detecção de anomalias
        df = detectar_anomalias(df)
        
        # Geração do Gantt Chart melhorado
        atividades = []
        current_activity = None
        
        for i in range(len(df)):
            if df.atividade.iloc[i] == 1 and current_activity is None:
                current_activity = {'start': df.timestamp.iloc[i]}
            elif df.atividade.iloc[i] == 0 and current_activity is not None:
                current_activity['end'] = df.timestamp.iloc[i]
                duration = (current_activity['end'] - current_activity['start']).total_seconds() / 60
                if duration > 0:
                    atividades.append({
                        "Tarefa": "Atividade Física",
                        "Início": current_activity['start'],
                        "Fim": current_activity['end'],
                        "Duração (min)": duration
                    })
                current_activity = None
        
        # Registrar atividade em andamento
        if current_activity is not None:
            current_activity['end'] = df.timestamp.iloc[-1]
            duration = (current_activity['end'] - current_activity['start']).total_seconds() / 60
            atividades.append({
                "Tarefa": "Atividade Física",
                "Início": current_activity['start'],
                "Fim": current_activity['end'],
                "Duração (min)": duration
            })
        
        df_atividades = pd.DataFrame(atividades)
        return df, df_atividades
    
    except Exception as e:
        st.error(f"Erro na geração de dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

# Nova função para gerar atividade física realista
def self_generate_activity(length, transition_prob):
    activity = np.zeros(length)
    current_state = 0
    for i in range(length):
        if np.random.rand() < transition_prob:
            current_state = 1 - current_state  # Alterna estado
        activity[i] = current_state
    return activity.astype(int)

def fetch_data():
    try:
        if tempo_real:
            return generate_random_data(real_time=True)
        else:
            return generate_random_data(real_time=False, 
                                      start=(data_inicio, hora_inicio),
                                      end=(data_fim, hora_fim))
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def check_alertas(df):
    alertas = []
    if df.empty:
        return alertas
    ultimo = df.iloc[-1]
    
    limites = {
        'temperatura': (35.5, 37.5),
        'batimento_cardiaco': (60, 120),
        'pressao_sistolica': (90, 140),
        'pressao_diastolica': (60, 90),
        'glicose': (70, 180),
        'oxigenio': (95, 100)
    }
    
    for parametro, (minimo, maximo) in limites.items():
        valor = ultimo[parametro]
        if valor < minimo:
            alertas.append(f"{parametro.capitalize()} baixo: {valor} (Mín: {minimo})")
        elif valor > maximo:
            alertas.append(f"{parametro.capitalize()} alto: {valor} (Máx: {maximo})")
    
    return alertas

with st.sidebar:
    st.title('PSM 2.0 - Os Suricatos Cibernéticos')
    
    if SIMULAR_LOGIN:
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            
        if not st.session_state.logged_in:
            with st.form("login_form"):
                usuario = st.selectbox("Médico", MEDICOS)
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Login"):
                    st.session_state.logged_in = True
                    st.session_state.medico = usuario
                    st.rerun()
            st.stop()
    
    st.subheader("Configurações de Monitoramento")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Editar Pacientes"):
            st.session_state.editando_pacientes = True
    with col2:
        if st.button("➕ Adicionar Paciente"):
            st.session_state.adicionando_paciente = True

    if st.session_state.get('editando_pacientes'):
        with st.form("editar_pacientes_form"):
            pacientes_texto = st.text_area("Lista de Pacientes (um por linha)", 
                                         value="\n".join(st.session_state.PACIENTES),
                                         height=150)
            if st.form_submit_button("Salvar Alterações"):
                st.session_state.PACIENTES = [p.strip() for p in pacientes_texto.split("\n") if p.strip()]
                del st.session_state.editando_pacientes
                st.rerun()
            if st.form_submit_button("Cancelar"):
                del st.session_state.editando_pacientes
                st.rerun()

    if st.session_state.get('adicionando_paciente'):
        with st.form("adicionar_paciente_form"):
            novo_paciente = st.text_input("Nome do Novo Paciente")
            if st.form_submit_button("Adicionar"):
                if novo_paciente.strip():
                    st.session_state.PACIENTES.append(novo_paciente.strip())
                    del st.session_state.adicionando_paciente
                    st.rerun()
            if st.form_submit_button("Cancelar"):
                del st.session_state.adicionando_paciente
                st.rerun()

    paciente = st.selectbox('Paciente', st.session_state.PACIENTES)
    tempo_real = st.checkbox('Monitoramento em tempo real')
    
    if not tempo_real:
        col1, col2 = st.columns(2)
        data_inicio = col1.date_input('Data inicial')
        hora_inicio = col2.time_input('Hora inicial')
        data_fim = col1.date_input('Data final')
        hora_fim = col2.time_input('Hora final')

def render_visao_geral(df):
    st.header(f"Monitoramento - {paciente}")
    st.subheader(f"Médico Responsável: {st.session_state.medico}")
    
    cols = st.columns(5)
    metricas = {
        'temperatura': f"{df['temperatura'].iloc[-1]:.1f}°C" if not df.empty else 'N/A',
        'batimento_cardiaco': f"{df['batimento_cardiaco'].iloc[-1]} BPM" if not df.empty else 'N/A',
        'pressao': f"{df['pressao_sistolica'].iloc[-1]}/{df['pressao_diastolica'].iloc[-1]} mmHg" if not df.empty else 'N/A',
        'glicose': f"{df['glicose'].iloc[-1]} mg/dL" if not df.empty else 'N/A',
        'oxigenio': f"{df['oxigenio'].iloc[-1]}% SpO2" if not df.empty else 'N/A'
    }
    
    for (nome, valor), col in zip(metricas.items(), cols):
        col.metric(nome.capitalize(), valor)

def create_vital_chart(df):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                       subplot_titles=("Temperatura Corporal", "Batimento Cardíaco", "Oxigênio no Sangue"))
    
    if not df.empty:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperatura'],
                      name="Temperatura (°C)", line=dict(color='#FF6B6B')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['batimento_cardiaco'],
                      name="BPM", line=dict(color='#4ECDC4')), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['oxigenio'],
                      name="SpO2 (%)", line=dict(color='#45B7D1')), row=3, col=1)
    else:
        for i in range(1,4):
            fig.add_annotation(text="Sem dados disponíveis",
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False,
                              row=i, col=1)
    
    fig.update_layout(height=600, showlegend=False)
    return fig

def create_pressure_chart(df):
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pressao_sistolica'],
                             name="Sistólica",
                             line=dict(color='#3498DB')))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pressao_diastolica'],
                             name="Diastólica",
                             line=dict(color='#2980B9')))
    else:
        fig.add_annotation(text="Sem dados disponíveis",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
    fig.update_layout(title="Pressão Arterial",
                    yaxis_title="mmHg",
                    height=300)
    return fig

def create_glucose_chart(df):
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['glicose'],
                             name="Glicose",
                             line=dict(color='#E74C3C')))
    else:
        fig.add_annotation(text="Sem dados disponíveis",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
    fig.update_layout(title="Níveis de Glicose",
                    yaxis_title="mg/dL",
                    height=300)
    return fig

def create_gantt_chart(df_atividades):
    fig = go.Figure()
    
    if not df_atividades.empty:
        for idx, row in df_atividades.iterrows():
            fig.add_trace(go.Scatter(
                x=[row["Início"], row["Fim"]],
                y=[row["Tarefa"], row["Tarefa"]],
                mode='lines',
                line=dict(color='#2ECC71', width=20),
                hoverinfo='text',
                text=[f"Duração: {row['Duração (min)']:.1f} minutos"],
                name='Atividade Física'
            ))
        
        fig.update_layout(
            title='Cronograma de Atividade Física',
            xaxis=dict(title='Tempo', type='date'),
            yaxis=dict(visible=False),
            height=300,
            showlegend=False
        )
    else:
        fig.add_annotation(text="Nenhuma atividade física registrada no período",
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
    
    return fig

def create_anomaly_chart(df):
    try:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Isolation Forest', 'LOF'))
        
        if not df.empty and 'Anomalia_IF' in df.columns and 'Anomalia_LOF' in df.columns:
            # Gráfico Isolation Forest
            fig.add_trace(go.Scatter(
                x=df['batimento_cardiaco'],
                y=df['temperatura'],
                mode='markers',
                marker=dict(
                    color=np.where(df['Anomalia_IF'] == -1, '#FF0000', '#00FF00'),
                    size=8,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name='IF',
                showlegend=False
            ), row=1, col=1)
            
            # Gráfico LOF
            fig.add_trace(go.Scatter(
                x=df['batimento_cardiaco'],
                y=df['temperatura'],
                mode='markers',
                marker=dict(
                    color=np.where(df['Anomalia_LOF'] == -1, '#FF0000', '#00FF00'),
                    size=8,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name='LOF',
                showlegend=False
            ), row=1, col=2)
            
            fig.update_layout(
                height=400,
                title_text="Detecção de Anomalias",
                xaxis_title="Batimento Cardíaco (BPM)",
                yaxis_title="Temperatura (°C)",
                xaxis2_title="Batimento Cardíaco (BPM)",
                yaxis2_title="Temperatura (°C)"
            )
        else:
            fig.add_annotation(text="Dados insuficientes para análise de anomalias",
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False)
        
        return fig
    
    except Exception as e:
        st.error(f"Erro ao criar gráfico de anomalias: {str(e)}")
        return go.Figure()

def render_graficos(df, df_atividades):
    st.subheader("Análise Temporal")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sinais Vitais", "Pressão Arterial", "Glicose", "Atividade Física", "Anomalias"])
    
    with tab1:
        st.plotly_chart(create_vital_chart(df), use_container_width=True)
    
    with tab2:
        st.plotly_chart(create_pressure_chart(df), use_container_width=True)
    
    with tab3:
        st.plotly_chart(create_glucose_chart(df), use_container_width=True)
    
    with tab4:
        st.plotly_chart(create_gantt_chart(df_atividades), use_container_width=True)
        if not df_atividades.empty:
            st.dataframe(df_atividades[['Início', 'Fim', 'Duração (min)']].style.format({
                'Início': lambda t: t.strftime('%H:%M:%S'),
                'Fim': lambda t: t.strftime('%H:%M:%S'),
                'Duração (min)': '{:.1f}'
            }), height=200)
        else:
            st.info("Nenhum registro de atividade física no período selecionado")
    
    with tab5:
        st.plotly_chart(create_anomaly_chart(df), use_container_width=True)
        if not df.empty and 'Anomalia_IF' in df.columns and 'Anomalia_LOF' in df.columns:
            anomalias_if = df[df['Anomalia_IF'] == -1]
            anomalias_lof = df[df['Anomalia_LOF'] == -1]
            
            st.subheader("Detalhes das Anomalias")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Isolation Forest**")
                if not anomalias_if.empty:
                    st.dataframe(anomalias_if[['timestamp', 'batimento_cardiaco', 'temperatura']].rename(columns={
                        'timestamp': 'Horário',
                        'batimento_cardiaco': 'BPM',
                        'temperatura': 'Temperatura'
                    }))
                else:
                    st.info("Nenhuma anomalia detectada pelo Isolation Forest")
            with col2:
                st.write("**LOF**")
                if not anomalias_lof.empty:
                    st.dataframe(anomalias_lof[['timestamp', 'batimento_cardiaco', 'temperatura']].rename(columns={
                        'timestamp': 'Horário',
                        'batimento_cardiaco': 'BPM',
                        'temperatura': 'Temperatura'
                    }))
                else:
                    st.info("Nenhuma anomalia detectada pelo LOF")
        else:
            st.info("Dados insuficientes para análise de anomalias")
        
        st.info("""
        **Legenda:**
        - Vermelho: Anomalia detectada
        - Verde: Valores normais
        """)

def render_alertas(alertas):
    st.subheader("Sistema de Alertas")
    if alertas:
        for alerta in alertas:
            st.error(f"⚠️ {alerta}", icon="🚨")
    else:
        st.success("Nenhum alerta crítico detectado", icon="✅")

if __name__ == "__main__":
    try:
        df, df_atividades = fetch_data()
        alertas = check_alertas(df)
        
        if df.empty:
            st.warning("Nenhum dado disponível para o período selecionado.")
        else:
            render_visao_geral(df)
            render_graficos(df, df_atividades)
            render_alertas(alertas)
        
        # Apenas UM expander para exportação
        st.divider()
        with st.expander("Exportação de Dados"):
            formato = st.selectbox("Formato de exportação", ["CSV", "JSON"])
            if st.button("Gerar Arquivo"):
                if not df.empty:
                    if formato == "CSV":
                        csv = df.to_csv(index=False)
                        st.download_button("Download CSV", csv, f"dados_{paciente}.csv")
                    else:
                        json = df.to_json(indent=2)
                        st.download_button("Download JSON", json, f"dados_{paciente}.json")
                else:
                    st.warning("Nenhum dado para exportar.")
        
        if tempo_real:
            time.sleep(10)
            st.rerun()
            
    except NameError as e:
        st.error(f"Erro de configuração: {str(e)}")
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")