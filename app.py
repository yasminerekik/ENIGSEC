import streamlit as st
import pickle
import pandas as pd
import sqlite3
import time
import matplotlib.pyplot as plt
import threading
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid
from streamlit_option_menu import option_menu
import base64
from PIL import Image
import io
import uuid

# Set page configuration
st.set_page_config(
    page_title="ENIGSEC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Charger le modèle Random Forest
@st.cache_resource
def load_model():
    with open('selected_randomforest.pkl', 'rb') as file:
        return pickle.load(file)

model = load_model()

# Connexion à la base de données SQLite
conn = sqlite3.connect("database/ids_data.db", check_same_thread=False)
cursor = conn.cursor()

# Définir les caractéristiques (features) du modèle
selected_features = ['duration', 'src_bytes', 'dst_bytes', 'wrong_fragment', 'num_failed_logins',
                     'logged_in', 'count', 'srv_count', 'dst_host_srv_serror_rate', 'neptune']

# Custom CSS with animations and modern design
def local_css():
    css = """
    <style>
        /* Custom fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Base styling */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main container */
        .main {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        
        /* Dashboard title */
        .dashboard-title {
            background: linear-gradient(90deg, #0d6efd, #20c997);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-align: center;
            animation: fadeIn 1.5s ease-in-out;
        }
        
        /* Subtitle */
        .dashboard-subtitle {
            color: #6c757d;
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 300;
        }
        
        /* Cards */
        .card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .card-header {
            color: #0d6efd;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 10px;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active {
            background-color: #20c997;
            box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.2);
            animation: pulse 2s infinite;
        }
        
        .status-inactive {
            background-color: #6c757d;
        }
        
        .status-warning {
            background-color: #ffc107;
        }
        
        .status-danger {
            background-color: #dc3545;
            animation: pulseDanger 1s infinite;
        }
        
        /* Normal traffic */
        .normal {
            color: #198754;
            font-weight: 500;
            background-color: rgba(25, 135, 84, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            animation: fadeInGreen 0.5s ease-out;
        }
        
        /* Anomaly */
        .anomaly {
            color: #dc3545;
            font-weight: 500;
            background-color: rgba(220, 53, 69, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            animation: fadeInRed 0.5s ease-out;
        }
        
        /* Animations */
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(32, 201, 151, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(32, 201, 151, 0); }
            100% { box-shadow: 0 0 0 0 rgba(32, 201, 151, 0); }
        }
        
        @keyframes pulseDanger {
            0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }
            100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInGreen {
            from { opacity: 0; background-color: rgba(25, 135, 84, 0); }
            to { opacity: 1; background-color: rgba(25, 135, 84, 0.1); }
        }
        
        @keyframes fadeInRed {
            from { opacity: 0; background-color: rgba(220, 53, 69, 0); }
            to { opacity: 1; background-color: rgba(220, 53, 69, 0.1); }
        }
        
        /* Dashboard stats */
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            height: 100%;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .stat-normal .stat-value {
            color: #198754;
        }
        
        .stat-anomaly .stat-value {
            color: #dc3545;
        }
        
        .stat-total .stat-value {
            color: #0d6efd;
        }
        
        .stat-rate .stat-value {
            color: #6f42c1;
        }
        
        /* Control buttons */
        .stButton > button {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: 500;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background-color: #0b5ed7;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Tables */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            border: none !important;
        }
        
        .dataframe thead tr th {
            background-color: #0d6efd !important;
            color: white !important;
            text-align: center !important;
            font-weight: 500 !important;
            padding: 10px !important;
        }
        
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .dataframe tbody tr:hover {
            background-color: #e9ecef;
        }
        
        /* Add custom styles for the sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }
        
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding-top: 2rem;
        }
        
        /* Custom progress bar */
        .stProgress > div > div > div > div {
            background-color: #0d6efd;
        }
        
        /* Tooltip styles */
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted #ccc;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Alert box */
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            border-left: 4px solid;
        }
        
        .alert-info {
            background-color: #cff4fc;
            border-left-color: #0dcaf0;
            color: #055160;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border-left-color: #ffc107;
            color: #664d03;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #842029;
        }
        
        .alert-success {
            background-color: #d1e7dd;
            border-left-color: #20c997;
            color: #0f5132;
        }

        /* System status badge */
        .badge {
            display: inline-block;
            padding: 0.35em 0.65em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
        }
        
        .badge-primary {
            background-color: #0d6efd;
        }
        
        .badge-success {
            background-color: #20c997;
        }
        
        .badge-warning {
            background-color: #ffc107;
            color: #000;
        }
        
        .badge-danger {
            background-color: #dc3545;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Dashboard Header Component
def render_dashboard_header():
    st.markdown('<h1 class="dashboard-title">ENIGSEC</h1>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Real-time Intrusion Detection and Prevention System (IDS/IPS)</p>', unsafe_allow_html=True)

# Sidebar with controls and info
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 24px; font-weight: 600; color: #0d6efd;">🛡️ IDS/IPS</span>
            <p style="font-size: 14px; color: #6c757d; margin-top: 5px;">Network Security Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        selected = option_menu(
            "Navigation",
            ["Dashboard", "Settings", "Documentation"],
            icons=["speedometer2", "gear", "book"],
            menu_icon="list", 
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#f8f9fa", "border-radius": "8px"},
                "icon": {"color": "#0d6efd", "font-size": "16px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
                "nav-link-selected": {"background-color": "#0d6efd", "color": "white"},
            }
        )
        
        if selected == "Dashboard":
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">System Status</div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span class="status-indicator status-active"></span>
                    <span>IDS Engine: <span class="badge badge-success">Active</span></span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span class="status-indicator status-active"></span>
                    <span>Database Connection: <span class="badge badge-success">Connected</span></span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span class="status-indicator status-active"></span>
                    <span>ML Model: <span class="badge badge-success">Loaded</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Information panel
            st.markdown("""
            <div class="alert alert-info" style="margin-top: 20px;">
                <strong>Info:</strong> Monitoring for network intrusions. 
                The model analyzes traffic patterns to detect anomalies.
            </div>
            """, unsafe_allow_html=True)
            
            # Footer
            st.markdown("""
            <div style="position: absolute; bottom: 20px; left: 20px; right: 20px; text-align: center; font-size: 12px; color: #6c757d;">
                © 2025 Network Security Monitor v1.0.0
            </div>
            """, unsafe_allow_html=True)
        
        elif selected == "Settings":
                        
            st.markdown("### Threat Response")
            auto_block = st.checkbox("Auto-block Malicious IPs", value=True)
        
        elif selected == "Documentation":
            st.markdown("## Documentation")
            st.markdown("""
            ### About IDS/IPS
            This Intrusion Detection and Prevention System uses machine learning to identify potential network threats in real-time.
            
            ### Features
            - Real-time traffic monitoring
            - Machine learning-based anomaly detection
            - Detailed traffic analysis and visualization
            - Alert system for potential intrusions
            
            ### How It Works
            The system uses a Random Forest model trained on network traffic data to classify traffic as normal or anomalous based on various features.
            """)

# Status cards
def render_status_cards(normal_count, anomaly_count):
    # Calculate rate and percentage
    total = normal_count + anomaly_count
    anomaly_rate = (anomaly_count / total) * 100 if total > 0 else 0
    
    # Create grid for stat cards
    stat_grid = grid(4, vertical_align="center")
    
    # Normal traffic card
    with stat_grid.container():
        st.markdown("""
        <div class="stat-card stat-normal">
            <div class="stat-label">Normal Traffic</div>
            <div class="stat-value">{}</div>
            <div style="font-size: 0.8rem; color: #6c757d;">Packets</div>
        </div>
        """.format(normal_count), unsafe_allow_html=True)
    
    # Anomaly card
    with stat_grid.container():
        st.markdown("""
        <div class="stat-card stat-anomaly">
            <div class="stat-label">Anomalies Detected</div>
            <div class="stat-value">{}</div>
            <div style="font-size: 0.8rem; color: #6c757d;">Packets</div>
        </div>
        """.format(anomaly_count), unsafe_allow_html=True)
    
    # Total traffic card
    with stat_grid.container():
        st.markdown("""
        <div class="stat-card stat-total">
            <div class="stat-label">Total Traffic</div>
            <div class="stat-value">{}</div>
            <div style="font-size: 0.8rem; color: #6c757d;">Packets</div>
        </div>
        """.format(total), unsafe_allow_html=True)
    
    # Anomaly rate card
    with stat_grid.container():
        st.markdown("""
        <div class="stat-card stat-rate">
            <div class="stat-label">Anomaly Rate</div>
            <div class="stat-value">{:.1f}%</div>
            <div style="font-size: 0.8rem; color: #6c757d;">of total traffic</div>
        </div>
        """.format(anomaly_rate), unsafe_allow_html=True)

# Helper function to create alert box
def create_alert(message, alert_type):
    alert_class = f"alert alert-{alert_type}"
    return f'<div class="{alert_class}">{message}</div>'

# Alert component
def render_alert(anomaly_count):
    if anomaly_count == 0:
        alert = create_alert(
            "<strong>System Normal:</strong> No anomalies detected in the network traffic.",
            "success"
        )
    elif anomaly_count < 3:
        alert = create_alert(
            f"<strong>Warning:</strong> {anomaly_count} potential anomalies detected. Monitoring system.",
            "warning"
        )
    else:
        alert = create_alert(
            f"<strong>Alert:</strong> {anomaly_count} anomalies detected! Possible intrusion attempt.",
            "danger"
        )
    
    st.markdown(alert, unsafe_allow_html=True)

# Recent activity timeline
def render_activity_timeline(recent_events):
    st.markdown('<div class="card-header">Recent Activity</div>', unsafe_allow_html=True)
    
    for event in recent_events:
        timestamp, event_type, details = event
        
        if event_type == "Normal":
            icon = "✅"
            event_class = "normal"
        else:
            icon = "⚠️"
            event_class = "anomaly"
        
        st.markdown(f"""
        <div style="display: flex; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #e9ecef;">
            <div style="margin-right: 15px; font-size: 1.2rem;">{icon}</div>
            <div style="flex-grow: 1;">
                <div style="display: flex; justify-content: space-between;">
                    <span class="{event_class}">{event_type} Traffic</span>
                    <span style="font-size: 0.8rem; color: #6c757d;">{timestamp}</span>
                </div>
                <div style="font-size: 0.9rem; margin-top: 5px; color: #212529;">{details}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
# Appuyer sur "Dashboard" ou "Settings" tout en maintenant le contenu de l'accueil
def render_main_page():
    st.markdown('<h1 class="main-title">Welcome to Network Security Monitor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-description">Your real-time network intrusion detection system is now active. Stay secure!</p>', unsafe_allow_html=True)

# Sidebar with controls and info
def render_sidebar():
    with st.sidebar:
        st.markdown("""<div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 24px; font-weight: 600; color: #0d6efd;">🛡️ IDS/IPS</span>
            <p style="font-size: 14px; color: #6c757d; margin-top: 5px;">Network Security Dashboard</p>
        </div>""", unsafe_allow_html=True)

        # Sidebar navigation
        selected = option_menu(
            "Navigation",
            ["Dashboard", "Settings", "Documentation"],
            icons=["speedometer2", "gear", "book"],
            menu_icon="list", 
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#f8f9fa", "border-radius": "8px"},
                "icon": {"color": "#0d6efd", "font-size": "16px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
                "nav-link-selected": {"background-color": "#0d6efd", "color": "white"},
            }
        )
        
        # Rendu dynamique du contenu
        if selected == "Dashboard":
            render_main_page()
            # Dashboard content
            render_dashboard_header()
            # Add specific dashboard content here, like system status, etc.
            st.markdown("### Live System Monitoring", unsafe_allow_html=True)
        
        elif selected == "Settings":
            render_main_page()
            # Settings content
            st.markdown("### System Configuration", unsafe_allow_html=True)
            auto_block = st.checkbox("Auto-block Malicious IPs", value=True)
        
        elif selected == "Documentation":
            st.markdown("## Documentation")
            st.markdown(""" ### About IDS/IPS This Intrusion Detection and Prevention System uses machine learning to identify potential network threats in real-time. """)
# Enhanced visualizations
def render_visualizations(time_series, prediction_stats):
    # Create tabs for different visualizations
    viz_tabs = st.tabs(["Distribution", "Time Series", "Features"])
    
    with viz_tabs[0]:
        # Enhanced pie chart
        labels = list(prediction_stats.keys())
        values = list(prediction_stats.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values,
            hole=.4,
            marker=dict(colors=['#20c997', '#dc3545']),
            textinfo='label+percent',
            pull=[0, 0.1],  # Pull the anomaly slice out slightly
            hoverinfo='label+value',
            textfont=dict(size=14)
        )])
        
        fig.update_layout(
            title_text="Traffic Classification Distribution",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=400,
            margin=dict(t=50, b=50, l=20, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with viz_tabs[1]:
         if time_series:
            times = list(range(len(time_series)))
            normal_cum = np.cumsum([1 if val == 0 else 0 for val in time_series])
            anomaly_cum = np.cumsum([1 if val == 1 else 0 for val in time_series])

            fig = go.Figure()
            fig.add_trace(go.Scatter(
            x=times, y=normal_cum, mode='lines', name='Normal',
            line=dict(color='#20c997', width=3),
            fill='tozeroy', fillcolor='rgba(32, 201, 151, 0.2)'
        ))
            fig.add_trace(go.Scatter(
            x=times, y=anomaly_cum, mode='lines', name='Anomalies',
            line=dict(color='#dc3545', width=3),
            fill='tozeroy', fillcolor='rgba(220, 53, 69, 0.2)'
        ))

            fig.update_layout(
            title='Cumulative Classification Over Time',
            xaxis_title='Time',
            yaxis_title='Count',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=400,
            margin=dict(t=50, b=50, l=20, r=20)
        )

        # 🔑 key unique ici
            st.plotly_chart(fig, use_container_width=True, key=f"time_series_chart_{len(time_series)}")

         else:
                st.info("Time series data will be displayed once monitoring starts.")
    
    with viz_tabs[2]:
    # Feature importance visualization
       if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        feature_importance = pd.DataFrame({
            'Feature': selected_features,
            'Importance': importances
        })
        feature_importance = feature_importance.sort_values(by='Importance', ascending=False)
        
        fig = px.bar(
            feature_importance, 
            x='Importance', 
            y='Feature',
            orientation='h',
            color='Importance',
            color_continuous_scale=['#0d6efd', '#20c997'],
            labels={'Importance': 'Feature Importance Score'}
        )
        
        fig.update_layout(
            title='Feature Importance in Anomaly Detection',
            yaxis={'categoryorder':'total ascending'},
            height=400,
            margin=dict(t=50, b=50, l=20, r=20)
        )

        # Utiliser une clé unique
        unique_key = f"feature_importance_chart_{uuid.uuid4()}"
        st.plotly_chart(fig, use_container_width=True, key=unique_key)
       else:
        st.info("Feature importance visualization not available for this model type")
# Data table with enhanced styling
def render_data_table(results_df):
    st.markdown('<div class="card-header">Recent Traffic Data</div>', unsafe_allow_html=True)
    
    # If DataFrame is empty, show placeholder
    if results_df.empty:
        st.info("Traffic data will appear here once monitoring begins")
        return
    
    # Add styling to the DataFrame
    def highlight_prediction(val):
        if 'Normal' in str(val):
            return 'background-color: rgba(32, 201, 151, 0.1); color: #198754;'
        elif 'Anomaly' in str(val):
            return 'background-color: rgba(220, 53, 69, 0.1); color: #dc3545;'
        return ''
    
    # Format the values for better display
    display_df = results_df.copy()
    
    # Format large numbers for better readability
    for col in ['src_bytes', 'dst_bytes']:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,}")
    
    # Limit the number of rows to display
    display_df = display_df.tail(10).reset_index(drop=True)
    
    # Style the dataframe
    styled_df = display_df.style.applymap(highlight_prediction, subset=['Prediction'])
    
    # Display the styled dataframe
    st.dataframe(styled_df, use_container_width=True)

# Variables globales
anomalies_detected = 0
anomalies_lock = threading.Lock()
results_df = pd.DataFrame(columns=["duration", "src_bytes", "dst_bytes", "wrong_fragment", "num_failed_logins", 
                                 "logged_in", "count", "srv_count", "dst_host_srv_serror_rate", "neptune", "Prediction"])
time_series = []
prediction_stats = {'Normal': 0, 'Anomaly': 0}
monitoring_active = False
recent_events = []

# Fonction pour surveiller et prédire les nouvelles données de trafic
def watch_for_new_traffic():
    global results_df, time_series, prediction_stats, anomalies_detected, monitoring_active, recent_events
    
    monitoring_active = True
    st.session_state.monitoring = True
    
    # Initialize session state for progress
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    
    # Main dashboard layout
    render_dashboard_header()
    
    # Progress indicator
    progress_bar = st.progress(st.session_state.progress)
    
    # Status container
    status_container = st.empty()
    
    # Alert container
    alert_container = st.empty()
    
    # Stats cards container
    stats_container = st.empty()
    
    # Create 2-column layout for data and timeline
    col1, col2 = st.columns([7, 3])
    
    # Data table container
    with col1:
        data_container = st.empty()
    
    # Timeline container
    with col2:
        timeline_container = st.empty()
    
    # Visualization container
    viz_container = st.empty()
    
    # Boucle de surveillance
    while monitoring_active and anomalies_detected < 8:
        try:
            # Update progress
            st.session_state.progress = (st.session_state.progress + 0.01) % 1
            progress_bar.progress(st.session_state.progress)
            
            # Display current status
            with status_container:
                if monitoring_active:
                    st.markdown("""
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <span class="status-indicator status-active"></span>
                        <span style="font-weight: 500; color: #0d6efd;">Monitoring Active</span>
                        <span style="margin-left: auto; font-size: 0.9rem; color: #6c757d;">
                            Last updated: {time}
                        </span>
                    </div>
                    """.format(time=datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)
            
            # Récupérer les dernières données de trafic
            cursor.execute("""
            SELECT duration, src_bytes, dst_bytes, wrong_fragment, num_failed_logins,
                   logged_in, count, srv_count, dst_host_srv_serror_rate, neptune
            FROM traffic_data ORDER BY timestamp DESC LIMIT 1
            """)
            data = cursor.fetchone()

            if data:
                # Convertir les données en DataFrame pour prédiction
                input_data = pd.DataFrame([data], columns=selected_features)
                prediction = model.predict(input_data)

                # Vérifier si l'anomalie est détectée
                if prediction[0] == 1:
                    with anomalies_lock:
                        anomalies_detected += 1
                
                # Ajouter les données et la prédiction aux tableaux
                if prediction[0] == 0:
                    pred_label = "Normal traffic (class 0)"
                    prediction_stats['Normal'] += 1
                    event_type = "Normal"
                    details = f"Source bytes: {data[1]}, Duration: {data[0]}"
                else:
                    pred_label = "Anomaly detected (class 1)"
                    prediction_stats['Anomaly'] += 1
                    event_type = "Anomaly"
                    details = f"Suspicious traffic! Bytes: {data[1]}, Wrong fragment: {data[3]}"

                # Add to recent events
                recent_events.append((datetime.now().strftime('%H:%M:%S'), event_type, details))
                if len(recent_events) > 5:
                    recent_events = recent_events[-5:]

                # Ajouter les données et prédiction au tableau
                input_data['Prediction'] = pred_label
                results_df = pd.concat([results_df, input_data], ignore_index=True)

                # Ajouter des données au time series pour le graphique en temps réel
                time_series.append(prediction[0])  # Suivi des prédictions (normal ou anomalie)
                
                # Update UI components
                with alert_container:
                    render_alert(anomalies_detected)
                
                with stats_container:
                    render_status_cards(prediction_stats['Normal'], prediction_stats['Anomaly'])
                
                with data_container:
                    render_data_table(results_df)
                
                with timeline_container:
                    render_activity_timeline(recent_events)
                
                with viz_container:
                    render_visualizations(time_series, prediction_stats)

            # Pause avant de vérifier les nouvelles données
            time.sleep(5)

        except Exception as e:
            st.error(f"Error: {e}")
            time.sleep(5)
            pass

# Main application
def main():
    # Render sidebar
    render_sidebar()
    
    # Initialize the dashboard if monitoring isn't active
    if 'monitoring' not in st.session_state or not st.session_state.monitoring:
        render_dashboard_header()
        
        # Welcome message
        st.markdown("""
        <div class="card">
            <div class="card-header">Welcome to Network Security Monitor</div>
            <p style="margin-bottom: 15px;">
                This dashboard provides real-time monitoring of network traffic to detect potential intrusions.
                The system uses machine learning to classify traffic as normal or anomalous.
            </p>
            <p>
                Click "Start Monitoring" in the sidebar to begin surveillance.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample visualizations
        st.markdown('<div class="card-header" style="margin-top: 20px;">System Overview</div>', unsafe_allow_html=True)
        
        # Create sample data for initial display
        if not time_series:
            sample_data = {
                'Normal': 20,
                'Anomaly': 5
            }
            
            # Sample visualization
            fig = go.Figure(data=[go.Pie(
                labels=list(sample_data.keys()), 
                values=list(sample_data.values()),
                hole=.4,
                marker=dict(colors=['#20c997', '#dc3545']),
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                title_text="Sample Distribution (Demo Data)",
                height=400,
                margin=dict(t=50, b=50, l=20, r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True, key="sample_distribution_chart")
            
            # Feature information
            st.markdown("""
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">Key Features Monitored</div>
                <ul style="padding-left: 20px;">
                    <li><strong>duration</strong>: Length of the connection</li>
                    <li><strong>src_bytes</strong>: Bytes sent from source to destination</li>
                    <li><strong>dst_bytes</strong>: Bytes sent from destination to source</li>
                    <li><strong>wrong_fragment</strong>: Number of wrong fragments</li>
                    <li><strong>logged_in</strong>: 1 if successfully logged in; 0 otherwise</li>
                    <li><strong>num_failed_logins</strong>: Number of failed login attempts</li>
                    <li><strong>count</strong>: Number of connections to the same host</li>
                    <li><strong>srv_count</strong>: Number of connections to the same service</li>
                    <li><strong>dst_host_srv_serror_rate</strong>: % of connections that have SYN errors</li>
                    <li><strong>neptune</strong>: Neptune attack flag</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Check if the start button is clicked in the sidebar
    if st.session_state.get('__sidebar_start_button', False):
        watch_for_new_traffic()
    
    # Handle sidebar start button click
    if st.sidebar.button('Start Monitoring', key='__sidebar_start_button'):
        watch_for_new_traffic()

# Run the application
if __name__ == "__main__":
    main()