import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import type { LatLngTuple } from 'leaflet'
import 'leaflet/dist/leaflet.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface BlockData {
  state: string
  district: string
  block: string
  latitude: number
  longitude: number
  latest_extraction_stage: number
  latest_category: string
}

const CATEGORY_STYLES: Record<string, { color: string; fillColor: string; radius: number; glow: string }> = {
  Safe: { color: '#10b981', fillColor: '#10b981', radius: 7, glow: '0 0 8px rgba(16, 185, 129, 0.4)' },
  'Semi-Critical': { color: '#f59e0b', fillColor: '#f59e0b', radius: 8, glow: '0 0 8px rgba(245, 158, 11, 0.4)' },
  Critical: { color: '#f97316', fillColor: '#f97316', radius: 9, glow: '0 0 10px rgba(249, 115, 22, 0.5)' },
  'Over-Exploited': { color: '#a855f7', fillColor: '#a855f7', radius: 10, glow: '0 0 12px rgba(168, 85, 247, 0.5)' },
}

// India bounding box
const INDIA_BOUNDS: [[number, number], [number, number]] = [
  [6.5, 68.0],   // Southwest (Kanyakumari area)
  [35.5, 97.5],  // Northeast (Arunachal Pradesh)
]
const INDIA_CENTER: LatLngTuple = [22.5, 80.0]

function FitBounds({ blocks }: { blocks: BlockData[] }) {
  const map = useMap()
  useEffect(() => {
    if (blocks.length === 0) {
      map.fitBounds(INDIA_BOUNDS, { padding: [40, 40], maxZoom: 5 })
      return
    }
    const lats = blocks.map(b => b.latitude)
    const lngs = blocks.map(b => b.longitude)
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)],
    ]
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7 })
  }, [blocks, map])
  return null
}

function Legend() {
  const items = [
    { label: 'Safe', color: '#10b981' },
    { label: 'Semi-Critical', color: '#f59e0b' },
    { label: 'Critical', color: '#f97316' },
    { label: 'Over-Exploited', color: '#a855f7' },
  ]

  return (
    <div className="absolute bottom-4 left-4 z-[1000] px-3 py-2.5" style={{
      background: 'var(--bg-glass)',
      backdropFilter: 'blur(16px)',
      border: '1px solid var(--border-medium)',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-elevated)',
    }}>
      <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-1.5 font-medium">Category</p>
      <div className="space-y-1">
        {items.map(item => (
          <div key={item.label} className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: item.color, boxShadow: `0 0 6px ${item.color}60` }}
            />
            <span className="text-[11px] text-[var(--text-secondary)]">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function GroundwaterMap() {
  const [blocks, setBlocks] = useState<BlockData[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetch(`${API}/api/blocks`)
      .then(r => r.json())
      .then(data => {
        setBlocks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = filter === 'all' ? blocks : blocks.filter(b => b.latest_category === filter)

  const categoryCounts = blocks.reduce((acc, b) => {
    acc[b.latest_category] = (acc[b.latest_category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="glass-card overflow-hidden animate-fade-in-up">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[var(--border-subtle)]">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)] uppercase tracking-wider">
              Groundwater Assessment Map
            </h3>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              {blocks.length} blocks across {new Set(blocks.map(b => b.state)).size} states &middot; Click a marker for details
            </p>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            <FilterButton
              label="All"
              count={blocks.length}
              active={filter === 'all'}
              onClick={() => setFilter('all')}
            />
            {Object.entries(categoryCounts).map(([cat, count]) => (
              <FilterButton
                key={cat}
                label={cat}
                count={count}
                active={filter === cat}
                onClick={() => setFilter(cat)}
                color={CATEGORY_STYLES[cat]?.color}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="relative h-[400px] sm:h-[500px] lg:h-[560px]">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center" style={{ background: 'var(--bg-surface)' }}>
            <div className="text-center animate-fade-in">
              <div className="w-8 h-8 border-2 border-[var(--accent-amber)] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              <p className="text-xs text-[var(--text-muted)]">Loading map data...</p>
            </div>
          </div>
        ) : (
          <>
            <MapContainer
              center={INDIA_CENTER}
              zoom={5}
              className="h-full w-full"
              zoomControl={false}
              attributionControl={false}
              maxBounds={INDIA_BOUNDS}
              maxBoundsViscosity={0.8}
              minZoom={4}
              maxZoom={10}
              worldCopyJump={false}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              />
              <FitBounds blocks={filtered} />
              {filtered.filter(b => b.latitude != null && b.longitude != null).map((block, i) => {
                const style = CATEGORY_STYLES[block.latest_category] || CATEGORY_STYLES.Safe
                return (
                  <CircleMarker
                    key={`${block.block}-${i}`}
                    center={[block.latitude, block.longitude]}
                    radius={style.radius}
                    pathOptions={{
                      color: style.color,
                      fillColor: style.fillColor,
                      fillOpacity: 0.75,
                      weight: 2,
                      opacity: 0.9,
                    }}
                  >
                    <Popup className="custom-popup">
                      <div className="min-w-[200px]">
                        <div className="flex items-center gap-2 mb-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full"
                            style={{ backgroundColor: style.color, boxShadow: style.glow }}
                          />
                          <span
                            className="text-xs font-bold uppercase tracking-wide"
                            style={{ color: style.color, fontFamily: 'var(--font-mono)' }}
                          >
                            {block.latest_category}
                          </span>
                        </div>
                        <div className="space-y-1.5 text-sm">
                          <PopupRow label="State" value={block.state} />
                          <PopupRow label="District" value={block.district} />
                          <PopupRow label="Block" value={block.block} />
                          <PopupRow label="Extraction Stage" value={`${block.latest_extraction_stage.toFixed(1)}%`} highlight />
                          <PopupRow label="Coordinates" value={`${block.latitude.toFixed(4)}, ${block.longitude.toFixed(4)}`} />
                        </div>
                      </div>
                    </Popup>
                  </CircleMarker>
                )
              })}
            </MapContainer>
            <Legend />
          </>
        )}
      </div>
    </div>
  )
}

function FilterButton({ label, count, active, onClick, color }: {
  label: string; count: number; active: boolean; onClick: () => void; color?: string
}) {
  return (
    <button
      onClick={onClick}
      className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-all duration-150 flex items-center gap-1.5 border ${
        active
          ? 'border-[var(--accent-amber)] text-[var(--accent-amber)]'
          : 'border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--accent-amber)]/30 hover:text-[var(--text-secondary)]'
      }`}
      style={active ? { background: 'var(--accent-amber-glow)' } : { background: 'var(--bg-glass)' }}
    >
      {color && (
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color, boxShadow: `0 0 4px ${color}60` }} />
      )}
      {label}
      <span className={active ? 'opacity-70' : 'text-[var(--text-faint)]'} style={{ fontFamily: 'var(--font-mono)' }}>{count}</span>
    </button>
  )
}

function PopupRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-[var(--text-muted)] text-xs">{label}</span>
      <span className={`text-xs text-right ${highlight ? 'font-bold' : 'font-medium'}`} style={{
        color: highlight ? 'var(--text-primary)' : 'var(--text-secondary)',
        fontFamily: highlight ? 'var(--font-mono)' : undefined,
      }}>
        {value}
      </span>
    </div>
  )
}
