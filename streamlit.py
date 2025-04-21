import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# Configurações da página
st.set_page_config(
    page_title="PSM 2.0 - Monitoramento",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Melhorias gerais */
    [data-testid=stMetric] {
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Cabeçalhos coloridos */
    h1, h2, h3 {
        color: #2C3E50;
    }
    
    /* Sidebar estilizada */
    [data-testid=stSidebar] {
        background: linear-gradient(180deg, #4B79A1 0%, #283E51 100%);
    }
    
    .sidebar-title {
        color: white !important;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Alertas destacados */
    .stAlert {
        border-left: 4px solid #E74C3C;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Configurações
SIMULAR_LOGIN = True
MEDICOS = ['Dr. Silva - Cardiologia', 'Dra. Costa - Clínica Geral', 'Dr. Oliveira - Cirurgia']
COLOR_PALETTE = ['#3498DB', '#2ECC71', '#E74C3C', '#9B59B6', '#F1C40F']

# Inicialização da sessão
if 'PACIENTES' not in st.session_state:
    st.session_state.PACIENTES = ['Paciente 1 - Pós-Cirúrgico', 
                                 'Paciente 2 - Recuperação', 
                                 'Paciente 3 - Alta Médica']

if 'dados_acumulados' not in st.session_state:
    st.session_state.dados_acumulados = {}

if 'limites' not in st.session_state:
    st.session_state.limites = {
        'temperatura': (35.5, 37.5),
        'batimento_cardiaco': (60, 120),
        'pressao_sistolica': (90, 140),
        'pressao_diastolica': (60, 90),
        'glicose': (70, 180),
        'oxigenio': (95, 100)
    }

def detectar_anomalias(df):
    try:
        if len(df) < 5:
            df['Anomalia_IF'] = 1
            df['Anomalia_LOF'] = 1
            return df

        iso_forest = IsolationForest(contamination=0.3, random_state=42)
        anomalias_if = iso_forest.fit_predict(df[['batimento_cardiaco', 'temperatura']])
        
        n_neighbors = min(15, max(5, len(df)-1))
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.3)
        anomalias_lof = lof.fit_predict(df[['batimento_cardiaco', 'temperatura']])
        
        df['Anomalia_IF'] = anomalias_if
        df['Anomalia_LOF'] = anomalias_lof
        return df
    except Exception as e:
        st.error(f"Erro na detecção de anomalias: {str(e)}")
        return df
    
def processar_anomalias(df):
    anomalias = []
    if not df.empty and 'Anomalia_IF' in df.columns and 'Anomalia_LOF' in df.columns:
        for idx, row in df.iterrows():
            motivo = []
            if row['Anomalia_IF'] == -1 or row['Anomalia_LOF'] == -1:
                # Verificar parâmetros fora do normal
                if row['batimento_cardiaco'] > st.session_state.limites['batimento_cardiaco'][1]:
                    motivo.append("Batimento cardíaco elevado")
                if row['temperatura'] > st.session_state.limites['temperatura'][1]:
                    motivo.append("Febre")
                if row['batimento_cardiaco'] < st.session_state.limites['batimento_cardiaco'][0]:
                    motivo.append("Bradicardia")
                if row['temperatura'] < st.session_state.limites['temperatura'][0]:
                    motivo.append("Hipotermia")
                
                if not motivo:  # Se nenhum motivo óbvio, usar explicação genérica
                    motivo.append("Padrão anômalo detectado pelo modelo")
                
                anomalias.append({
                    "Data/Hora": row['timestamp'].strftime('%d/%m/%Y %H:%M:%S'),
                    "Batimento (BPM)": row['batimento_cardiaco'],
                    "Temperatura (°C)": f"{row['temperatura']:.1f}",
                    "Modelo Detectado": "IF + LOF" if (row['Anomalia_IF'] == -1 and row['Anomalia_LOF'] == -1) 
                                      else "Isolation Forest" if row['Anomalia_IF'] == -1 
                                      else "LOF",
                    "Motivo": ", ".join(motivo)
                })
    return pd.DataFrame(anomalias)

def generate_random_data(real_time=True, start=None, end=None):
    try:
        np.random.seed(int(time.time()))
        anomaly_ratio = 0.3
        activity_transition_prob = 0.2
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
            num_points = np.random.randint(5, 10)
            
            if paciente in st.session_state.dados_acumulados:
                ultimo_ts = st.session_state.dados_acumulados[paciente][0]['timestamp'].iloc[-1]
                timestamps = [ultimo_ts + timedelta(seconds=10*(i+1)) for i in range(num_points)]
            else:
                timestamps = [now - timedelta(seconds=10*i) for i in range(num_points)]
        else:
            start_dt = datetime.combine(start[0], start[1])
            end_dt = datetime.combine(end[0], end[1])
            
            if end_dt < start_dt:
                st.error("Data final deve ser após a data inicial.")
                return pd.DataFrame(), pd.DataFrame()
            
            delta = end_dt - start_dt
            total_seconds = delta.total_seconds()
            num_points = max(int(total_seconds // 60), 1)
            timestamps = [start_dt + timedelta(minutes=i) for i in range(num_points)]

        num_anomaly = max(1, int(num_points * anomaly_ratio))
        anomaly_indices = np.random.choice(num_points, num_anomaly, replace=False)

        data = {
            'timestamp': timestamps,
            'temperatura': np.where(
                np.isin(np.arange(num_points), anomaly_indices),
                np.random.normal(39.5, 0.8, num_points),
                np.random.normal(36.5, 0.3, num_points)
            ),
            'batimento_cardiaco': np.where(
                np.isin(np.arange(num_points), anomaly_indices),
                np.random.normal(160, 20, num_points),
                np.random.normal(80, 5, num_points)
            ).astype(int),
            'atividade': self_generate_activity(num_points, activity_transition_prob)
        }

        for param in ['pressao_sistolica', 'pressao_diastolica', 'glicose', 'oxigenio']:
            data[param] = np.random.normal(
                base_params[param][0], 
                base_params[param][1], 
                num_points
            ).astype(int)

        data['dispositivo_estado'] = ['Ativo'] * num_points

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = detectar_anomalias(df)

        atividades = processar_atividades(df)
        df_atividades = pd.DataFrame(atividades)
        return df, df_atividades

    except Exception as e:
        st.error(f"Erro na geração de dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def processar_atividades(df):
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

    if current_activity is not None:
        current_activity['end'] = df.timestamp.iloc[-1]
        duration = (current_activity['end'] - current_activity['start']).total_seconds() / 60
        atividades.append({
            "Tarefa": "Atividade Física",
            "Início": current_activity['start'],
            "Fim": current_activity['end'],
            "Duração (min)": duration
        })
    
    return atividades

def self_generate_activity(length, transition_prob):
    activity = np.zeros(length)
    current_state = 0
    for i in range(length):
        if np.random.rand() < transition_prob:
            current_state = 1 - current_state
        activity[i] = current_state
    return activity.astype(int)

def fetch_data():
    try:
        if tempo_real:
            novo_df, novo_atividades = generate_random_data(real_time=True)
            
            if paciente not in st.session_state.dados_acumulados:
                combined_df = novo_df
                combined_ativ = novo_atividades
            else:
                old_df, old_ativ = st.session_state.dados_acumulados[paciente]
                combined_df = pd.concat([old_df, novo_df]).reset_index(drop=True)
                combined_ativ = pd.concat([old_ativ, novo_atividades]).reset_index(drop=True)
            
            combined_df = detectar_anomalias(combined_df)
            st.session_state.dados_acumulados[paciente] = (combined_df, combined_ativ)
            return combined_df, combined_ativ
        else:
            df_historico, df_ativ_historico = generate_random_data(
                real_time=False,
                start=(data_inicio, hora_inicio),
                end=(data_fim, hora_fim)
            )
            return df_historico, df_ativ_historico
            
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()
    
# Funções gráficas
def create_pressure_chart(df):
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['pressao_sistolica'],
            name="Sistólica",
            line=dict(color=COLOR_PALETTE[3], width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['pressao_diastolica'],
            name="Diastólica",
            line=dict(color=COLOR_PALETTE[0], width=2)
        ))
    fig.update_layout(
        title="Pressão Arterial",
        yaxis_title="mmHg",
        template="plotly_white",
        height=300
    )
    return fig

def create_glucose_chart(df):
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['glicose'],
            name="Glicose",
            line=dict(color=COLOR_PALETTE[2], width=2)
        ))
    fig.update_layout(
        title="Níveis de Glicose",
        yaxis_title="mg/dL",
        template="plotly_white",
        height=300
    )
    return fig

def create_gantt_chart(df_atividades):
    fig = go.Figure()
    if not df_atividades.empty:
        for idx, row in df_atividades.iterrows():
            fig.add_trace(go.Scatter(
                x=[row["Início"], row["Fim"]],
                y=[row["Tarefa"], row["Tarefa"]],
                mode='lines',
                line=dict(color=COLOR_PALETTE[1], width=20),
                hoverinfo='text',
                text=[f"Duração: {row['Duração (min)']:.1f} minutos<br>Início: {row['Início']}<br>Fim: {row['Fim']}"],
                name=''
            ))
        fig.update_layout(
            title='Cronograma de Atividade Física',
            xaxis=dict(title='Tempo', type='date'),
            yaxis=dict(visible=False),
            height=300,
            template="plotly_white",
            showlegend=False
        )
    else:
        fig.add_annotation(
            text="Nenhuma atividade física registrada",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False
        )
    return fig
    
def check_alertas(df):
    alertas = []
    if df.empty:
        return alertas
    ultimo = df.iloc[-1]
    
    for parametro, (minimo, maximo) in st.session_state.limites.items():
        valor = ultimo[parametro]
        if valor < minimo:
            alertas.append(f"🔻 {parametro.capitalize()} baixa: {valor:.2f} (Mín: {minimo})")
        elif valor > maximo:
            alertas.append(f"🔺 {parametro.capitalize()} alta: {valor:.2f} (Máx: {maximo})")
    
    return alertas

with st.sidebar:
    st.markdown('<h1 class="sidebar-title">🏥 PSM 2.0</h1>', unsafe_allow_html=True)
    
    if SIMULAR_LOGIN:
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            
        if not st.session_state.logged_in:
            with st.form("login_form"):
                with st.container():
                    st.markdown("""
                    <style>
                        div[data-testid="stForm"] > div:first-child {
                            border-radius: 10px;
                            padding: 20px;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    usuario = st.selectbox("👨⚕️ Médico", MEDICOS)
                    senha = st.text_input("🔒 Senha", type="password")
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.form_submit_button("🚪 **Login**", use_container_width=True):
                            st.session_state.logged_in = True
                            st.session_state.medico = usuario
                            st.rerun()
                st.stop()
        else:
            st.success(f"👤 Logado como: {st.session_state.medico}", icon="✅")
            if st.button("🚪 Sair"):
                st.session_state.logged_in = False
                del st.session_state.medico
                st.rerun()

    st.subheader("⚙️ Configurações")
    
    with st.expander("👥 Gerenciar Pacientes"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Editar", use_container_width=True):
                st.session_state.editando_pacientes = True
        with col2:
            if st.button("➕ Novo", use_container_width=True):
                st.session_state.adicionando_paciente = True

        if st.session_state.get('editando_pacientes'):
            with st.form("editar_pacientes_form"):
                pacientes_texto = st.text_area("Lista de Pacientes", 
                                            value="\n".join(st.session_state.PACIENTES),
                                            height=150)
                if st.form_submit_button("💾 Salvar"):
                    st.session_state.PACIENTES = [p.strip() for p in pacientes_texto.split("\n") if p.strip()]
                    del st.session_state.editando_pacientes
                    st.rerun()
                if st.form_submit_button("❌ Cancelar"):
                    del st.session_state.editando_pacientes
                    st.rerun()

        if st.session_state.get('adicionando_paciente'):
            with st.form("adicionar_paciente_form"):
                novo_paciente = st.text_input("Nome do Paciente")
                if st.form_submit_button("✅ Adicionar"):
                    if novo_paciente.strip():
                        st.session_state.PACIENTES.append(novo_paciente.strip())
                        del st.session_state.adicionando_paciente
                        st.rerun()
                if st.form_submit_button("❌ Cancelar"):
                    del st.session_state.adicionando_paciente
                    st.rerun()

    with st.expander("📊 Configurar Limites"):
        with st.form("limites_form"):
            novos_limites = {}
            for param, (min_val, max_val) in st.session_state.limites.items():
                col1, col2 = st.columns(2)
                novo_min = col1.number_input(f"Mín {param}", value=min_val)
                novo_max = col2.number_input(f"Máx {param}", value=max_val)
                novos_limites[param] = (novo_min, novo_max)
            
            if st.form_submit_button("💾 Salvar Limites"):
                st.session_state.limites = novos_limites
                st.success("Limites atualizados com sucesso!")

    paciente = st.selectbox('👨⚕️ Paciente', st.session_state.PACIENTES)
    tempo_real = st.checkbox('📡 Dados Simulados', True)
    
    if not tempo_real:
        st.subheader("📅 Período Histórico")
        col1, col2 = st.columns(2)
        data_inicio = col1.date_input('Data Inicial')
        hora_inicio = col2.time_input('Hora Inicial')
        data_fim = col1.date_input('Data Final')
        hora_fim = col2.time_input('Hora Final')

def render_visao_geral(df):
    st.header(f"📊 Monitoramento - {paciente}")
    medico = st.session_state.get('medico', 'Nenhum médico logado')
    st.subheader(f"👨⚕️ Médico Responsável: {medico}")
    
    cols = st.columns(5)
    metricas = {
        '🌡️ Temperatura': f"{df['temperatura'].iloc[-1]:.1f}°C" if not df.empty else 'N/A',
        '💓 Batimento': f"{df['batimento_cardiaco'].iloc[-1]} BPM" if not df.empty else 'N/A',
        '🩸 Pressão': f"{df['pressao_sistolica'].iloc[-1]}/{df['pressao_diastolica'].iloc[-1]} mmHg" if not df.empty else 'N/A',
        '🩸 Glicose': f"{df['glicose'].iloc[-1]} mg/dL" if not df.empty else 'N/A',
        '💨 Oxigênio': f"{df['oxigenio'].iloc[-1]}% SpO2" if not df.empty else 'N/A'
    }
    
    for (nome, valor), col in zip(metricas.items(), cols):
        col.metric(nome, valor)

def create_vital_chart(df):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                       subplot_titles=("Temperatura Corporal", "Batimento Cardíaco", "Oxigênio no Sangue"))
    
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['temperatura'],
            name="Temperatura",
            line=dict(color=COLOR_PALETTE[0], width=2)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['batimento_cardiaco'],
            name="BPM",
            line=dict(color=COLOR_PALETTE[1], width=2)
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['oxigenio'],
            name="SpO2",
            line=dict(color=COLOR_PALETTE[2], width=2)
        ), row=3, col=1)
    
    fig.update_layout(height=600, template="plotly_white", showlegend=False)
    return fig

def create_anomaly_chart(df):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Isolation Forest', 'LOF'))
    
    if not df.empty and 'Anomalia_IF' in df.columns and 'Anomalia_LOF' in df.columns:
        df['timestamp_str'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        fig.add_trace(go.Scatter(
            x=df['batimento_cardiaco'],
            y=df['temperatura'],
            mode='markers',
            marker=dict(
                color=np.where(df['Anomalia_IF'] == -1, COLOR_PALETTE[2], COLOR_PALETTE[1]),
                size=8,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=df.apply(lambda row: f"Data: {row['timestamp_str']}<br>Batimento: {row['batimento_cardiaco']}<br>Temperatura: {row['temperatura']:.1f}", axis=1),
            hoverinfo='text',
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['batimento_cardiaco'],
            y=df['temperatura'],
            mode='markers',
            marker=dict(
                color=np.where(df['Anomalia_LOF'] == -1, COLOR_PALETTE[2], COLOR_PALETTE[1]),
                size=8,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=df.apply(lambda row: f"Data: {row['timestamp_str']}<br>Batimento: {row['batimento_cardiaco']}<br>Temperatura: {row['temperatura']:.1f}", axis=1),
            hoverinfo='text',
            showlegend=False
        ), row=1, col=2)
        
    fig.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Batimento Cardíaco (BPM)",
        yaxis_title="Temperatura (°C)",
        xaxis2_title="Batimento Cardíaco (BPM)",
        yaxis2_title="Temperatura (°C)",
        showlegend=False
    )
    return fig

def render_alertas(alertas):
    with st.container():
        st.subheader("🚨 Alertas em Tempo Real")
        if alertas:
            for alerta in alertas:
                st.error(alerta, icon="⚠️")
        else:
            st.success("✅ Todos os parâmetros dentro da normalidade", icon="✅")

# Execução Principal
try:
    if 'current_paciente' not in st.session_state:
        st.session_state.current_paciente = paciente
    
    if st.session_state.current_paciente != paciente:
        if paciente in st.session_state.dados_acumulados:
            del st.session_state.dados_acumulados[paciente]
        st.session_state.current_paciente = paciente
    
    df, df_atividades = fetch_data()
    alertas = check_alertas(df)
    
    if df.empty:
        st.warning("⚠️ Nenhum dado disponível para o período selecionado")
    else:
        render_visao_geral(df)
        render_alertas(alertas)
        
        st.subheader("📈 Visualização de Dados")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sinais Vitais", "Pressão", "Glicose", "Atividades", "Anomalias"])
        
        with tab1:
            st.plotly_chart(create_vital_chart(df), use_container_width=True)
        
        with tab2:
            st.plotly_chart(create_pressure_chart(df), use_container_width=True)
        
        with tab3:
            st.plotly_chart(create_glucose_chart(df), use_container_width=True)
        
        with tab4:
            st.plotly_chart(create_gantt_chart(df_atividades), use_container_width=True)
        
        with tab5:  
            st.plotly_chart(create_anomaly_chart(df), use_container_width=True)
            
            df_anomalias = processar_anomalias(df)
            if not df_anomalias.empty:
                st.subheader("📋 Detalhes das Anomalias Detectadas")
                st.dataframe(
                    df_anomalias,
                    column_config={
                        "Data/Hora": "Data/Hora",
                        "Batimento (BPM)": st.column_config.NumberColumn(format="%d"),
                        "Temperatura (°C)": st.column_config.NumberColumn(format="%.1f"),
                        "Modelo Detectado": "Modelo",
                        "Motivo": "Motivo"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("ℹ️ Nenhuma anomalia detectada no período selecionado")

    st.divider()
    with st.expander("💾 Exportar Dados"):
        formato = st.selectbox("Formato", ["CSV", "JSON"])
        if st.button("Gerar Arquivo", type="primary"):
            if not df.empty:
                with st.spinner("Gerando arquivo..."):
                    if formato == "CSV":
                        csv = df.to_csv(index=False)
                        st.download_button("⬇️ Download CSV", csv, f"dados_{paciente}.csv")
                    else:
                        json = df.to_json(indent=2)
                        st.download_button("⬇️ Download JSON", json, f"dados_{paciente}.json")
            else:
                st.warning("Nenhum dado disponível para exportar")

    if tempo_real:
        next_update = datetime.now() + timedelta(seconds=60)
        st.caption(f"⏳ Próxima atualização: {next_update.strftime('%H:%M:%S')}")
        time.sleep(60)
        st.rerun()

except Exception as e:
    st.error(f"Erro crítico: {str(e)}")
