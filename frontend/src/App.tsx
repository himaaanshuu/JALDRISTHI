import { useEffect, useState, lazy, Suspense } from 'react'
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid, AreaChart, Area,
} from 'recharts'

const GroundwaterMap = lazy(() => import('./components/GroundwaterMap'))
const ChatAssistant = lazy(() => import('./components/ChatAssistant'))

type Page = 'dashboard' | 'assistant' | 'map'

const API = 'http://localhost:8000'

interface HealthStatus {
  status: string
  service: string
  version: string
  timestamp: string
}

interface CategoryDistribution {
  category: string
  count: number
  percentage: number
}

interface TrendPoint {
  assessment_year: number
  total_extraction: number
  avg_extraction_stage: number
  total_recharge: number
  blocks_assessed: number
}

interface TopBlock {
  state: string
  district: string
  block: string
  assessment_year: number
  groundwater_extraction: number
  extraction_stage: number
  category: string
}

interface StateInfo {
  state: string
  districts: number
  blocks: number
  latest_assessment_year: number
  avg_extraction_stage: number
}

const CATEGORY_COLORS: Record<string, string> = {
  Safe: '#10b981',
  'Semi-Critical': '#f59e0b',
  Critical: '#f97316',
  'Over-Exploited': '#a855f7',
}

