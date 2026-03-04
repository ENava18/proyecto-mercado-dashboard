import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import subprocess
import os
import plotly.graph_objects as plotly_go
from streamlit_autorefresh import st_autorefresh
from daily_monitor import PORTAFOLIO, LIMITE_STOP_LOSS, LIMITE_TARGET, obtener_precios_actuales

st.set_page_config(page_title="Dashboard Portafolio BMV", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for Dark Mode and Green Accents (Bloomberg/Yahoo Finance Terminal style)
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    h1, h2, h3 {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton > button {
        background-color: #00FF41;
        color: #0d1117;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #00cc33;
        color: #ffffff;
    }
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        color: #00FF41;
    }
    .markdown-container {
        background-color: #161b22;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #30363d;
        height: 600px;
        overflow-y: auto;
    }
    /* Banner Error */
    div[data-testid="stAlert"] {
        background-color: rgba(255, 0, 0, 0.2);
        color: #ff4d4d;
        border-left: 5px solid #ff4d4d;
    }
</style>
""", unsafe_allow_html=True)

# Autorefresh every 5 minutes (300,000 ms)
st_autorefresh(interval=300000, limit=None, key="auto_refresh_prices")

st.title("📈 Swing Trading Dashboard - Portafolio BMV")

# Check for manual update
if st.button("🔄 Actualizar Análisis de Mercado (Análisis Completo de 38 Tickers)"):
    with st.spinner("Ejecutando análisis técnico profundo y buscando noticias..."):
        try:
            subprocess.run(["python", "technical_analysis.py"], check=True)
            with open("reporte_final.md", "a", encoding="utf-8") as f:
                f.write(f"\n*Última actualización de análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            st.success("Análisis técnico finalizado y reporte actualizado.")
            st.balloons()
        except Exception as e:
            st.error(f"Error al ejecutar technical_analysis.py: {e}")

st.divider()

# Fetch latest prices for dashboard
precios_vivos = obtener_precios_actuales()

# Alerts evaluation
alertas_stop_loss = []
for ticker, info in PORTAFOLIO.items():
    p_entrada = info["Entrada_Estimada"]
    p_actual = precios_vivos.get(ticker, p_entrada)
    var_pct = (p_actual - p_entrada) / p_entrada
    if var_pct <= LIMITE_STOP_LOSS:
        alertas_stop_loss.append(f"{ticker} (Caída: {var_pct*100:.2f}%)")

if alertas_stop_loss:
    st.error(f"🚨 **ALERTA DE STOP LOSS ALCANZADO:** {', '.join(alertas_stop_loss)}. ¡EVALUAR VENTA INMEDIATA!")

# Prepare Data
data_rows = []

for ticker, info in PORTAFOLIO.items():
    p_entrada = info["Entrada_Estimada"]
    p_actual = precios_vivos.get(ticker, p_entrada)
    var_pct = (p_actual - p_entrada) / p_entrada
    
    status_text = "🟢 En seguimiento"
    if var_pct >= LIMITE_TARGET:
        status_text = "🎯 TARGET"
    elif var_pct <= LIMITE_STOP_LOSS:
        status_text = "🛑 STOP"
        
    data_rows.append({
        "Ticker": ticker,
        "Nombre": info["Nombre"],
        "Costo Entrada": f"${p_entrada:.2f}",
        "Precio Actual": f"${p_actual:.2f}",
        "Target": f"${info['Target_Ganancia']:.2f}",
        "Variación": var_pct,
        "Estado": status_text
    })

df_portfolio = pd.DataFrame(data_rows)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Resumen del Portafolio en Vivo")
    
    # Format Variation for display
    df_display = df_portfolio.copy()
    df_display['Variación'] = (df_display['Variación'] * 100).apply(lambda x: f"{x:+.2f}%")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Visualización de Variación (ROI) con Plotly
    fig = plotly_go.Figure()
    
    colors = ['#ff4d4d' if val < 0 else '#00FF41' for val in df_portfolio['Variación']]
    
    fig.add_trace(plotly_go.Bar(
        x=df_portfolio['Ticker'],
        y=df_portfolio['Variación'] * 100,
        text=(df_portfolio['Variación'] * 100).apply(lambda x: f"{x:+.2f}%"),
        textposition='auto',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Rendimiento Proyectado por Acción (ROI %)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#C9D1D9'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#30363d', ticksuffix="%"),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📰 Titulares Guardados (Catalizadores)")
    
    try:
        with open("noticias_catalizadores.md", "r", encoding="utf-8") as f:
            noticias_md = f.read()
            st.markdown(f"<div class='markdown-container'>{noticias_md}</div>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("El archivo `noticias_catalizadores.md` no se encuentra.")
