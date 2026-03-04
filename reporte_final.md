# Reporte Final: Portafolio Estratégico Swing Trading (BMV)
**Simulador Accitrade Coach - Cierre 3 Semanas**

**Gestor:** Antigravity (Senior Portfolio Manager)
**Capital Inicial:** $2,000,000 MXN.
**Objetivo:** Retorno de Inversión Absoluto Máximo en 21 días (Swing Trading).

---

## 1. Tesis de Inversión (Visión General)
Dado el estricto horizonte temporal de 3 semanas, este portafolio abandona las métricas de valuación tradicionales a largo plazo y se basa en un modelo cuantitativo de **Momentum de Corto Plazo y Catalizadores Específicos**. 

El universo de 38 emisoras se filtró mediante un **Agente de Análisis Técnico en Python** buscando volumen superior a $1.6M MXN diarios, cruces positivos en EMA de 9 y 12 periodos (para reacción rápida) y zonas de sobreventa RSI con potencial de expansión de MACD. Paralelamente, un **Agente de Investigación** escaneó el mercado en busca de "drivers" direccionales como *Nearshoring*, recuperación de flujo o contratos amarrados y confirmados.

Finalmente, para cumplir las reglas del torneo y proteger el capital ante riesgos sistémicos, el portafolio cuenta con exactamente **6 Acciones (Diversificadas en 6 sectores de la BMV)** y una asignación ponderada por nuestra convicción de la tesis.

## 2. Asignación del Portafolio y Composición
(La sumatoria es exactamente de $2,000,000.00 MXN)

| Ticker | Sector | Convicción | Inversión (MXN) | Peso |
| :--- | :--- | :--- | :--- | :--- |
| **GMEXICOB.MX** | Materiales | Alta (5) | $416,666.67 | 20.83% |
| **VESTA.MX** | Inmobiliario Indust. | Alta (5) | $416,666.67 | 20.83% |
| **LABB.MX** | Salud / Consumo | Media-Alta (4) | $333,333.33 | 16.67% |
| **GCARSOA1.MX** | Industrial / Energía | Media-Alta (4) | $333,333.33 | 16.67% |
| **KIMBERA.MX** | Consumo Básico | Media (3) | $250,000.00 | 12.50% |
| **BBAJIOO.MX** | Financiero | Media (3) | $250,000.00 | 12.50% |


## 3. Justificación Específica por Emisora

### 1. **Vesta** (`VESTA.MX` - $416,666.67)
*   **Fundamental:** El apalancamiento puro en *Nearshoring*. La ocupación está al límite y acaban de reportar un cierre 2025 superando guía con ocupaciones agresivas. El mercado comenzará a tarifar los nuevos ingresos arrendatarios en las siguientes semanas previas al reporte del Q1.
*   **Técnico:** De las pocas acciones del sector inmobiliario con un cruce técnico alcista fuerte: EMA 9 sobrepasando EMA 12 impulsado por MACD positivo. 

### 2. **Grupo México** (`GMEXICOB.MX` - $416,666.67)
*   **Fundamental:** Tuvo caídas agresivas la primera semana de marzo por temores de recesión externa, sin embargo, el déficit de Cobre previsto para este año empujará necesariamente los precios hacia arriba. Además, reportaron EBITDA histórico. Acaban de pagar dividendos, por lo que el precio ya descontó dicho evento. 
*   **Técnico:** La caída de estos días pone a su RSI en niveles sumamente atractivos de rebote para hacer un *swing* clásico. Además, su volumen colosal garantiza que saldremos ilesos si el *trade* va en contra (Filtro de Liquidez superado sin esfuerzo).

### 3. **Grupo Carso** (`GCARSOA1.MX` - $333,333.33)
*   **Fundamental:** El contrato reciente de consolidación de Carso Energy (GSM Bronco) con Pemex para el campo Macavil (a 20 años) acaba de entrar al escrutinio analítico. La promesa de duplicar utilidades de la división en 2026 debe reaccionar positivamente en la acción en los próximos días como premio adelantado de flujo.
*   **Técnico:** Mostró un retroceso momentáneo pero su EMA de corto plazo soporta rebotes agresivos en la zona de los $120-$124 MXN.

### 4. **Genomma Lab** (`LABB.MX` - $333,333.33)
*   **Fundamental:** Historia de "Turnaround" a corto plazo. Reportaron ingresos históricos, dejando atrás la presión de márgenes del año anterior. La gerencia ha sido clara en que reinvertirán, por lo que las agencias calificadoras ya lo están ponderando.
*   **Técnico:** Con un RSI equilibrado (51.25) tiene toda la pista para un Rally alcista. MACD ya en verde intenso confirmando soporte sobre los $17 MXN.

### 5. **Kimberly-Clark** (`KIMBERA.MX` - $250,000.00)
*   **Fundamental:** Posición más defensiva. Aunque su *Beta* es relativamente menor, anunciaron un agresivo programa de recompra de acciones y fuertes dividendos. Esto es un "piso de soporte artificial"; en 3 semanas es un lugar excelente para parquear dinero mientras otras volátiles corren.
*   **Técnico:** En firme tendencia de consolidación post-earnings, EMA 9 cortando por encima.

### 6. **BanBajío** (`BBAJIOO.MX` - $250,000.00)
*   **Fundamental:** Diversificación bancaria forzosa para control de riesgos y exposición secundaria al nearshoring (crédito empresarial en la zona bajío/norte).
*   **Técnico:** De acuerdo a la matriz de correlación generada (`matriz_correlacion.png`) su comportamiento diversifica perfectamente vs. el bloque industrial y de materiales, cumpliendo así nuestro análisis multi-sectorial riguroso. 

---

## 4. Gestión del Trade Activo
Para proteger nuestro liderazgo en el Torneo, se ha implementado mediante Python un **Agente de Monitoreo Diario (`daily_monitor.py`)**. 
*   **Regla de Stop Loss:** Venta inmediata con Notificación si cualquier activo cruza el -3.5% (Prevenir *drawdowns* severos irrecuperables en 21 días).
*   **Regla de Take Profit:** Retirada quirúrgica al llegar entre +6% a +8% de *Alpha* en cualquiera de las posiciones asimétricas.

*Última actualización de análisis: 2026-03-04 11:34:33*