const CATEGORY_GLOW: Record<string, string> = {
  Safe: '0 0 12px rgba(16, 185, 129, 0.3)',
  'Semi-Critical': '0 0 12px rgba(245, 158, 11, 0.3)',
  Critical: '0 0 12px rgba(249, 115, 22, 0.3)',
  'Over-Exploited': '0 0 12px rgba(168, 85, 247, 0.3)',
}

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [categories, setCategories] = useState<CategoryDistribution[]>([])
  const [trend, setTrend] = useState<TrendPoint[]>([])
  const [topBlocks, setTopBlocks] = useState<TopBlock[]>([])
  const [states, setStates] = useState<StateInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/health`).then(r => r.json()),
      fetch(`${API}/api/analytics/category-distribution`).then(r => r.json()),
      fetch(`${API}/api/analytics/trend`).then(r => r.json()),
      fetch(`${API}/api/analytics/top-extraction?limit=5`).then(r => r.json()),
      fetch(`${API}/api/states`).then(r => r.json()),
    ])
      .then(([h, cat, tr, top, st]) => {
        setHealth(h)
        setCategories(cat)
        setTrend(tr)
        setTopBlocks(top)
        setStates(st)
        setLoading(false)
      })
      .catch(() => {
        setError('Cannot connect to backend at ' + API)
        setLoading(false)
      })
  }, [])

  if (loading) return <LoadingScreen />
  if (error) return <ErrorScreen message={error} />

  const totalUnits = categories.reduce((s, c) => s + c.count, 0)
  const safeUnits = categories.find(c => c.category === 'Safe')?.count ?? 0
  const criticalUnits = categories.find(c => c.category === 'Critical')?.count ?? 0
  const semiCriticalUnits = categories.find(c => c.category === 'Semi-Critical')?.count ?? 0
  const overExploitedUnits = categories.find(c => c.category === 'Over-Exploited')?.count ?? 0
  const avgStage = trend.length ? trend[trend.length - 1].avg_extraction_stage : 0
  const latestExtraction = trend.length ? trend[trend.length - 1].total_extraction : 0
  const prevExtraction = trend.length >= 2 ? trend[trend.length - 2].total_extraction : latestExtraction
  const extractionDelta = latestExtraction - prevExtraction

  return (
    <div className="flex h-screen bg-[var(--bg-deep)] overflow-hidden topo-bg">
      {/* Sidebar */}
      <aside className={`${sidebarCollapsed ? 'w-[72px]' : 'w-[248px]'} bg-[var(--bg-surface)]/80 backdrop-blur-xl border-r border-[var(--border-subtle)] flex flex-col transition-all duration-300 flex-shrink-0 animate-slide-in-left`}>
        {/* Brand */}
        <div className="px-5 py-5 border-b border-[var(--border-subtle)]">
          <a href="#" onClick={(e) => { e.preventDefault(); setPage('dashboard') }} className="cursor-pointer group">
            {!sidebarCollapsed && (
              <div className="flex items-baseline gap-0.5">
                <span className="text-2xl text-[var(--accent-amber)] tracking-tight group-hover:opacity-80 transition-opacity" style={{ fontFamily: 'var(--font-serif)' }}>जल</span>
                <span className="text-xl font-semibold text-[var(--text-primary)] tracking-tight" style={{ fontFamily: 'var(--font-sans)' }}>DRISHTI</span>
              </div>
            )}
            {sidebarCollapsed && (
              <span className="text-xl text-[var(--accent-amber)] block text-center" style={{ fontFamily: 'var(--font-serif)' }}>ज</span>
            )}
          </a>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <SidebarSection label="OVERVIEW" collapsed={sidebarCollapsed}>
            <SidebarItem
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>}
              label="Dashboard"
              active={page === 'dashboard'}
              onClick={() => setPage('dashboard')}
              collapsed={sidebarCollapsed}
            />
            <SidebarItem
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 4.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" /></svg>}
              label="Map View"
              active={page === 'map'}
              onClick={() => setPage('map')}
              collapsed={sidebarCollapsed}
            />
          </SidebarSection>

          <SidebarSection label="INTELLIGENCE" collapsed={sidebarCollapsed}>
            <SidebarItem
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" /></svg>}
              label="AI Assistant"
              active={page === 'assistant'}
              onClick={() => setPage('assistant')}
              collapsed={sidebarCollapsed}
            />
            <SidebarItem
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>}
              label="Trends"
              collapsed={sidebarCollapsed}
              onClick={() => setPage('dashboard')}
            />
            <SidebarItem
              icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>}
              label="Risk Analysis"
              collapsed={sidebarCollapsed}
              onClick={() => setPage('assistant')}
            />
          </SidebarSection>
        </nav>

        {/* Collapse toggle */}
        <div className="px-3 py-3 border-t border-[var(--border-subtle)]">
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]/50 transition-all"
          >
            <svg className={`w-4 h-4 transition-transform ${sidebarCollapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M18.75 19.5l-7.5-7.5 7.5-7.5m-6 15L5.25 12l7.5-7.5" />
            </svg>
            {!sidebarCollapsed && <span>Collapse</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="h-14 bg-[var(--bg-surface)]/60 backdrop-blur-xl border-b border-[var(--border-subtle)] flex items-center justify-between px-6 flex-shrink-0 animate-fade-in">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-[var(--bg-elevated)]/50 border border-[var(--border-subtle)] rounded-lg px-3 py-2 w-80 focus-within:border-[var(--accent-sky)]/30 focus-within:ring-1 focus-within:ring-[var(--accent-sky)]/20 transition-all">
              <svg className="w-4 h-4 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && searchQuery.trim()) {
                    setPage('assistant')
                  }
                }}
                placeholder="Search states, districts..."
                className="bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none w-full"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
              health?.status === 'healthy'
                ? 'bg-[var(--safe)]/10 text-[var(--safe)] border border-[var(--safe)]/20'
                : 'bg-[var(--danger)]/10 text-[var(--danger)] border border-[var(--danger)]/20'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${health?.status === 'healthy' ? 'bg-[var(--safe)]' : 'bg-[var(--danger)]'}`} style={health?.status === 'healthy' ? { animation: 'pulse-glow 2s infinite' } : {}} />
              {health?.status === 'healthy' ? 'System Online' : 'Offline'}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto">
          {page === 'dashboard' && (
            <DashboardPage
              categories={categories}
              trend={trend}
              topBlocks={topBlocks}
              states={states}
              totalUnits={totalUnits}
              safeUnits={safeUnits}
              criticalUnits={criticalUnits}
              semiCriticalUnits={semiCriticalUnits}
              overExploitedUnits={overExploitedUnits}
              avgStage={avgStage}
              latestExtraction={latestExtraction}
              extractionDelta={extractionDelta}
            />
          )}
          {page === 'assistant' && (
            <div className="p-6">
              <Suspense fallback={<PageFallback />}>
                <ChatAssistant initialQuery={searchQuery} />
              </Suspense>
            </div>
          )}
          {page === 'map' && (
            <div className="p-6">
              <Suspense fallback={<PageFallback />}>
                <GroundwaterMap />
              </Suspense>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

// --- Dashboard Page ---

function DashboardPage({ categories, trend, topBlocks, states, totalUnits, safeUnits, criticalUnits, semiCriticalUnits, overExploitedUnits, avgStage, latestExtraction, extractionDelta }: {
  categories: CategoryDistribution[]
  trend: TrendPoint[]
  topBlocks: TopBlock[]
  states: StateInfo[]
  totalUnits: number
  safeUnits: number
  criticalUnits: number
  semiCriticalUnits: number
  overExploitedUnits: number
  avgStage: number
  latestExtraction: number
  extractionDelta: number
}) {
  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <h1 className="text-3xl text-[var(--text-primary)]" style={{ fontFamily: 'var(--font-serif)' }}>Dashboard</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Groundwater assessment overview across India</p>
        </div>
      </div>

      {/* Official Data Source Banner */}
      <div className="glass-card-static px-4 py-3 flex items-center gap-3 animate-fade-in-up delay-1" style={{ borderColor: 'rgba(14, 165, 233, 0.15)' }}>
        <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'var(--accent-sky-glow)' }}>
          <svg className="w-4 h-4 text-[var(--accent-sky)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="text-[11px] font-semibold text-[var(--accent-sky)]">Source: Central Ground Water Board / IN-GRES</div>
          <div className="text-[10px] text-[var(--text-muted)]">
            Official groundwater assessment data from Ministry of Jal Shakti, Government of India
          </div>
        </div>
        <div className="flex-shrink-0 text-right">
          <div className="text-[10px] font-medium text-[var(--accent-sky)]">Assessment Years: 2020, 2022, 2024, 2025</div>
          <div className="text-[9px] text-[var(--text-muted)]">
            <a href="https://cgwb.gov.in/en/ground-water-resource-assessment-0" target="_blank" rel="noopener noreferrer" className="hover:text-[var(--text-secondary)] transition-colors">
              cgwb.gov.in
            </a>
          </div>
        </div>
      </div>

      {/* Stat Cards Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Assessment Units"
          value={totalUnits.toLocaleString()}
          sub={`${states.length} states assessed`}
          icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6z" /></svg>}
          color="var(--accent-sky)"
          delay={2}
        />
        <StatCard
          label="Safe Blocks"
          value={safeUnits.toLocaleString()}
          sub={`${((safeUnits / totalUnits) * 100).toFixed(0)}% of total`}
          icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          color="var(--safe)"
          trend="down"
          trendLabel={`${((safeUnits / totalUnits) * 100).toFixed(0)}%`}
          delay={3}
        />
        <StatCard
          label="Critical + Over-Exploited"
          value={(criticalUnits + overExploitedUnits).toLocaleString()}
          sub={`${((criticalUnits + overExploitedUnits) / totalUnits * 100).toFixed(0)}% of total`}
          icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" /></svg>}
          color="var(--danger)"
          trend="up"
          trendLabel={`${((criticalUnits + overExploitedUnits) / totalUnits * 100).toFixed(0)}%`}
          delay={4}
        />
        <StatCard
          label="Avg Extraction Stage"
          value={`${avgStage.toFixed(1)}%`}
          sub="National average"
          icon={<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 21a8.966 8.966 0 01-5.982-2.275M12 21a8.966 8.966 0 005.982-2.275M12 21V3m0 18c-4.97 0-9-2.686-9-6s4.03-6 9-6 9 2.686 9 6-4.03 6-9 6z" /></svg>}
          color="var(--accent-teal)"
          delay={5}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart - 2 cols */}
        <div className="lg:col-span-2 glass-card p-5 animate-fade-in-up delay-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Extraction Trend</h3>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">National extraction vs recharge (2020-2025)</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-[10px] text-[var(--text-muted)]">
                <span className="w-2 h-2 rounded-full" style={{ background: 'var(--accent-amber)' }} />
                Extraction
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-[var(--text-muted)]">
                <span className="w-2 h-2 rounded-full" style={{ background: 'var(--accent-teal)' }} />
                Recharge
              </div>
              <span className="text-xs text-[var(--text-muted)] bg-[var(--bg-elevated)] border border-[var(--border-subtle)] px-2.5 py-1 rounded-md" style={{ fontFamily: 'var(--font-mono)' }}>
                {trend.length} assessment{trend.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
          <div className="h-[280px]">
            <ResponsiveContainer>
              <AreaChart data={trend} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="gradExtraction" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-amber)" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="var(--accent-amber)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradRecharge" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-teal)" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="var(--accent-teal)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                <XAxis
                  dataKey="assessment_year"
                  stroke="var(--text-muted)"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  fontFamily="var(--font-mono)"
                  tickFormatter={(v) => `'${String(v).slice(2)}`}
                />
                <YAxis
                  stroke="var(--text-muted)"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  fontFamily="var(--font-mono)"
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
                />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-medium)', borderRadius: 8, fontSize: 11, boxShadow: 'var(--shadow-elevated)', color: 'var(--text-primary)' }}
                  formatter={(value: number, name: string) => {
                    if (name === 'total_extraction') return [`${value.toLocaleString()} MCM`, 'Extraction']
                    if (name === 'total_recharge') return [`${value.toLocaleString()} MCM`, 'Recharge']
                    return [`${value.toFixed(1)}%`, 'Stage']
                  }}
                  labelFormatter={(label) => `Assessment Year ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="total_recharge"
                  stroke="var(--accent-teal)"
                  strokeWidth={2}
                  fill="url(#gradRecharge)"
                  name="total_recharge"
                  dot={{ r: 4, fill: 'var(--accent-teal)', stroke: 'var(--bg-surface)', strokeWidth: 2 }}
                  activeDot={{ r: 6, stroke: 'var(--accent-teal)', strokeWidth: 2, fill: 'var(--bg-surface)' }}
                />
                <Area
                  type="monotone"
                  dataKey="total_extraction"
                  stroke="var(--accent-amber)"
                  strokeWidth={2}
                  fill="url(#gradExtraction)"
                  name="total_extraction"
                  dot={{ r: 4, fill: 'var(--accent-amber)', stroke: 'var(--bg-surface)', strokeWidth: 2 }}
                  activeDot={{ r: 6, stroke: 'var(--accent-amber)', strokeWidth: 2, fill: 'var(--bg-surface)' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          {/* Trend insight */}
          {trend.length >= 2 && (
            <div className="mt-3 pt-3 border-t border-[var(--border-subtle)] flex items-center gap-4 text-[11px] text-[var(--text-muted)]">
              <span>
                Extraction trend:
                <span className="font-medium ml-1" style={{
                  color: trend[trend.length - 1].total_extraction > trend[0].total_extraction ? 'var(--danger)' : 'var(--safe)',
                  fontFamily: 'var(--font-mono)',
                }}>
                  {trend[0].total_extraction > 0 ? ((trend[trend.length - 1].total_extraction - trend[0].total_extraction) / trend[0].total_extraction * 100).toFixed(1) : '0'}%
                </span>
                {' '}since {trend[0].assessment_year}
              </span>
              <span className="w-px h-3 bg-[var(--border-subtle)]" />
              <span>
                Stage: {trend[0].avg_extraction_stage.toFixed(1)}%
                <span className="mx-1">&rarr;</span>
                {trend[trend.length - 1].avg_extraction_stage.toFixed(1)}%
              </span>
              <span className="w-px h-3 bg-[var(--border-subtle)]" />
              <span style={{ fontFamily: 'var(--font-mono)' }}>
                Source: CGWB
              </span>
            </div>
          )}
        </div>

        {/* Category Distribution - 1 col */}
        <div className="glass-card p-5 animate-fade-in-up delay-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Category Split</h3>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">{totalUnits} blocks total</p>
            </div>
          </div>
          <div className="h-[180px]">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={categories}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="count"
                  stroke="none"
                >
                  {categories.map((entry) => (
                    <Cell key={entry.category} fill={CATEGORY_COLORS[entry.category] || 'var(--text-muted)'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-medium)', borderRadius: 8, fontSize: 11, boxShadow: 'var(--shadow-elevated)', color: 'var(--text-primary)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2.5 mt-3">
            {categories.map((cat) => (
              <div key={cat.category} className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: CATEGORY_COLORS[cat.category] || 'var(--text-muted)', boxShadow: CATEGORY_GLOW[cat.category] }} />
                  <span className="text-sm text-[var(--text-secondary)]">{cat.category}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{cat.count}</span>
                  <span className="text-xs text-[var(--text-muted)]">({cat.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Extraction Table */}
        <div className="lg:col-span-2 glass-card p-5 animate-fade-in-up delay-7">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--text-primary)]">Top Extraction Regions</h3>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">Highest groundwater extraction districts</p>
            </div>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] text-[var(--text-muted)] uppercase border-b border-[var(--border-subtle)]">
                <th className="pb-2.5 font-medium">District</th>
                <th className="pb-2.5 font-medium">Category</th>
                <th className="pb-2.5 font-medium text-right">Extraction</th>
                <th className="pb-2.5 font-medium text-right">Stage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)]">
              {topBlocks.map((block, i) => (
                <tr key={`${block.block}-${i}`} className="hover:bg-[var(--bg-elevated)]/30 transition-colors">
                  <td className="py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-bold`} style={{
                        background: i === 0 ? 'var(--accent-amber-glow)' : i === 1 ? 'var(--accent-sky-glow)' : i === 2 ? 'var(--accent-teal-glow)' : 'var(--bg-elevated)',
                        color: i === 0 ? 'var(--accent-amber)' : i === 1 ? 'var(--accent-sky)' : i === 2 ? 'var(--accent-teal)' : 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                      }}>
                        {i + 1}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">{block.district}</p>
                        <p className="text-xs text-[var(--text-muted)]">{block.state}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5">
                    <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium`} style={{
                      background: `${CATEGORY_COLORS[block.category]}15`,
                      color: CATEGORY_COLORS[block.category],
                      border: `1px solid ${CATEGORY_COLORS[block.category]}30`,
                    }}>
                      {block.category}
                    </span>
                  </td>
                  <td className="py-3.5 text-right">
                    <span className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{block.groundwater_extraction.toFixed(0)} MCM</span>
                  </td>
                  <td className="py-3.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 h-1.5 bg-[var(--bg-elevated)] rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${Math.min(block.extraction_stage, 100)}%`,
                            backgroundColor: block.extraction_stage > 90 ? 'var(--over-exploited)' : block.extraction_stage > 70 ? 'var(--semi-critical)' : 'var(--safe)',
                            boxShadow: block.extraction_stage > 90 ? 'var(--over-exploited-glow)' : block.extraction_stage > 70 ? 'var(--semi-critical-glow)' : 'var(--safe-glow)',
                          }}
                        />
                      </div>
                      <span className="text-xs text-[var(--text-muted)] w-8 text-right" style={{ fontFamily: 'var(--font-mono)' }}>{block.extraction_stage.toFixed(0)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* State Overview */}
        <div className="glass-card p-5 animate-fade-in-up delay-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--text-primary)]">State Overview</h3>
              <p className="text-sm text-[var(--text-muted)] mt-0.5">Extraction status by state</p>
            </div>
          </div>
          <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
            {states.map((s) => {
              const cat = s.avg_extraction_stage > 90 ? 'Over-Exploited' : s.avg_extraction_stage > 70 ? 'Semi-Critical' : 'Safe'
              const catColor = CATEGORY_COLORS[cat]
              return (
                <div key={s.state} className="group">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-[var(--text-secondary)]">{s.state}</span>
                    <span className="text-xs text-[var(--text-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>{s.avg_extraction_stage.toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 bg-[var(--bg-elevated)] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(s.avg_extraction_stage, 100)}%`,
                        backgroundColor: catColor,
                        boxShadow: `0 0 8px ${catColor}40`,
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-[var(--text-muted)]">{s.blocks} blocks</span>
                    <span className="text-xs font-medium" style={{ color: catColor }}>
                      {cat}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

// --- Sidebar Components ---

function SidebarSection({ label, collapsed, children }: { label: string; collapsed: boolean; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      {!collapsed && <p className="text-[10px] font-semibold text-[var(--text-faint)] uppercase tracking-[0.1em] px-3 mb-1.5">{label}</p>}
      {children}
    </div>
  )
}

function SidebarItem({ icon, label, active, onClick, collapsed }: {
  icon: React.ReactNode; label: string; active?: boolean; onClick?: () => void; collapsed?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={`nav-item w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
        active ? 'active' : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
      } ${collapsed ? 'justify-center' : ''}`}
      title={collapsed ? label : undefined}
    >
      {icon}
      {!collapsed && <span>{label}</span>}
    </button>
  )
}

// --- Shared Components ---

function StatCard({ label, value, sub, icon, color, trend, trendLabel, delay }: {
  label: string; value: string; sub: string; icon: React.ReactNode; color: string; trend?: 'up' | 'down'; trendLabel?: string; delay?: number
}) {
  return (
    <div className={`glass-card p-5 group animate-fade-in-up`} style={{ animationDelay: delay ? `${delay * 0.05}s` : undefined }}>
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `${color}15`, color }}>
          {icon}
        </div>
        {trendLabel && (
          <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium`} style={{
            background: trend === 'up' ? 'var(--danger-glow)' : 'var(--safe-glow)',
            color: trend === 'up' ? 'var(--danger)' : 'var(--safe)',
            border: `1px solid ${trend === 'up' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`,
          }}>
            {trend === 'up' ? '\u2191' : '\u2193'} {trendLabel}
          </span>
        )}
      </div>
      <p className="text-[11px] text-[var(--text-muted)] font-medium uppercase tracking-wider">{label}</p>
      <p className="text-3xl font-semibold text-[var(--text-primary)] mt-1.5" style={{ fontFamily: 'var(--font-mono)' }}>{value}</p>
      <p className="text-xs text-[var(--text-muted)] mt-1.5">{sub}</p>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-[var(--bg-deep)] flex items-center justify-center topo-bg">
      <div className="text-center animate-fade-in">
        <div className="relative w-16 h-16 mx-auto mb-6">
          <div className="absolute inset-0 rounded-full border-2 border-[var(--accent-amber)]/20" />
          <div className="absolute inset-0 rounded-full border-2 border-[var(--accent-amber)] border-t-transparent animate-spin" />
          <div className="absolute inset-2 rounded-full border-2 border-[var(--accent-teal)]/20" />
          <div className="absolute inset-2 rounded-full border-2 border-[var(--accent-teal)] border-b-transparent animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
        </div>
        <p className="text-[var(--accent-amber)] text-lg animate-pulse" style={{ fontFamily: 'var(--font-serif)' }}>Loading JAL-DRISHTI</p>
        <p className="text-[var(--text-muted)] text-xs mt-2">Initializing groundwater intelligence platform</p>
      </div>
    </div>
  )
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="min-h-screen bg-[var(--bg-deep)] flex items-center justify-center px-4 topo-bg">
      <div className="glass-card p-8 max-w-md text-center animate-scale-in">
        <div className="w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center" style={{ background: 'var(--danger-glow)' }}>
          <svg className="w-7 h-7 text-[var(--danger)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
          </svg>
        </div>
        <h2 className="text-[var(--danger)] text-lg font-semibold mb-2">Connection Error</h2>
        <p className="text-[var(--text-secondary)] text-sm">{message}</p>
        <p className="text-[var(--text-muted)] text-xs mt-4">Ensure backend is running on port 8000</p>
      </div>
    </div>
  )
}

function PageFallback() {
  return (
    <div className="flex items-center justify-center h-[60vh]">
      <div className="text-center animate-fade-in">
        <div className="w-8 h-8 border-2 border-[var(--accent-amber)] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-[var(--text-muted)]">Loading...</p>
      </div>
    </div>
  )
}
