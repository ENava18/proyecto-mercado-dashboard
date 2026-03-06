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

def obtener_recomendacion_reemplazo(cantidad_efectivo):
    # Retrieve the top candidate not in portfolio from technical analysis
    analysis_file = os.path.join(os.path.dirname(__file__), 'analisis_tecnico_resultados.md')
    if not os.path.exists(analysis_file):
        return None, 0
        
    try:
        with open(analysis_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        in_table = False
        candidates = []
        for line in lines:
            if "| Ticker" in line:
                in_table = True
                continue
            if in_table and "|---" in line:
                continue
            if in_table and line.strip().startswith("|"):
                parts = line.split("|")
                if len(parts) > 2:
                    ticker = parts[1].strip()
                    price_str = parts[2].strip().replace('$', '').replace(',', '')
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = 0.0
                    candidates.append({"ticker": ticker, "price": price})
            elif in_table and not line.strip():
                in_table = False
                
        for cand in candidates:
            price_val = float(cand["price"])
            if cand["ticker"] not in PORTAFOLIO and price_val > 0.0:
                cantidad_a_comprar = int(cantidad_efectivo // price_val)
                return cand["ticker"], cantidad_a_comprar
                
    except Exception as e:
        print("Error leyendo recomendaciones:", e)
        
    return None, 0

def main():
    precios_vivos = obtener_precios_actuales()
    
    report_file = os.path.join(os.path.dirname(__file__), f"reporte_diario_{HOY}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"### Reporte Diario - {HOY}\n\n")
        f.write("A continuación se muestra el estado actual de sus posiciones:\n\n")
        
        recomendaciones_accion = []
        
        for ticker, info in PORTAFOLIO.items():
            precio_entrada = float(info["Entrada_Estimada"])
            precio_actual = float(precios_vivos.get(ticker, precio_entrada))
            cantidad = int(info["Cantidad"])
            valor_actual = precio_actual * cantidad
            
            cambio_pct = (precio_actual - precio_entrada) / precio_entrada
            
            f.write(f"- **{ticker}**: Conservar {cantidad} acciones. (Rendimiento local: {cambio_pct*100:+.2f}%)\n")
            
            # Revisar si hay condición de venta:
            if cambio_pct <= LIMITE_STOP_LOSS or cambio_pct >= LIMITE_TARGET:
                motivo = "Stop Loss" if cambio_pct <= LIMITE_STOP_LOSS else "Take Profit (Target)"
                reemplazo, cant_reemplazo = obtener_recomendacion_reemplazo(valor_actual)
                
                sugerencia = f"  - ⚠️ **EJECUCIÓN SUGERIDA:** Vender **toda la posición** de {ticker} (por {motivo}). "
                if reemplazo:
                    sugerencia += f"Comprar directamente **{cant_reemplazo} acciones** de **{reemplazo}** con el efectivo liberado (${valor_actual:,.2f} MXN)."
                else:
                    sugerencia += "Mantener en efectivo."
                    
                recomendaciones_accion.append(sugerencia)
        
        if recomendaciones_accion:
            f.write("\n### 🚨 Movimientos Estratégicos Recomendados Hoy:\n\n")
            for rec in recomendaciones_accion:
                f.write(rec + "\n")
                
    print(f"Reporte diario simplificado generado: {report_file}")
        
if __name__ == "__main__":
    main()
