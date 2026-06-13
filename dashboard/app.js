// Genesis System3 Dashboard - Vue3 Application
const { createApp, ref, computed, onMounted, onUnmounted } = Vue;

const API_BASE = window.location.origin; // local Codespace preview

createApp({
    setup() {
        // State
        const activeTab = ref('overview');
        const systemStatus = ref('LIVE');
        const selectedUnderlying = ref('NIFTY');
        const underlyings = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX'];
        
        const tabs = [
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'latency', label: 'Latency', icon: '⚡' },
            { id: 'risk', label: 'Risk', icon: '🛡️' },
            { id: 'greeks', label: 'Greeks', icon: '📈' },
            { id: 'options', label: 'Option Chain', icon: '🔗' },
            { id: 'trades', label: 'Live Trades', icon: '💹' },
            { id: 'rankings', label: 'Rankings', icon: '🏆' },
            { id: 'accuracy', label: 'Accuracy', icon: '🎯' },
            { id: 'syshealth', label: 'System Health', icon: '🩺' },
        ];

        const metrics = ref({
            pnl: 0,
            pnlChange: 0,
            cycleDuration: 0,
            fetchDuration: 0,
            strategyDuration: 0,
            tradesExecuted: 0,
            openPositions: 0,
            greeksSuccess: 0,
            greeksFallback: 0,
            greeksUnavailable: 0,
            lastFetch: null,
            dataSuccessRate: 0,
            signalSuccessRate: 0,
            maxDrawdown: 0,
            winRate: 0,
            totalTrades: 0,
            winningTrades: 0
        });

        const chainData = ref({
            spot: 0,
            pcr: 1.0,
            totalContracts: 0,
            contracts: []
        });

        const liveTrades = ref([]);

        // System3 analytics state
        const gainRankData = ref({ status: 'loading', latest: null, history: [], total_days: 0 });
        const accuracyData = ref({ status: 'loading', trend: [], avg_rho: null, retrain_needed: false, days_available: 0 });
        const systemHealth = ref({ status: 'loading', token: null, datasource_health: null, datasource_resilience: 'UNKNOWN', retrain_needed: false, jobs: [] });

        // Computed
        const filteredContracts = computed(() => {
            return chainData.value.contracts || [];
        });

        // Methods
        const formatNumber = (num) => {
            if (!num && num !== 0) return '0';
            return parseFloat(num).toLocaleString('en-IN', { maximumFractionDigits: 2 });
        };

        const formatTime = (timestamp) => {
            if (!timestamp) return 'N/A';
            try {
                const date = new Date(timestamp);
                return date.toLocaleTimeString('en-IN');
            } catch {
                return 'N/A';
            }
        };

        const getPnLClass = () => {
            return metrics.value.pnl >= 0 ? 'green' : 'red';
        };

        const getPerfClass = () => {
            const dur = metrics.value.cycleDuration;
            if (dur < 3) return 'green';
            if (dur < 10) return 'yellow';
            return 'red';
        };

        const getGreeksClass = () => {
            const success = metrics.value.greeksSuccess;
            if (success >= 95) return 'green';
            if (success >= 80) return 'yellow';
            return 'red';
        };

        const getLatencyClass = (value) => {
            if (value < 3) return 'green';
            if (value < 10) return 'yellow';
            return 'red';
        };

        const getRiskClass = (value) => {
            if (value < 5) return 'green';
            if (value < 10) return 'yellow';
            return 'red';
        };

        // API Calls
        const fetchHealth = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/health`);
                const data = await response.json();
                
                metrics.value.pnl = data.total_pnl || 0;
                metrics.value.cycleDuration = data.performance_sla?.cycle_duration_sec || 0;
                metrics.value.fetchDuration = data.performance_sla?.fetch_duration_sec || 0;
                metrics.value.strategyDuration = data.performance_sla?.strategy_duration_sec || 0;
                metrics.value.tradesExecuted = data.trades_executed || 0;
                metrics.value.openPositions = data.open_positions || 0;
                metrics.value.lastFetch = data.last_fetch;
                metrics.value.dataSuccessRate = data.data_success_rate || 0;
                metrics.value.signalSuccessRate = data.signal_success_rate || 0;
                systemStatus.value = data.mode || 'UNKNOWN';
            } catch (error) {
                console.error('Error fetching health:', error);
            }
        };

        const fetchPerformance = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/perf`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = await response.json();
                
                if (data.current) {
                    metrics.value.cycleDuration = data.current.cycle_duration_sec || 0;
                    metrics.value.fetchDuration = data.current.fetch_duration_sec || 0;
                    metrics.value.strategyDuration = data.current.strategy_duration_sec || 0;
                }
            } catch (error) {
                console.error('Error fetching performance:', error);
                // Don't reset on error, keep previous values
            }
        };

        const fetchPnL = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/pnl`);
                const data = await response.json();
                
                if (data.summary) {
                    const summary = data.summary;
                    const prevPnL = metrics.value.pnl;
                    metrics.value.pnl = summary.total_pnl || 0;
                    metrics.value.winRate = summary.win_rate || 0;
                    metrics.value.totalTrades = summary.total_trades || 0;
                    metrics.value.winningTrades = summary.winning_trades || 0;
                    metrics.value.maxDrawdown = summary.max_drawdown || 0;
                    
                    // Calculate PnL change percentage
                    if (prevPnL !== 0) {
                        metrics.value.pnlChange = ((metrics.value.pnl - prevPnL) / Math.abs(prevPnL)) * 100;
                    } else {
                        metrics.value.pnlChange = 0;
                    }
                }
            } catch (error) {
                console.error('Error fetching PnL:', error);
            }
        };

        const fetchChainData = async (underlying) => {
            try {
                const response = await fetch(`${API_BASE}/api/chain/${underlying}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = await response.json();
                
                chainData.value = {
                    spot: data.spot || 0,
                    pcr: data.pcr || 1.0,
                    totalContracts: data.total_contracts || 0,
                    contracts: data.contracts || []
                };
                
                // Update Greeks status after fetching chain data
                await fetchGreeksStatus();
            } catch (error) {
                console.error('Error fetching chain data:', error);
                chainData.value = {
                    spot: 0,
                    pcr: 1.0,
                    totalContracts: 0,
                    contracts: []
                };
                // Reset Greeks metrics on error
                metrics.value.greeksSuccess = 0;
                metrics.value.greeksFallback = 0;
                metrics.value.greeksUnavailable = 0;
            }
        };

        const fetchPositions = async () => {
            try {
                const response = await fetch(`${API_BASE}/api/positions`);
                const data = await response.json();
                
                liveTrades.value = (data.positions || []).map(pos => ({
                    id: pos.position_id,
                    symbol: pos.symbol || `${pos.underlying} ${pos.strike}${pos.option_type}`,
                    entryPrice: pos.entry_price || 0,
                    currentPrice: pos.current_price || pos.entry_price || 0,
                    pnl: pos.unrealized_pnl || 0
                }));
            } catch (error) {
                console.error('Error fetching positions:', error);
            }
        };

        // System3 analytics fetch functions
        const fetchGainRank = async () => {
            try {
                const r = await fetch(`${API_BASE}/api/gain_rank`);
                if (!r.ok) return;
                gainRankData.value = await r.json();
            } catch (e) {
                console.error('Error fetching gain rank:', e);
            }
        };

        const fetchAccuracyTrend = async () => {
            try {
                const r = await fetch(`${API_BASE}/api/accuracy_trend`);
                if (!r.ok) return;
                accuracyData.value = await r.json();
            } catch (e) {
                console.error('Error fetching accuracy trend:', e);
            }
        };

        const fetchSystemHealth = async () => {
            try {
                const r = await fetch(`${API_BASE}/api/system_health`);
                if (!r.ok) return;
                systemHealth.value = await r.json();
            } catch (e) {
                console.error('Error fetching system health:', e);
            }
        };

        const fetchGreeksStatus = async () => {
            // Ensure chain data is loaded first
            if (!chainData.value.contracts || chainData.value.contracts.length === 0) {
                await fetchChainData(selectedUnderlying.value);
            }
            
            // Calculate Greeks status from chain data
            if (chainData.value.contracts && chainData.value.contracts.length > 0) {
                const contracts = chainData.value.contracts;
                const withGreeks = contracts.filter(c => {
                    const delta = c.delta !== null && c.delta !== undefined && c.delta !== '';
                    const gamma = c.gamma !== null && c.gamma !== undefined && c.gamma !== '';
                    const vega = c.vega !== null && c.vega !== undefined && c.vega !== '';
                    const theta = c.theta !== null && c.theta !== undefined && c.theta !== '';
                    return delta && gamma && vega && theta;
                });
                const withPartialGreeks = contracts.filter(c => {
                    const hasDelta = c.delta !== null && c.delta !== undefined && c.delta !== '';
                    const hasGamma = c.gamma !== null && c.gamma !== undefined && c.gamma !== '';
                    const hasVega = c.vega !== null && c.vega !== undefined && c.vega !== '';
                    const hasTheta = c.theta !== null && c.theta !== undefined && c.theta !== '';
                    return hasDelta || hasGamma || hasVega || hasTheta;
                });
                const total = contracts.length;
                metrics.value.greeksSuccess = total > 0 ? (withGreeks.length / total * 100) : 0;
                metrics.value.greeksFallback = Math.max(0, withPartialGreeks.length - withGreeks.length);
                metrics.value.greeksUnavailable = Math.max(0, total - withPartialGreeks.length);
            } else {
                // Reset if no data
                metrics.value.greeksSuccess = 0;
                metrics.value.greeksFallback = 0;
                metrics.value.greeksUnavailable = 0;
            }
        };

        // Update all data — overlap guard prevents concurrent fetches
        let _updating = false;
        const updateAll = async () => {
            if (_updating) return;
            _updating = true;
            try {
                await Promise.all([
                    fetchHealth(),
                    fetchPerformance(),
                    fetchPnL(),
                    fetchPositions()
                ]);
                if (activeTab.value === 'options' || activeTab.value === 'greeks') {
                    await fetchChainData(selectedUnderlying.value);
                }
                if (activeTab.value === 'rankings') {
                    await fetchGainRank();
                }
                if (activeTab.value === 'accuracy') {
                    await fetchAccuracyTrend();
                }
                if (activeTab.value === 'syshealth') {
                    await fetchSystemHealth();
                }
            } catch (error) {
                console.error('Error updating data:', error);
            } finally {
                _updating = false;
            }
        };

        // Lifecycle
        let updateInterval = null;

        onMounted(() => {
            // Initial data load
            updateAll();

            // Poll every 5 seconds — no overlapping requests
            updateInterval = setInterval(updateAll, 5000);
            
            // Watch for tab changes to load tab-specific data
            Vue.watch(() => activeTab.value, async (newTab) => {
                if (newTab === 'options' || newTab === 'greeks') {
                    await fetchChainData(selectedUnderlying.value);
                }
                if (newTab === 'rankings') await fetchGainRank();
                if (newTab === 'accuracy') await fetchAccuracyTrend();
                if (newTab === 'syshealth') await fetchSystemHealth();
            });
            
            // Watch for underlying changes
            Vue.watch(() => selectedUnderlying.value, async (newUnderlying) => {
                if (activeTab.value === 'options' || activeTab.value === 'greeks') {
                    await fetchChainData(newUnderlying);
                }
            });
        });

        onUnmounted(() => {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });

        // Watch for tab changes
        const watchTab = () => {
            if (activeTab.value === 'options' && selectedUnderlying.value) {
                fetchChainData(selectedUnderlying.value);
            }
        };

        return {
            activeTab,
            systemStatus,
            selectedUnderlying,
            underlyings,
            tabs,
            metrics,
            chainData,
            liveTrades,
            gainRankData,
            accuracyData,
            systemHealth,
            filteredContracts,
            formatNumber,
            formatTime,
            getPnLClass,
            getPerfClass,
            getGreeksClass,
            getLatencyClass,
            getRiskClass,
            fetchChainData,
            fetchGainRank,
            fetchAccuracyTrend,
            fetchSystemHealth,
            watchTab
        };
    }
}).mount('#app');
