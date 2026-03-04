import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import os
import datetime

# --- CONFIGURACIÓN ---
BMV_TICKERS = [
    "AC.MX", "ALFAA.MX", "ALSEA.MX", "AMXB.MX", "ASURB.MX", "BBAJIOO.MX", 
    "BIMBOA.MX", "BOLSAA.MX", "CEMEXCPO.MX", "CHDRAUIB.MX", "CUERVO.MX", 
    "ELEKTRA.MX", "FEMSAUBD.MX", "GAPB.MX", "GCARSOA1.MX", "GCC.MX", 
    "GENTERA.MX", "GFINBURO.MX", "GFNORTEO.MX", "GMEXICOB.MX", "GRUMAB.MX", 
    "KIMBERA.MX", "KOFUBL.MX", "LABB.MX", "LACOMERUBC.MX", "LIVEPOLC1.MX", 
    "MEGACPO.MX", "NAFTRACISHRS.MX", "OMAB.MX", "ORBIA.MX", "PE&OLES.MX", 
    "PINFRA.MX", "Q.MX", "RA.MX", "SIGMAA.MX", "TLEVISACPO.MX", "VESTA.MX", 
    "WALMEX.MX"
]

CAPITAL_TOTAL = 2000000
MIN_ACCIONES = 6
POSICION_PROMEDIO = CAPITAL_TOTAL / MIN_ACCIONES # ~ $333,333 MXN
VOLUMEN_MINIMO_MXN_DIARIO = POSICION_PROMEDIO * 5 
DIAS_HISTORIAL = "120d" 

OUTPUT_DIR = r"c:\Users\emin1\Antigravity\Proyecto_Mercado"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "analisis_tecnico_resultados.md")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_datos(tickers, period):
    print(f"Descargando datos históricos para {len(tickers)} tickers...")
    try:
        # data = yf.download(tickers, period=period, group_by='ticker', threads=True, auto_adjust=True)
        # Para evitar problemas con el MultiIndex en versiones nuevas, podemos iterar o descargar directo
        # La forma más segura es usar Ticker history individual para no lidiar con un df complicado
        datos_por_ticker = {}
        for tick in tickers:
            ticker_obj = yf.Ticker(tick)
            hist = ticker_obj.history(period=period)
            if not hist.empty:
                datos_por_ticker[tick] = hist
        return datos_por_ticker
    except Exception as e:
        print(f"Error general descargando datos: {e}")
        return {}

def analizar_ticker(ticker, df):
    try:
        if df is None or df.empty or len(df) < 50:
            return None
            
        df = df.dropna(subset=['Close', 'Volume']).copy()
        df['Volumen_MXN'] = df['Volume'] * df['Close']
        avg_vol_mxn = df['Volumen_MXN'].tail(10).mean()
        pass_liquidity = avg_vol_mxn > VOLUMEN_MINIMO_MXN_DIARIO
        
        # EMA rápidas
        df.ta.ema(length=9, append=True)
        df.ta.ema(length=12, append=True)
        # RSI
        df.ta.rsi(length=14, append=True)
        # MACD (12, 26, 9)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        
        df = df.dropna().copy()
        
        if df.empty: return None
            
        ultimo_dia = df.iloc[-1]
        ema9 = ultimo_dia['EMA_9']
        ema12 = ultimo_dia['EMA_12']
        rsi = ultimo_dia['RSI_14']
        macd_hist = ultimo_dia.get('MACDh_12_26_9', 0)
        close_price = ultimo_dia['Close']
        
        score = 0
        if ema9 > ema12: score += 2    # Tendencia alcista
        if macd_hist > 0: score += 1   # Momentum acelerando
        if 40 <= rsi <= 65: score += 1 # Espacio de crecimiento
        if rsi < 35: score += 2        # Sobrevendido brutalmente, probable rebote
        
        return {
            "Ticker": ticker,
            "Close": close_price,
            "EMA9": ema9,
            "EMA12": ema12,
            "RSI": rsi,
            "MACD_Hist": macd_hist,
            "Avg_Vol_MXN": avg_vol_mxn,
            "Pass_Liquidity": pass_liquidity,
            "Score": score,
            "DF_History": df 
        }
    except Exception as e:
        print(f"Error analizando {ticker}: {e}")
        return None

def main():
    print("Iniciando Análisis Técnico Swing Trading BMV...")
    datos_por_ticker = descargar_datos(BMV_TICKERS, DIAS_HISTORIAL)
    resultados = []
    
    for ticker, df in datos_por_ticker.items():
        res = analizar_ticker(ticker, df)
        if res:
            resultados.append(res)
            
    liquidos = [r for r in resultados if r['Pass_Liquidity']]
    print(f"\nTickers que pasaron filtro de liquidez: {len(liquidos)} de {len(resultados)}")
    
    liquidos_ordenados = sorted(liquidos, key=lambda x: (x['Score'], x['RSI'] if x['RSI'] < 40 else -x['RSI']), reverse=True)
    top_candidatos = liquidos_ordenados[:10] 
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Resultados de Análisis Técnico (Short-Term Momentum)\n\n")
        f.write(f"**Fecha de Análisis:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Filtro Liquidez:** > ${VOLUMEN_MINIMO_MXN_DIARIO:,.2f} MXN Diarios\n\n")
        f.write("## Top Candidatos Cuantitativos\n\n")
        f.write("| Ticker | Close MXN | EMA 9 | EMA 12 | Tendencia EMA | RSI (14) | MACD Hist | Score | Vol Prom (MXN) |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        
        for p in top_candidatos:
            tendencia = "Alcista" if p['EMA9'] > p['EMA12'] else "Bajista"
            f.write(f"| {p['Ticker']} | ${p['Close']:.2f} | {p['EMA9']:.2f} | {p['EMA12']:.2f} | {tendencia} | {p['RSI']:.2f} | {p['MACD_Hist']:.3f} | {p['Score']} | ${p['Avg_Vol_MXN']:,.0f} |\n")
            
            # Gráfica
            df = p['DF_History'].tail(45) 
            plt.figure(figsize=(10, 5))
            plt.plot(df.index, df['Close'], label='Cierre', color='black', alpha=0.5, linewidth=2)
            plt.plot(df.index, df['EMA_9'], label='EMA 9', color='blue', linestyle='--')
            plt.plot(df.index, df['EMA_12'], label='EMA 12', color='red', linestyle='--')
            plt.title(f"{p['Ticker']} - Cierre y EMAs (Últimos 45 días)")
            plt.xlabel('Fecha')
            plt.ylabel('Precio MXN')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            grafica_path = os.path.join(OUTPUT_DIR, f"{p['Ticker'].replace('.MX', '')}_chart.png")
            plt.savefig(grafica_path, bbox_inches='tight')
            plt.close()
            
        f.write("\n\n*Las gráficas visuales han sido guardadas en la misma carpeta.*")
    
    print(f"\nReporte guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
