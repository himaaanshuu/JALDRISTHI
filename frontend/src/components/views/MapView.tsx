import { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import IndiaLeafletMap, { GroundwaterRecord, MapMode } from '../IndiaLeafletMap';
import { STATE_MAPPINGS, STATUS_COLORS } from '../../data/stateMap';
import {
  getAssessments, getStateTrends,
  getOverview,
  GroundwaterStateData, AssessmentRecord,
} from '../../lib/api';

// ─── Map Mode Config ─────────────────────────────────────────────────────────

const MAP_MODES: { key: MapMode; label: string; icon: string }[] = [
  { key: 'status', label: 'Groundwater Status', icon: '💧' },
  { key: 'extraction', label: 'Extraction Stage', icon: '📊' },
  { key: 'recharge', label: 'Annual Recharge', icon: '🌧️' },
];

const YEARS = [2025, 2024, 2022, 2020];

// ─── Helper: Build groundwater data map from API ─────────────────────────────

function buildGroundwaterMap(records: AssessmentRecord[]): Map<string, GroundwaterRecord> {
  const map = new Map<string, GroundwaterRecord>();
  for (const r of records) {
    if (!r.state) continue;
    const existing = map.get(r.state);
    if (!existing || (r.assessment_year || 0) > (existing.assessment_year || 0)) {
      map.set(r.state, {
        state: r.state,
        district: r.district,
        block: r.block,
        assessment_year: r.assessment_year,
        annual_groundwater_recharge: r.annual_groundwater_recharge,
        extractable_groundwater_resource: r.extractable_groundwater_resource,
        groundwater_extraction: r.groundwater_extraction,
        extraction_stage: r.extraction_stage,
        category: r.category,
        latitude: r.latitude,
        longitude: r.longitude,
      });
    }
  }
  return map;
}

function buildDistrictMap(records: AssessmentRecord[]): Map<string, GroundwaterRecord> {
  const map = new Map<string, GroundwaterRecord>();
  for (const r of records) {
    if (!r.state || !r.district) continue;
    const key = `${r.state}::${r.district}`;
    const existing = map.get(key);
    if (!existing || (r.assessment_year || 0) > (existing.assessment_year || 0)) {
      map.set(key, {
        state: r.state,
        district: r.district,
        block: r.block,
        assessment_year: r.assessment_year,
        annual_groundwater_recharge: r.annual_groundwater_recharge,
        extractable_groundwater_resource: r.extractable_groundwater_resource,
        groundwater_extraction: r.groundwater_extraction,
        extraction_stage: r.extraction_stage,
        category: r.category,
      });
    }
  }
  return map;
}

// ─── Main MapView ────────────────────────────────────────────────────────────

export default function MapView() {
  const [mode, setMode] = useState<MapMode>('status');
  const [year, setYear] = useState(2025);
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);
  const [hoveredState, setHoveredState] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [showDistricts, setShowDistricts] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [panelTab, setPanelTab] = useState<'overview' | 'districts' | 'trends'>('overview');
  const playRef = useRef<NodeJS.Timeout | null>(null);

  // Data states
  const [allRecords, setAllRecords] = useState<AssessmentRecord[]>([]);
  const [stateData, setStateData] = useState<GroundwaterStateData | null>(null);
  const [districtRecords, setDistrictRecords] = useState<AssessmentRecord[]>([]);
  const [trendData, setTrendData] = useState<any>(null);
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // ─── Data Fetching ───────────────────────────────────────────────────────

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getAssessments({ year, limit: 2000 }),
      getOverview(),
    ]).then(([records, ov]) => {
      setAllRecords(records);
      setOverview(ov);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [year]);

  // Fetch state details when selected
  useEffect(() => {
    if (!selectedState) {
      setStateData(null);
      setDistrictRecords([]);
      setTrendData(null);
      setShowDistricts(false);
      return;
    }
    Promise.all([
      getAssessments({ state: selectedState, year, limit: 2000 }),
      getStateTrends(selectedState),
    ]).then(([records, trend]: [AssessmentRecord[], any]) => {
      setStateData({
          state: selectedState,
          data: (() => {
            const blocks = records.filter((r: AssessmentRecord) => r.block);
            const totalRecharge = blocks.reduce((s: number, r: AssessmentRecord) => s + (r.annual_groundwater_recharge || 0), 0);
            const totalExtraction = blocks.reduce((s: number, r: AssessmentRecord) => s + (r.groundwater_extraction || 0), 0);
            const avgStage = blocks.length ? blocks.reduce((s: number, r: AssessmentRecord) => s + (r.extraction_stage || 0), 0) / blocks.length : 0;
            return {
              total_recharge: totalRecharge,
              total_extractable: blocks.reduce((s: number, r: AssessmentRecord) => s + (r.extractable_groundwater_resource || 0), 0),
              total_extraction: totalExtraction,
              avg_stage: avgStage,
              districts: new Set(records.map((r: AssessmentRecord) => r.district).filter(Boolean)).size,
              blocks: blocks.length,
              oe_blocks: records.filter((r: AssessmentRecord) => r.category === 'Over-Exploited' && r.block).length,
              critical_blocks: records.filter((r: AssessmentRecord) => r.category === 'Critical' && r.block).length,
              sc_blocks: records.filter((r: AssessmentRecord) => r.category === 'Semi-Critical' && r.block).length,
              safe_blocks: records.filter((r: AssessmentRecord) => r.category === 'Safe' && r.block).length,
              assessment_year: year,
            };
          })(),
          trend: trend ? {
            direction: trend.direction,
            total_change: trend.total_change,
            percentage_change: trend.percentage_change,
          } : null,
        });
        setDistrictRecords(records);
        setTrendData(trend);
      });
  }, [selectedState, year]);

  // ─── Computed Data ──────────────────────────────────────────────────────

  const groundwaterMap = useMemo(() => buildGroundwaterMap(allRecords), [allRecords]);
  const districtMap = useMemo(() => buildDistrictMap(districtRecords), [districtRecords]);

  const stateSummary = useMemo(() => {
    if (!selectedState) return null;
    const mapping = STATE_MAPPINGS.find(m => m.dbName === selectedState);
    const records = allRecords.filter(r => r.state === selectedState && r.block);
    const categories = {
      Safe: records.filter(r => r.category === 'Safe').length,
      'Semi-Critical': records.filter(r => r.category === 'Semi-Critical').length,
      Critical: records.filter(r => r.category === 'Critical').length,
      'Over-Exploited': records.filter(r => r.category === 'Over-Exploited').length,
    };
    return { mapping, categories, totalBlocks: records.length };
  }, [selectedState, allRecords]);

  // Search results
  const searchResults = useMemo(() => {
    if (!searchQuery || searchQuery.length < 2) return [];
    const q = searchQuery.toLowerCase();
    const results: { name: string; nameHi: string; type: string; dbName: string }[] = [];
    for (const m of STATE_MAPPINGS) {
      if (m.displayName.toLowerCase().includes(q) || m.displayNameHi.includes(q) || m.dbName.toLowerCase().includes(q)) {
        results.push({ name: m.displayName, nameHi: m.displayNameHi, type: m.type, dbName: m.dbName });
      }
    }
    return results.slice(0, 8);
  }, [searchQuery]);

  // Statistics
  const stats = useMemo(() => {
    const byState = new Map<string, AssessmentRecord[]>();
    for (const r of allRecords) {
      if (!r.state) continue;
      if (!byState.has(r.state)) byState.set(r.state, []);
      byState.get(r.state)!.push(r);
    }

    let safe = 0, semi = 0, crit = 0, oe = 0, noData = 0;
    const allStates = STATE_MAPPINGS.map(m => m.dbName);

    for (const stateName of allStates) {
      const records = byState.get(stateName);
      if (!records || records.length === 0) { noData++; continue; }
      const latest = records.filter(r => r.block).sort((a, b) => (b.assessment_year || 0) - (a.assessment_year || 0))[0];
      if (!latest) { noData++; continue; }
      switch (latest.category) {
        case 'Safe': safe++; break;
        case 'Semi-Critical': semi++; break;
        case 'Critical': crit++; break;
        case 'Over-Exploited': oe++; break;
        default: noData++;
      }
    }

    return { safe, semi, crit, oe, noData, total: allStates.length };
  }, [allRecords]);

  // ─── Handlers ───────────────────────────────────────────────────────────

  const handleSelectState = useCallback((state: string) => {
    setSelectedState(state);
    setSelectedDistrict(null);
    setShowDistricts(true);
    setPanelTab('overview');
  }, []);

  const handleSelectDistrict = useCallback((_state: string, district: string) => {
    setSelectedDistrict(district);
    setPanelTab('districts');
  }, []);

  const handleSearchSelect = useCallback((dbName: string) => {
    setSelectedState(dbName);
    setShowDistricts(true);
    setSearchQuery('');
    setShowSearch(false);
  }, []);

  const handleReset = useCallback(() => {
    setSelectedState(null);
    setSelectedDistrict(null);
    setShowDistricts(false);
    setPanelTab('overview');
  }, []);

  // Year animation
  useEffect(() => {
    if (isPlaying) {
      playRef.current = setInterval(() => {
        setYear(prev => {
          const idx = YEARS.indexOf(prev);
          if (idx >= YEARS.length - 1) {
            setIsPlaying(false);
            return YEARS[0];
          }
          return YEARS[idx + 1];
        });
      }, 2000);
    }
    return () => { if (playRef.current) clearInterval(playRef.current); };
  }, [isPlaying]);

  const selectedStateMapping = selectedState ? STATE_MAPPINGS.find(m => m.dbName === selectedState) : null;
  const currentGroundwater = selectedState ? groundwaterMap.get(selectedState) : null;

  return (
    <div className="gw-map-view">
      {/* ─── Map Container ─── */}
      <div className="gw-map-main">
        {loading && (
          <div className="gw-map-loading">
            <div className="gw-map-loading-spinner" />
            <span>Loading groundwater data...</span>
          </div>
        )}

        <IndiaLeafletMap
          groundwaterData={groundwaterMap}
          selectedState={selectedState}
          selectedDistrict={selectedDistrict}
          onSelectState={handleSelectState}
          onSelectDistrict={handleSelectDistrict}
          mode={mode}
          onHover={setHoveredState}
          highlightStates={hoveredState ? [hoveredState] : []}
          districtData={districtMap}
          showDistricts={showDistricts}
        />

        {/* ─── Map Mode Selector ─── */}
        <div className="gw-map-modes">
          {MAP_MODES.map(m => (
            <button
              key={m.key}
              className={`gw-map-mode-btn ${mode === m.key ? 'active' : ''}`}
              onClick={() => setMode(m.key)}
              title={m.label}
            >
              <span className="gw-map-mode-icon">{m.icon}</span>
              <span className="gw-map-mode-label">{m.label}</span>
            </button>
          ))}
        </div>

        {/* ─── Search Box ─── */}
        <div className="gw-map-search">
          <div className="gw-map-search-input-wrap">
            <svg className="gw-map-search-icon" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
            <input
              type="text"
              placeholder="Search states, districts..."
              value={searchQuery}
              onChange={e => { setSearchQuery(e.target.value); setShowSearch(true); }}
              onFocus={() => setShowSearch(true)}
              onBlur={() => setTimeout(() => setShowSearch(false), 200)}
              className="gw-map-search-input"
            />
          </div>
          {showSearch && searchResults.length > 0 && (
            <div className="gw-map-search-results">
              {searchResults.map(r => (
                <button
                  key={r.dbName}
                  className="gw-map-search-result"
                  onMouseDown={() => handleSearchSelect(r.dbName)}
                >
                  <span className="gw-map-search-result-name">{r.name}</span>
                  <span className="gw-map-search-result-hi">{r.nameHi}</span>
                  <span className="gw-map-search-result-type">{r.type}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ─── Year Slider ─── */}
        <div className="gw-map-year-control">
          <button className="gw-map-year-btn" onClick={() => setIsPlaying(!isPlaying)} title={isPlaying ? 'Pause' : 'Play'}>
            {isPlaying ? '⏸' : '▶'}
          </button>
          <button
            className="gw-map-year-btn"
            onClick={() => { const i = YEARS.indexOf(year); if (i > 0) setYear(YEARS[i - 1]); }}
            disabled={year === YEARS[0]}
          >
            ◀
          </button>
          <div className="gw-map-year-slider">
            {YEARS.map(y => (
              <button
                key={y}
                className={`gw-map-year-dot ${y === year ? 'active' : ''}`}
                onClick={() => setYear(y)}
              >
                <span className="gw-map-year-label">{y}</span>
              </button>
            ))}
          </div>
          <button
            className="gw-map-year-btn"
            onClick={() => { const i = YEARS.indexOf(year); if (i < YEARS.length - 1) setYear(YEARS[i + 1]); }}
            disabled={year === YEARS[YEARS.length - 1]}
          >
            ▶
          </button>
        </div>

        {/* ─── Legend ─── */}
        <div className="gw-map-legend">
          <div className="gw-map-legend-title">
            {mode === 'status' ? 'Assessment Category' :
             mode === 'extraction' ? 'Extraction Stage' : 'Annual Recharge'}
          </div>
          {mode === 'status' || mode === 'extraction' ? (
            <div className="gw-map-legend-items">
              {Object.entries(STATUS_COLORS).filter(([k]) => k !== 'No Data').map(([cat, color]) => (
                <div key={cat} className="gw-map-legend-item">
                  <span className="gw-map-legend-dot" style={{ background: color }} />
                  <span>{cat}</span>
                </div>
              ))}
              <div className="gw-map-legend-item">
                <span className="gw-map-legend-dot" style={{ background: STATUS_COLORS['No Data'] }} />
                <span>No Data</span>
              </div>
            </div>
          ) : (
            <div className="gw-map-legend-items">
              <div className="gw-map-legend-item"><span className="gw-map-legend-dot" style={{ background: '#10b981' }} /><span>High (&gt;5000 MCM)</span></div>
              <div className="gw-map-legend-item"><span className="gw-map-legend-dot" style={{ background: '#34d399' }} /><span>Medium-High</span></div>
              <div className="gw-map-legend-item"><span className="gw-map-legend-dot" style={{ background: '#6ee7b7' }} /><span>Medium</span></div>
              <div className="gw-map-legend-item"><span className="gw-map-legend-dot" style={{ background: '#a7f3d0' }} /><span>Low</span></div>
              <div className="gw-map-legend-item"><span className="gw-map-legend-dot" style={{ background: STATUS_COLORS['No Data'] }} /><span>No Data</span></div>
            </div>
          )}
        </div>

        {/* ─── Quick Stats ─── */}
        <div className="gw-map-stats">
          <div className="gw-map-stat">
            <span className="gw-map-stat-value">{stats.total}</span>
            <span className="gw-map-stat-label">States/UTs</span>
          </div>
          <div className="gw-map-stat safe"><span className="gw-map-stat-value">{stats.safe}</span><span className="gw-map-stat-label">Safe</span></div>
          <div className="gw-map-stat semi"><span className="gw-map-stat-value">{stats.semi}</span><span className="gw-map-stat-label">Semi-Critical</span></div>
          <div className="gw-map-stat critical"><span className="gw-map-stat-value">{stats.crit}</span><span className="gw-map-stat-label">Critical</span></div>
          <div className="gw-map-stat oe"><span className="gw-map-stat-value">{stats.oe}</span><span className="gw-map-stat-label">Over-Exploited</span></div>
        </div>
      </div>

      {/* ─── Side Panel ─── */}
      <div className={`gw-map-panel ${selectedState ? 'open' : ''}`}>
        {selectedState && selectedStateMapping ? (
          <>
            {/* Panel Header */}
            <div className="gw-map-panel-header">
              <div>
                <div className="gw-map-panel-state">{selectedStateMapping.displayName}</div>
                <div className="gw-map-panel-state-hi">{selectedStateMapping.displayNameHi}</div>
              </div>
              <button className="gw-map-panel-close" onClick={handleReset}>✕</button>
            </div>

            {/* Breadcrumb */}
            <div className="gw-map-breadcrumb">
              <span className="gw-map-bc-item" onClick={handleReset}>India</span>
              <span className="gw-map-bc-sep">/</span>
              <span className="gw-map-bc-item active">{selectedStateMapping.displayName}</span>
              {selectedDistrict && (
                <>
                  <span className="gw-map-bc-sep">/</span>
                  <span className="gw-map-bc-item active">{selectedDistrict}</span>
                </>
              )}
            </div>

            {/* Status Badge */}
            {currentGroundwater && (
              <div className="gw-map-panel-status">
                <div className="gw-map-panel-status-label">Groundwater Status</div>
                <div
                  className="gw-map-panel-status-badge"
                  style={{ background: STATUS_COLORS[currentGroundwater.category || 'No Data'] || STATUS_COLORS['No Data'] }}
                >
                  {currentGroundwater.category || 'No Data'}
                </div>
              </div>
            )}

            {/* Tab Navigation */}
            <div className="gw-map-panel-tabs">
              <button className={`gw-map-panel-tab ${panelTab === 'overview' ? 'active' : ''}`} onClick={() => setPanelTab('overview')}>Overview</button>
              <button className={`gw-map-panel-tab ${panelTab === 'districts' ? 'active' : ''}`} onClick={() => setPanelTab('districts')}>Districts</button>
              <button className={`gw-map-panel-tab ${panelTab === 'trends' ? 'active' : ''}`} onClick={() => setPanelTab('trends')}>Trends</button>
            </div>

            {/* Panel Content */}
            <div className="gw-map-panel-content">
              {panelTab === 'overview' && stateData && (
                <div className="gw-map-panel-metrics">
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Assessment Year</span>
                    <span className="gw-map-panel-metric-value">{stateData.data.assessment_year}</span>
                  </div>
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Stage of Extraction</span>
                    <span className="gw-map-panel-metric-value highlight">{stateData.data.avg_stage.toFixed(1)}%</span>
                  </div>
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Annual Recharge</span>
                    <span className="gw-map-panel-metric-value">{stateData.data.total_recharge.toLocaleString()} MCM</span>
                  </div>
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Extractable Resource</span>
                    <span className="gw-map-panel-metric-value">{stateData.data.total_extractable.toLocaleString()} MCM</span>
                  </div>
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Groundwater Extraction</span>
                    <span className="gw-map-panel-metric-value">{stateData.data.total_extraction.toLocaleString()} MCM</span>
                  </div>
                  <div className="gw-map-panel-metric">
                    <span className="gw-map-panel-metric-label">Assessment Units</span>
                    <span className="gw-map-panel-metric-value">{stateData.data.blocks}</span>
                  </div>

                  {/* Category Breakdown */}
                  <div className="gw-map-panel-divider" />
                  <div className="gw-map-panel-metric-label">Category Breakdown</div>
                  <div className="gw-map-panel-categories">
                    {stateSummary && Object.entries(stateSummary.categories).map(([cat, count]) => (
                      <div key={cat} className="gw-map-panel-cat">
                        <span className="gw-map-panel-cat-dot" style={{ background: STATUS_COLORS[cat] }} />
                        <span className="gw-map-panel-cat-name">{cat}</span>
                        <span className="gw-map-panel-cat-count">{count}</span>
                      </div>
                    ))}
                  </div>

                  {/* Trend */}
                  {stateData.trend && (
                    <>
                      <div className="gw-map-panel-divider" />
                      <div className="gw-map-panel-metric">
                        <span className="gw-map-panel-metric-label">Trend</span>
                        <span className={`gw-map-panel-metric-value trend ${stateData.trend.direction}`}>
                          {stateData.trend.direction === 'improving' ? '↓ Improving' :
                           stateData.trend.direction === 'deteriorating' ? '↑ Deteriorating' : '→ Stable'}
                          {' '}({stateData.trend.percentage_change > 0 ? '+' : ''}{stateData.trend.percentage_change.toFixed(1)}%)
                        </span>
                      </div>
                    </>
                  )}
                </div>
              )}

              {panelTab === 'districts' && (
                <div className="gw-map-panel-districts">
                  {districtRecords.length > 0 ? (
                    <>
                      <div className="gw-map-panel-districts-header">
                        Districts in {selectedStateMapping.displayName}
                      </div>
                      {(() => {
                        const byDistrict = new Map<string, AssessmentRecord[]>();
                        for (const r of districtRecords) {
                          if (!r.district) continue;
                          if (!byDistrict.has(r.district)) byDistrict.set(r.district, []);
                          byDistrict.get(r.district)!.push(r);
                        }
                        const districts = Array.from(byDistrict.entries())
                          .map(([name, records]) => ({
                            name,
                            category: records.find(r => r.block)?.category || records[0]?.category || 'No Data',
                            stage: records.filter(r => r.block).reduce((s, r) => s + (r.extraction_stage || 0), 0) / Math.max(records.filter(r => r.block).length, 1),
                            blocks: records.filter(r => r.block).length,
                          }))
                          .sort((a, b) => b.stage - a.stage);

                        return districts.map(d => (
                          <button
                            key={d.name}
                            className={`gw-map-panel-district ${d.name === selectedDistrict ? 'selected' : ''}`}
                            onClick={() => handleSelectDistrict(selectedState!, d.name)}
                          >
                            <div className="gw-map-panel-district-name">{d.name}</div>
                            <div className="gw-map-panel-district-meta">
                              <span className="gw-map-panel-cat-dot" style={{ background: STATUS_COLORS[d.category] || STATUS_COLORS['No Data'] }} />
                              <span>{d.category}</span>
                              <span className="gw-map-panel-district-stage">{d.stage.toFixed(1)}%</span>
                              <span className="gw-map-panel-district-blocks">{d.blocks} blocks</span>
                            </div>
                          </button>
                        ));
                      })()}
                    </>
                  ) : (
                    <div className="gw-map-panel-empty">No district-level data available</div>
                  )}
                </div>
              )}

              {panelTab === 'trends' && trendData && (
                <div className="gw-map-panel-trends">
                  <div className="gw-map-panel-trends-header">
                    Multi-Year Trend: {selectedStateMapping.displayName}
                  </div>
                  {trendData.points && trendData.points.length > 0 ? (
                    <div className="gw-map-panel-trend-chart">
                      <svg viewBox="0 0 300 150" className="gw-trend-svg">
                        {(() => {
                          const points = trendData.points;
                          const maxVal = Math.max(...points.map((p: any) => p.value));
                          const minVal = Math.min(...points.map((p: any) => p.value));
                          const range = maxVal - minVal || 1;
                          const padding = 20;
                          const w = 300 - padding * 2;
                          const h = 150 - padding * 2;

                          const pathPoints = points.map((p: any, i: number) => {
                            const x = padding + (i / (points.length - 1)) * w;
                            const y = padding + (1 - (p.value - minVal) / range) * h;
                            return `${x},${y}`;
                          });

                          return (
                            <>
                              <polyline
                                points={pathPoints.join(' ')}
                                fill="none"
                                stroke="#4da8ff"
                                strokeWidth="2"
                                strokeLinejoin="round"
                              />
                              {points.map((p: any, i: number) => {
                                const x = padding + (i / (points.length - 1)) * w;
                                const y = padding + (1 - (p.value - minVal) / range) * h;
                                return (
                                  <g key={i}>
                                    <circle cx={x} cy={y} r="4" fill="#4da8ff" />
                                    <text x={x} y={y - 10} textAnchor="middle" fill="#94a3b8" fontSize="10">
                                      {p.value.toFixed(1)}%
                                    </text>
                                    <text x={x} y={h + padding + 15} textAnchor="middle" fill="#64748b" fontSize="10">
                                      {p.year}
                                    </text>
                                  </g>
                                );
                              })}
                            </>
                          );
                        })()}
                      </svg>
                      <div className="gw-map-panel-trend-info">
                        <div className="gw-map-panel-trend-metric">
                          Direction:
                          <span className={`trend ${trendData.direction}`}>
                            {trendData.direction === 'improving' ? ' Improving' :
                             trendData.direction === 'deteriorating' ? ' Deteriorating' : ' Stable'}
                          </span>
                        </div>
                        <div className="gw-map-panel-trend-metric">
                          Change: {trendData.total_change > 0 ? '+' : ''}{trendData.total_change.toFixed(1)}
                          ({trendData.percentage_change > 0 ? '+' : ''}{trendData.percentage_change.toFixed(1)}%)
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="gw-map-panel-empty">Insufficient data for trend analysis</div>
                  )}
                </div>
              )}
            </div>
          </>
        ) : (
          /* ─── Default: India Overview ─── */
          <div className="gw-map-panel-overview">
            <div className="gw-map-panel-overview-header">
              <div className="gw-map-panel-overview-title">INDIA GROUNDWATER OVERVIEW</div>
              <div className="gw-map-panel-overview-subtitle">भारत भूजल अवलोकन</div>
            </div>
            <div className="gw-map-panel-overview-year">Assessment Year: {year}</div>
            {overview && (
              <div className="gw-map-panel-overview-stats">
                <div className="gw-map-panel-overview-stat">
                  <span className="gw-map-panel-overview-stat-value">{overview.states || stats.total}</span>
                  <span className="gw-map-panel-overview-stat-label">States/UTs Covered</span>
                </div>
                <div className="gw-map-panel-overview-stat">
                  <span className="gw-map-panel-overview-stat-value">{overview.blocks || 0}</span>
                  <span className="gw-map-panel-overview-stat-label">Assessment Units</span>
                </div>
                <div className="gw-map-panel-overview-divider" />
                <div className="gw-map-panel-overview-stat safe">
                  <span className="gw-map-panel-overview-stat-value">{overview.safe_blocks || stats.safe}</span>
                  <span className="gw-map-panel-overview-stat-label">Safe</span>
                </div>
                <div className="gw-map-panel-overview-stat semi">
                  <span className="gw-map-panel-overview-stat-value">{overview.sc_blocks || stats.semi}</span>
                  <span className="gw-map-panel-overview-stat-label">Semi-Critical</span>
                </div>
                <div className="gw-map-panel-overview-stat critical">
                  <span className="gw-map-panel-overview-stat-value">{overview.critical_blocks || stats.crit}</span>
                  <span className="gw-map-panel-overview-stat-label">Critical</span>
                </div>
                <div className="gw-map-panel-overview-stat oe">
                  <span className="gw-map-panel-overview-stat-value">{overview.oe_blocks || stats.oe}</span>
                  <span className="gw-map-panel-overview-stat-label">Over-Exploited</span>
                </div>
                <div className="gw-map-panel-overview-divider" />
                <div className="gw-map-panel-overview-stat">
                  <span className="gw-map-panel-overview-stat-value">{(overview.total_extraction || 0).toLocaleString()} MCM</span>
                  <span className="gw-map-panel-overview-stat-label">Total Extraction</span>
                </div>
                <div className="gw-map-panel-overview-stat">
                  <span className="gw-map-panel-overview-stat-value">{(overview.total_recharge || 0).toLocaleString()} MCM</span>
                  <span className="gw-map-panel-overview-stat-label">Total Recharge</span>
                </div>
              </div>
            )}
            <div className="gw-map-panel-overview-hint">
              Click on a state to view detailed groundwater intelligence
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
