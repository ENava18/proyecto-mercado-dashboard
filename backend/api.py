import subprocess
import os
import sys
import datetime
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Adjust path to import from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daily_monitor import PORTAFOLIO, LIMITE_TARGET, LIMITE_STOP_LOSS, obtener_precios_actuales, EFECTIVO, save_portfolio

app = FastAPI(title="Swing Trading API")

class UpdateSharesRequest(BaseModel):
    ticker: str
    cantidad: int

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/portfolio")
def get_portfolio():
    precios_vivos = obtener_precios_actuales()
    data_rows = []
    
    total_inversion_acciones = 0
    total_actual_acciones = 0
    
    for ticker, info in PORTAFOLIO.items():
        p_entrada = info["Entrada_Estimada"]
        cantidad = info["Cantidad"]
        p_actual = precios_vivos.get(ticker, p_entrada)
        var_pct = (p_actual - p_entrada) / p_entrada
        
        status_text = "En seguimiento"
        if var_pct >= LIMITE_TARGET:
            status_text = "TARGET"
        elif var_pct <= LIMITE_STOP_LOSS:
            status_text = "STOP"
            
        valor_entrada = cantidad * p_entrada
        valor_actual = cantidad * p_actual
        
        total_inversion_acciones += valor_entrada
        total_actual_acciones += valor_actual
            
        data_rows.append({
            "ticker": ticker,
            "nombre": info["Nombre"],
            "precio_entrada": p_entrada,
            "precio_actual": round(p_actual, 2),
            "cantidad": cantidad,
            "target": info["Target_Ganancia"],
            "variacion_pct": round(var_pct * 100, 2),
            "estado": status_text
        })
        
    inversion_total_portafolio = total_inversion_acciones + EFECTIVO
    balance_total = total_actual_acciones + EFECTIVO
    
    roi_total = ((balance_total - inversion_total_portafolio) / inversion_total_portafolio) * 100 if inversion_total_portafolio > 0 else 0
    ganancia_absoluta = balance_total - inversion_total_portafolio

    return {
        "portfolio": data_rows,
        "summary": {
            "balance_total": round(balance_total, 2),
            "inversion_inicial": round(inversion_total_portafolio, 2),
            "ganancia_absoluta": round(ganancia_absoluta, 2),
            "roi_total_pct": round(roi_total, 2)
        }
    }

@app.get("/api/news")
def get_news():
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_report = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', f'reporte_diario_{today_str}.md'))
    
    # Fallback if no report for today
    if not os.path.exists(daily_report):
        # find the most recently modified reporte_diario_*.md
        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        reports = [f for f in os.listdir(directory) if f.startswith('reporte_diario_') and f.endswith('.md')]
        if reports:
            reports.sort(reverse=True) # Sort lexicographically (by date descending)
            daily_report = os.path.join(directory, reports[0])
        else:
            daily_report = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'reporte_final.md'))
            
    if not os.path.exists(daily_report):
        raise HTTPException(status_code=404, detail="No report found")
        
    try:
        with open(daily_report, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendation")
def get_recommendation():
    """
    Reads the analisis_tecnico_resultados.md to find the top recommended stock 
    that is NOT currently in the portfolio.
    """
    try:
        analysis_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analisis_tecnico_resultados.md'))
        if not os.path.exists(analysis_file):
            return {"recommendation": "No se encontró el análisis técnico reciente."}
            
        with open(analysis_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Parse the markdown table
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
                if len(parts) > 1:
                    ticker = parts[1].strip()
                    candidates.append(ticker)
            elif in_table and not line.strip():
                # End of table
                in_table = False
                
        # Find the first candidate not in portfolio
        for candidate in candidates:
            if candidate not in PORTAFOLIO:
                return {"recommendation": candidate}
                
        return {"recommendation": "No hay nuevas opciones que superen el filtro actual."}
        
    except Exception as e:
        return {"recommendation": f"Error al generar recomendación: {str(e)}"}

@app.post("/api/portfolio/update")
def update_portfolio_shares(request: UpdateSharesRequest):
    if request.ticker not in PORTAFOLIO:
        raise HTTPException(status_code=404, detail="Ticker not found in portfolio")
    
    # Update the dictionary in memory
    PORTAFOLIO[request.ticker]["Cantidad"] = request.cantidad
    
    # Save the updated dictionary to the JSON file
    try:
        save_portfolio(PORTAFOLIO)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")
        
    return {"message": f"Successfully updated {request.ticker} to {request.cantidad} shares"}

async def run_analysis_task():
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        process = await asyncio.create_subprocess_exec(
            "python", "technical_analysis.py",
            cwd=root_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            report_file = os.path.join(root_dir, "reporte_final.md")
            with open(report_file, "a", encoding="utf-8") as f:
                f.write(f"\n*Última actualización de análisis (API): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            print("Análisis técnico completado.")
        else:
            print(f"Error en el análisis técnico: {stderr.decode()}")
    except Exception as e:
        print(f"Failed to run task: {e}")

@app.post("/api/analyze")
async def trigger_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_analysis_task)
    return {"message": "Análisis lanzado en el fondo. Se actualizará el reporte en unos momentos."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
