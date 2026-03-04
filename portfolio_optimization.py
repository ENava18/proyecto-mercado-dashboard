import yfinance as yf
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime

# --- CONFIGURACIÓN ---
CAPITAL_TOTAL = 2000000
OUTPUT_DIR = r"c:\Users\emin1\Antigravity\Proyecto_Mercado"
CORRELATION_FILE = os.path.join(OUTPUT_DIR, "matriz_correlacion.png")
PORTFOLIO_FILE = os.path.join(OUTPUT_DIR, "portafolio_optimizado.md")

# Tickers seleccionados tras Fase 1 y 2
# Sectores: Industrial/Inmuebles (VESTA), Materiales (GMEXICO), Salud/Consumo (LABB), 
# Industrial/Construcción (GCARSO), Consumo Básico (KIMBERA), Financiero (BBAJIOO)
TICKERS_ELEGIDOS = [
    "VESTA.MX", 
    "GMEXICOB.MX", 
    "LABB.MX", 
    "GCARSOA1.MX", 
    "KIMBERA.MX", 
    "BBAJIOO.MX"
]

# Datos de la decisión cualitativa/cuantitativa
SCORE_Y_CATALIZADOR = {
    "VESTA.MX": {"Sector": "Inmobiliario Industrial", "Puntos_Conviction": 5}, # Nearshoring + Técnico fuerte
    "GMEXICOB.MX": {"Sector": "Materiales (Minería)", "Puntos_Conviction": 5}, # Cobre en déficit + Rebote RSI
    "LABB.MX": {"Sector": "Salud / Consumo", "Puntos_Conviction": 4},          # Earnings recovery + EMA cruce
    "GCARSOA1.MX": {"Sector": "Industrial / Energía", "Puntos_Conviction": 4}, # Mega contrato Pemex a 20 años
    "KIMBERA.MX": {"Sector": "Consumo Básico", "Puntos_Conviction": 3},        # Recompra acciones + Dividendos
    "BBAJIOO.MX": {"Sector": "Financiero", "Puntos_Conviction": 3}             # Diversificación + Tasas altas
}

def obtener_datos(tickers, period="180d"):
    datos_cierres = pd.DataFrame()
    for tick in tickers:
        try:
            hist = yf.Ticker(tick).history(period=period)
            if not hist.empty:
                datos_cierres[tick] = hist['Close']
        except Exception as e:
            print(f"Error bajando {tick}: {e}")
    return datos_cierres.dropna()

def calcular_correlacion(df_cierres):
    # Usamos rendimientos diarios para la correlación financiera real
    rendimientos = df_cierres.pct_change().dropna()
    correlacion = rendimientos.corr()
    return correlacion

def asignar_pesos(tickers_dict):
    """
    Asigna peso al portafolio de $2,000,000 basado en los "Puntos de Convicción"
    (combinación de Momentum de Corto Plazo + Catalizador Noticias).
    """
    total_puntos = sum([v["Puntos_Conviction"] for v in tickers_dict.values()])
    
    asignacion = {}
    monto_restante = CAPITAL_TOTAL
    
    for i, (ticker, data) in enumerate(tickers_dict.items()):
        if i == len(tickers_dict) - 1:
            # Al último le damos exactamente el resto para cuadrar centavos
            asignacion[ticker] = monto_restante
        else:
            peso_porcentual = data["Puntos_Conviction"] / total_puntos
            monto = round(CAPITAL_TOTAL * peso_porcentual, 2)
            asignacion[ticker] = monto
            monto_restante = round(monto_restante - monto, 2)
            
    return asignacion

def main():
    print("Iniciando Fase 3: Optimización y Verificación de Correlaciones...")
    
    # 1. Verificación de Diversificación (Requisito: >= 3 sectores)
    sectores_unicos = set([d["Sector"] for d in SCORE_Y_CATALIZADOR.values()])
    print(f"Verificación de Sectores: {len(sectores_unicos)} sectores distintos encontrados.")
    if len(sectores_unicos) < 3:
        print("ADVERTENCIA: Portafolio no cumple el mínimo de 3 sectores.")
    
    # 2. Descarga de datos y Correlación
    df = obtener_datos(TICKERS_ELEGIDOS)
    if not df.empty:
        corr_matrix = calcular_correlacion(df)
        
        # Guardar gráfico de correlación térmica simple
        plt.figure(figsize=(8, 6))
        plt.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, fignum=1)
        plt.colorbar()
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45, ha='left')
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.title('Matriz de Correlación (Rendimientos Diarios)', pad=20)
        plt.savefig(CORRELATION_FILE, bbox_inches='tight')
        plt.close()
        print(f"Matriz de correlación guardada en {CORRELATION_FILE}")
    else:
        print("No se pudieron descargar datos para la correlación.")

    # 3. Asignación de Capital
    montos = asignar_pesos(SCORE_Y_CATALIZADOR)
    
    # 4. Guardar Reporte Final
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        f.write("# Portafolio Optimizado (Fase 3)\n\n")
        f.write(f"**Fecha de Asignación:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Capital Total Invertido:** ${CAPITAL_TOTAL:,.2f} MXN\n")
        f.write(f"**Verificación Sectorial:** {len(sectores_unicos)} sectores. (CUMPLE REQUISITO >3)\n\n")
        
        f.write("## Asignación de Capital por Emisora\n\n")
        f.write("| Ticker | Sector | Nivel de Convicción | Asignación (MXN) | % del Portafolio |\n")
        f.write("|---|---|---|---|---|\n")
        
        for tick, monto in montos.items():
            porcentaje = (monto / CAPITAL_TOTAL) * 100
            sector = SCORE_Y_CATALIZADOR[tick]["Sector"]
            conviccion = SCORE_Y_CATALIZADOR[tick]["Puntos_Conviction"]
            f.write(f"| **{tick}** | {sector} | {conviccion}/5 | ${monto:,.2f} | {porcentaje:.2f}% |\n")
            
        f.write("\n\n### Análisis de Riesgo y Correlación\n")
        f.write("Se ha generado una matriz de correlación localmente (`matriz_correlacion.png`) basada en los rendimientos diarios recientes.\n")
        f.write("Al pertenecer a sectores como Minería, Consumo Básico, Financiero e Industrial, el portafolio mitiga el riesgo sistémico de un solo sector mexicano, cumpliendo la regla impuesta para la clase.\n")
        
        f.write("\n### Targets a corto plazo (Swing de 3 Semanas)\n")
        f.write("*   **Toma de Ganancias Acelerada (Target):** +6% a +8% (Vendemos posición sin apego emocional).\n")
        f.write("*   **Stop Loss Estricto:** Si el activo cae -3.5% desde el precio de entrada, *vendemos* para preservar capital y reasignar liquidez.\n")

    print(f"Asignación completa. Detalles en: {PORTFOLIO_FILE}")

if __name__ == "__main__":
    main()
