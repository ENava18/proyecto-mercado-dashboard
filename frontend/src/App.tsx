import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, RefreshCw, BarChart2, DollarSign, Activity, FileText } from 'lucide-react';
import axios from 'axios';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'https://api-proyecto-mercado.onrender.com/api';

interface StockData {
    ticker: string;
    nombre: string;
    precio_entrada: number;
    precio_actual: number;
    target: number;
    variacion_pct: number;
    estado: string;
}

interface SummaryData {
    balance_total: number;
    inversion_inicial: number;
    ganancia_absoluta: number;
    roi_total_pct: number;
}

export default function App() {
    const [portfolio, setPortfolio] = useState<StockData[]>([]);
    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [news, setNews] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(false);
    const [mockChartData, setMockChartData] = useState<any[]>([]);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [portRes, newsRes] = await Promise.all([
                axios.get(`${API_BASE}/portfolio`),
                axios.get(`${API_BASE}/news`)
            ]);
            setPortfolio(portRes.data.portfolio);
            setSummary(portRes.data.summary);
            setNews(newsRes.data.content);

            // Generate some simulated chart data ending with the total balance
            generateChartData(portRes.data.summary);

        } catch (err) {
            console.error("Error fetching data:", err);
        } finally {
            setLoading(false);
        }
    };

    const generateChartData = (summaryData: SummaryData) => {
        // Generate an ascending curvy trend mimicking the realistic performance history
        const data = [];
        let startVal = summaryData.inversion_inicial;
        let endVal = summaryData.balance_total;

        if (startVal === 0) {
            for (let i = 1; i <= 21; i++) data.push({ day: i, value: 0 });
            return setMockChartData(data);
        }

        let currentVal = startVal;
        let trend = (endVal - startVal) / 20; // 21 days total, 20 steps

        for (let i = 1; i <= 21; i++) {
            data.push({ day: i, value: currentVal });
            // Add daily variation combining trend and some random volatility
            currentVal += trend + (Math.random() - 0.5) * (startVal * 0.015);
        }
        // ensure last value accurately points towards current balance
        data[data.length - 1].value = endVal;

        setMockChartData(data);
    }

    useEffect(() => {
        fetchDashboardData();
        // Auto refresh every 5 mins
        const interval = setInterval(fetchDashboardData, 300000);
        return () => clearInterval(interval);
    }, []);

    const handleAnalyze = async () => {
        try {
            setAnalyzing(true);
            await axios.post(`${API_BASE}/analyze`);
            // Wait a bit to simulate processing time, then fetch new data
            setTimeout(() => {
                fetchDashboardData();
                setAnalyzing(false);
            }, 5000);
        } catch (err) {
            console.error(err);
            setAnalyzing(false);
        }
    };

    return (
        <div className="min-h-screen p-4 md:p-8 text-text overflow-hidden">
            {/* Top Navigation / Brand */}
            <header className="flex items-center justify-between mb-8 glass rounded-2xl px-6 py-4">
                <div className="flex items-center gap-3">
                    <div className="bg-primary p-2 rounded-xl">
                        <BarChart2 className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-xl font-bold tracking-wider">Nava <span className="text-primary font-normal text-sm ml-2">Proyecto Mercado</span></h1>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={handleAnalyze}
                        disabled={analyzing}
                        className="flex items-center gap-2 bg-primary hover:bg-primary/80 transition-colors px-6 py-2.5 rounded-full font-medium text-white disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
                        {analyzing ? 'Analizando...' : 'Actualizar Mercado'}
                    </button>
                </div>
            </header>

            {loading && !summary ? (
                <div className="flex flex-col items-center justify-center h-64 gap-4">
                    <RefreshCw className="w-8 h-8 animate-spin text-primary" />
                    <p className="text-muted text-sm">Conectando al servidor financiero...</p>
                </div>
            ) : !summary ? (
                <div className="flex flex-col items-center justify-center h-64 text-center glass rounded-3xl p-8 mb-8">
                    <p className="text-danger font-bold text-lg mb-2">⚠️ Error de conexión</p>
                    <p className="text-muted text-sm">Asegúrate de que el Backend esté en ejecución en el puerto 8000.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Main Left Column */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Hero Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                            {/* Balance Card */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="glass rounded-3xl p-6 relative overflow-hidden"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <span className="text-muted text-sm font-medium">Account balance</span>
                                    <DollarSign className="w-5 h-5 text-muted" />
                                </div>

                                <motion.h2
                                    initial={{ scale: 0.9 }}
                                    animate={{ scale: 1 }}
                                    className="text-4xl font-bold text-white mb-2 font-mono flex items-center"
                                >
                                    ${summary?.balance_total.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                                </motion.h2>

                                <div className="flex items-center gap-2 mt-4">
                                    <span className={`px-2 py-1 rounded-md text-xs font-bold flex items-center gap-1 ${summary!.roi_total_pct >= 0 ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'}`}>
                                        {summary!.roi_total_pct >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                        {summary?.roi_total_pct.toFixed(2)}%
                                    </span>
                                    <span className="text-muted text-xs">Since inception</span>
                                </div>
                            </motion.div>

                            {/* P&L Card */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="glass rounded-3xl p-6 relative overflow-hidden"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <span className="text-muted text-sm font-medium">Profit and losses</span>
                                    <Activity className="w-5 h-5 text-muted" />
                                </div>

                                <motion.h2
                                    initial={{ scale: 0.9 }}
                                    animate={{ scale: 1 }}
                                    className="text-3xl font-bold text-white mb-2 font-mono flex items-center"
                                >
                                    ${summary?.ganancia_absoluta.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                                </motion.h2>

                                <div className="flex items-center gap-2 mt-4">
                                    <span className={`text-xs font-bold ${summary!.ganancia_absoluta >= 0 ? 'text-success' : 'text-danger'}`}>
                                        {summary!.ganancia_absoluta >= 0 ? '+' : ''}${Math.abs(summary?.ganancia_absoluta || 0).toLocaleString('es-MX')}
                                    </span>
                                    <span className="text-muted text-xs">Total ROI</span>
                                </div>
                            </motion.div>
                        </div>

                        {/* Portfolio Overview Chart Area */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className="glass rounded-3xl p-6"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h3 className="text-lg font-bold">Portfolio Overview</h3>
                                    <p className="text-sm text-muted">21 Day Swing Trading Horizon</p>
                                </div>
                                <div className="px-3 py-1 bg-surface/80 rounded-full border border-white/5 text-xs text-muted">
                                    Agente de Rigs Cuantitativos Activo
                                </div>
                            </div>

                            <div className="h-[250px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={mockChartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                                        <XAxis
                                            dataKey="day"
                                            type="number"
                                            domain={[1, 21]}
                                            tickCount={21}
                                            tickFormatter={(val) => `D${val}`}
                                            stroke="#94a3b8"
                                            fontSize={10}
                                            tickMargin={10}
                                        />
                                        <YAxis
                                            domain={['dataMin - 10000', 'dataMax + 10000']}
                                            stroke="#94a3b8"
                                            fontSize={10}
                                            tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                                            orientation="right"
                                            tickMargin={10}
                                        />
                                        <Area type="monotone" dataKey="value" stroke="#34d399" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" connectNulls={true} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#171721', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                            itemStyle={{ color: '#34d399', fontWeight: 'bold' }}
                                            formatter={(value: any) => [`$${Number(value).toLocaleString('es-MX', { minimumFractionDigits: 2 })}`, 'Portafolio']}
                                            labelFormatter={(label) => `Día ${label}`}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </motion.div>

                        {/* News Feed section mapped from Markdown */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className="glass rounded-3xl p-6 mb-6"
                        >
                            <div className="flex items-center gap-2 mb-4">
                                <FileText className="w-5 h-5 text-primary" />
                                <h3 className="text-lg font-bold">Latest Catalysts</h3>
                            </div>
                            <div className="h-48 overflow-y-auto pr-4 custom-scrollbar">
                                <article className="prose prose-sm prose-invert max-w-none text-muted">
                                    <ReactMarkdown>{news}</ReactMarkdown>
                                </article>
                            </div>
                        </motion.div>

                    </div>

                    {/* Right Column (Watchlist) */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 }}
                        className="glass rounded-3xl p-6 h-full flex flex-col"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-lg font-bold flex items-center gap-2">
                                ⚡ Watchlist
                            </h3>
                        </div>

                        {/* Table subheader */}
                        <div className="grid grid-cols-4 text-xs font-semibold text-muted mb-4 pb-2 border-b border-white/10 uppercase tracking-wider">
                            <span className="col-span-2">Name</span>
                            <span className="text-right">Price</span>
                            <span className="text-right">Change</span>
                        </div>

                        <div className="flex-1 overflow-y-auto space-y-1">
                            <AnimatePresence>
                                {portfolio.map((stock, i) => (
                                    <motion.div
                                        key={stock.ticker}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.4 + i * 0.05 }}
                                        className="grid grid-cols-4 items-center p-3 hover:bg-white/5 rounded-xl transition-colors cursor-pointer"
                                    >
                                        <div className="col-span-2 flex items-center gap-3">
                                            {/* Stock Icon Circle */}
                                            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center font-bold text-xs text-white">
                                                {stock.ticker.substring(0, 2)}
                                            </div>
                                            <div>
                                                <div className="font-bold text-sm text-white">{stock.nombre}</div>
                                                <div className="text-xs text-muted">{stock.ticker.replace('.MX', '')}</div>
                                            </div>
                                        </div>

                                        <div className="text-right font-mono text-sm text-white">
                                            ${stock.precio_actual.toFixed(2)}
                                        </div>

                                        <div className={`text-right font-bold text-sm ${stock.variacion_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                                            {stock.variacion_pct >= 0 ? '+' : ''}{stock.variacion_pct.toFixed(2)}%
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </motion.div>

                </div>
            )}
        </div>
    );
}
