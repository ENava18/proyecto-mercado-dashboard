import yfinance as yf
import pandas as pd
import datetime
import requests # Básico para buscar titulares (usando API pública de RSS o simulación)
import json
import os

# Configuración del Portafolio Elegido
PORTAFOLIO_FILE = os.path.join(os.path.dirname(__file__), 'portafolio.json')

def load_portfolio():
    if not os.path.exists(PORTAFOLIO_FILE):
        default_portfolio = {
            "VESTA.MX": {"Nombre": "Vesta", "Entrada_Estimada": 59.27, "Cantidad": 6931, "Target_Ganancia": 63.76, "Stop_Loss": 56.97},
            "GMEXICOB.MX": {"Nombre": "Grupo México", "Entrada_Estimada": 207.67, "Cantidad": 1985, "Target_Ganancia": 222.21, "Stop_Loss": 198.54},
            "LABB.MX": {"Nombre": "Genomma Lab", "Entrada_Estimada": 17.34, "Cantidad": 18948, "Target_Ganancia": 18.98, "Stop_Loss": 16.96},
            "GCARSOA1.MX": {"Nombre": "Grupo Carso", "Entrada_Estimada": 125.79, "Cantidad": 2655, "Target_Ganancia": 134.65, "Stop_Loss": 120.31},
            "KIMBERA.MX": {"Nombre": "Kimberly Clark", "Entrada_Estimada": 42.61, "Cantidad": 5879, "Target_Ganancia": 45.47, "Stop_Loss": 40.63},
            "BBAJIOO.MX": {"Nombre": "BanBajio", "Entrada_Estimada": 55.42, "Cantidad": 4492, "Target_Ganancia": 59.72, "Stop_Loss": 53.36}
        }
        with open(PORTAFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_portfolio, f, indent=4, ensure_ascii=False)
        return default_portfolio
    else:
        with open(PORTAFOLIO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_portfolio(data):
    with open(PORTAFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

PORTAFOLIO = load_portfolio()
EFECTIVO = 8134.27

# Límites de la estrategia (3.5% SL, 8% Target)
LIMITE_STOP_LOSS = -0.035
LIMITE_TARGET = 0.08
HOY = datetime.datetime.now().strftime("%Y-%m-%d")

def obtener_precios_actuales():
    print("Recuperando precios en tiempo real de la BMV...")
    precios = {}
    try:
        tickers = list(PORTAFOLIO.keys())
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
        for t in tickers:
            try:
                # yfinance return handling for single vs multiple symbols
                df_ticker = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                if not df_ticker.empty:
                    precios[t] = float(df_ticker['Close'].iloc[-1])
            except Exception as e:
                print(f"Error obteniendo {t}: {e}")
                precios[t] = PORTAFOLIO[t]["Entrada_Estimada"] # Fallback al precio original para que no truene el script
    except Exception as e_gral:
         print(f"Error de red general: {e_gral}")
         pass
    return precios

def alertar_notificaciones(ticker, cambio_pct):
    if cambio_pct <= LIMITE_STOP_LOSS:
         return f"🚀 **[ALERTA INBOX ANTIGRAVITY]** 🛑 STOP LOSS ALCANZADO para {ticker}. Caída del {cambio_pct*100:.2f}%. Evaluación de *Venta Inmediata* y Reasignación requerida."
    elif cambio_pct >= LIMITE_TARGET:
         return f"✅ **[ALERTA INBOX ANTIGRAVITY]** 🎯 TARGET DE GANANCIAS ALCANZADO para {ticker} (+{cambio_pct*100:.2f}%). Cerrar posición sugerida."
    return "En seguimiento normal."

def buscar_noticias_ticker(ticker_name):
    # Simulación simple de obtención de feeds de noticias usando Yahoo Finance feed (RSS logic u objeto ticker)
    # En producción real esto golpearía la API de búsqueda web de un LLM o NewsAPI.
    try:
        obj = yf.Ticker(ticker_name)
        noticias = obj.news
        if noticias and len(noticias) > 0:
            return noticias[0]['title']
    except Exception:
        pass
    return "No hay titulares recientes relevantes detectados hoy."

def main():
    print(f"\n--- REPORTE DIARIO DE MONITOREO BMV - SWING TRADING ({HOY}) ---\n")
    
    precios_vivos = obtener_precios_actuales()
    
    print("-" * 120)
    print(f"{'Ticker':<12} | {'Precio Act':<10} | {'Costo Ent.':<10} | {'Variación':<10} | {'Estado Alerta':<80}")
    print("-" * 120)
    
    for ticker, info in PORTAFOLIO.items():
        precio_entrada = info["Entrada_Estimada"]
        precio_actual = precios_vivos.get(ticker, precio_entrada)
        
        cambio_pct = (precio_actual - precio_entrada) / precio_entrada
        
        estado = alertar_notificaciones(ticker, cambio_pct)
        
        print(f"{ticker:<12} | ${precio_actual:<9.2f} | ${precio_entrada:<9.2f} | {cambio_pct*100:>8.2f}% | {estado}")
        
    print("-" * 120)
    print("\n[Últimos Titulares Detectados]")
    for ticker in PORTAFOLIO.keys():
        titular = buscar_noticias_ticker(ticker)
        print(f" > {ticker}: {titular}")
        
if __name__ == "__main__":
    main()
