import { useEffect, useRef, useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const API = 'http://localhost:8000'

const PIE_COLORS = ['#10b981', '#f59e0b', '#f97316', '#f43f5e']

interface ChatSource {
  title: string
  endpoint: string
  record_count: number
  data: Record<string, unknown>[]
}

interface ChartData {
  type: 'line' | 'bar' | 'pie'
  title: string
  data: Record<string, unknown>[]
}

interface ParsedIntent {
  intent: string
  state: string | null
  district: string | null
  block: string | null
  year: number | null
  comparison_years: number[]
  metric: string | null
  category: string | null
  confidence: number
}

interface Evidence {
  source: string
  assessment_year: number | null
  location: string
  records_used: number
  confidence: 'High' | 'Medium' | 'Low'
  source_url: string
  data_type: 'official' | 'synthetic' | 'mixed'
}

interface RiskFactor {
  factor: string
  contribution: number
  description: string
}

interface RiskScore {
  state: string
  year: number
  risk_score: number
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical'
  avg_extraction_stage: number
  dominant_category: string
  trend_direction: string
  factors: RiskFactor[]
  disclaimer: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  suggestedFollowups?: string[]
  parsedIntent?: ParsedIntent
  chart?: ChartData
  evidence?: Evidence
  riskScore?: RiskScore
  timestamp: Date
}

const SUGGESTED_QUESTIONS = [
  'What is the groundwater status of Rajasthan?',
  'Compare extraction trends between 2020 and 2025.',
  'Which districts have the highest extraction stage?',
  'Show over-exploited areas in Punjab.',
  'What is the risk score for Haryana?',
  'पंजाब की जल स्थिति बताओ',
]

export default function ChatAssistant({ initialQuery = '' }: { initialQuery?: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isDemoRunning, setIsDemoRunning] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const initialQuerySent = useRef(false)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    if (initialQuery && !initialQuerySent.current && messages.length === 0) {
      initialQuerySent.current = true
      sendMessage(initialQuery)
    }
  }, [initialQuery])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isTyping) return

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.reply,
        sources: data.sources,
        suggestedFollowups: data.suggested_followups,
        parsedIntent: data.parsed_intent,
        chart: data.chart,
        evidence: data.evidence,
        riskScore: data.risk_score,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I could not connect to the backend. Please ensure the API server is running on port 8000.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsTyping(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    inputRef.current?.focus()
  }

  const runDemo = async () => {
    if (isDemoRunning || isTyping) return
    setIsDemoRunning(true)
    setMessages([])

    const demoQueries = [
      'What is the groundwater status of Haryana?',
      'Compare extraction trends between 2020 and 2025.',
      'Which districts have the highest extraction stage?',
      'पंजाब की जल स्थिति बताओ',
    ]

    const delays = [1800, 2200, 1600, 2000]

    for (let i = 0; i < demoQueries.length; i++) {
      const query = demoQueries[i]

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: query,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, userMsg])

      await new Promise(r => setTimeout(r, 400))

      setIsTyping(true)

      try {
        const res = await fetch(`${API}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: query }),
        })
        const data = await res.json()

        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: data.reply,
          sources: data.sources,
          suggestedFollowups: data.suggested_followups,
          parsedIntent: data.parsed_intent,
          chart: data.chart,
          evidence: data.evidence,
          riskScore: data.risk_score,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, assistantMsg])
      } catch {
        const errorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Demo error: Backend not reachable.',
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, errorMsg])
      }

      setIsTyping(false)

      if (i < demoQueries.length - 1) {
        await new Promise(r => setTimeout(r, delays[i]))
      }
    }

    setIsDemoRunning(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const showSuggestions = messages.length === 0

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] min-h-[500px]">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[var(--border-subtle)] bg-[var(--bg-surface)]/60 backdrop-blur-xl rounded-t-xl">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold text-white" style={{ background: 'linear-gradient(135deg, var(--accent-amber), #d97706)', boxShadow: '0 0 16px var(--accent-amber-glow)' }}>
            AI
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">AI Assistant</h3>
            <p className="text-[10px] text-[var(--text-muted)]">Groundwater analysis powered by JAL-DRISHTI</p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] bg-[var(--bg-elevated)]/50 hover:bg-[var(--bg-elevated)] border border-[var(--border-subtle)] transition-all"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 bg-[var(--bg-deep)]">
        {showSuggestions && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12 animate-fade-in">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg, var(--accent-amber-glow), var(--accent-teal-glow))', border: '1px solid var(--border-medium)' }}>
              <svg className="w-7 h-7 text-[var(--accent-amber)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-1" style={{ fontFamily: 'var(--font-serif)' }}>JAL-DRISHTI AI Assistant</h3>
            <p className="text-sm text-[var(--text-muted)] max-w-md mb-2">
              Ask questions about groundwater assessment data across Indian states and districts.
            </p>
            <p className="text-[11px] text-[var(--text-faint)] max-w-sm mb-6" style={{ fontFamily: 'var(--font-mono)' }}>
              Data source: CGWB / IN-GRES (2020, 2022, 2024, 2025)
            </p>

            <button
              onClick={runDemo}
              disabled={isDemoRunning}
              className="mb-6 flex items-center gap-2.5 px-6 py-3 rounded-xl text-sm font-semibold text-[var(--bg-deep)] disabled:opacity-50 transition-all duration-300 group"
              style={{
                background: 'linear-gradient(135deg, var(--accent-amber), #d97706)',
                boxShadow: '0 0 24px var(--accent-amber-glow)',
              }}
            >
              {isDemoRunning ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Running Demo...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                  </svg>
                  Run Live Demo
                </>
              )}
            </button>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left px-4 py-3 rounded-xl text-sm text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:border-[var(--accent-amber)]/30 hover:bg-[var(--accent-amber)]/5 transition-all duration-200 group animate-fade-in-up"
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-[var(--text-faint)] group-hover:text-[var(--accent-amber)] transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                    </svg>
                    {q}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} onFollowup={sendMessage} />
        ))}

        {isTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-4 border-t border-[var(--border-subtle)] bg-[var(--bg-surface)]/60 backdrop-blur-xl rounded-b-xl">
        <div className="flex items-center gap-3 bg-[var(--bg-elevated)]/50 border border-[var(--border-subtle)] rounded-xl px-4 py-2 focus-within:border-[var(--accent-amber)]/30 focus-within:ring-1 focus-within:ring-[var(--accent-amber)]/20 transition-all">
          <svg className="w-5 h-5 text-[var(--text-muted)] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about groundwater data..."
            disabled={isTyping}
            className="flex-1 bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isTyping}
            className="w-8 h-8 rounded-lg disabled:opacity-30 text-[var(--bg-deep)] flex items-center justify-center transition-all flex-shrink-0"
            style={{
              background: input.trim() && !isTyping ? 'linear-gradient(135deg, var(--accent-amber), #d97706)' : 'var(--bg-elevated)',
              color: input.trim() && !isTyping ? 'var(--bg-deep)' : 'var(--text-muted)',
            }}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </button>
        </div>
        <p className="text-[10px] text-[var(--text-faint)] mt-2 text-center">
          Official CGWB/IN-GRES data &middot; Assessment years 2020, 2022, 2024, 2025
        </p>
      </div>
    </div>
  )
}

function MessageBubble({ message, onFollowup }: { message: ChatMessage; onFollowup: (text: string) => void }) {
  const [showSources, setShowSources] = useState(false)
  const [showIntent, setShowIntent] = useState(false)
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
      <div className={`max-w-[85%] ${isUser ? 'order-2' : ''}`}>
        {/* Message */}
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'text-[var(--bg-deep)] rounded-br-md'
              : 'text-[var(--text-primary)] border border-[var(--border-subtle)] rounded-bl-md'
          }`}
          style={isUser ? {
            background: 'linear-gradient(135deg, var(--accent-amber), #d97706)',
          } : {
            background: 'var(--bg-surface)',
          }}
        >
          <FormattedText text={message.content} />
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1.5 text-[11px] text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
            >
              <svg className={`w-3 h-3 transition-transform ${showSources ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
              {message.sources.length} source{message.sources.length > 1 ? 's' : ''} cited
            </button>
            {showSources && (
              <div className="mt-2 space-y-2">
                {message.sources.map((src, i) => (
                  <div key={i} className="bg-[var(--bg-elevated)]/50 border border-[var(--border-subtle)] rounded-lg px-3 py-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-medium text-[var(--text-secondary)]">{src.title}</span>
                      <span className="text-[10px] text-[var(--text-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>{src.record_count} records</span>
                    </div>
                    <code className="text-[10px] text-[var(--text-faint)] block mt-0.5" style={{ fontFamily: 'var(--font-mono)' }}>{src.endpoint}</code>
                    {src.data.length > 0 && (
                      <div className="mt-1.5 flex flex-wrap gap-1">
                        {src.data.slice(0, 3).map((d, j) => (
                          <span key={j} className="text-[10px] bg-[var(--bg-surface)] text-[var(--text-muted)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">
                            {String(d.block || d.state || d.year || d.district || JSON.stringify(d).slice(0, 30))}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Parsed Intent */}
        {!isUser && message.parsedIntent && (
          <div className="mt-2">
            <button
              onClick={() => setShowIntent(!showIntent)}
              className="flex items-center gap-1.5 text-[11px] text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
            >
              <svg className={`w-3 h-3 transition-transform ${showIntent ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
              Parsed intent ({message.parsedIntent.intent})
              {message.parsedIntent.state && ` \u00b7 ${message.parsedIntent.state}`}
              {message.parsedIntent.confidence > 0 && ` \u00b7 ${Math.round(message.parsedIntent.confidence * 100)}%`}
            </button>
            {showIntent && (
              <div className="mt-2 bg-[var(--bg-elevated)]/50 border border-[var(--border-subtle)] rounded-lg px-3 py-2">
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-[var(--text-muted)]" style={{ fontFamily: 'var(--font-mono)' }}>
                  <span><strong className="text-[var(--text-secondary)]">intent:</strong> {message.parsedIntent.intent}</span>
                  {message.parsedIntent.state && <span><strong className="text-[var(--text-secondary)]">state:</strong> {message.parsedIntent.state}</span>}
                  {message.parsedIntent.district && <span><strong className="text-[var(--text-secondary)]">district:</strong> {message.parsedIntent.district}</span>}
                  {message.parsedIntent.block && <span><strong className="text-[var(--text-secondary)]">block:</strong> {message.parsedIntent.block}</span>}
                  {message.parsedIntent.year && <span><strong className="text-[var(--text-secondary)]">year:</strong> {message.parsedIntent.year}</span>}
                  {message.parsedIntent.comparison_years.length > 0 && <span><strong className="text-[var(--text-secondary)]">years:</strong> {message.parsedIntent.comparison_years.join(', ')}</span>}
                  {message.parsedIntent.metric && <span><strong className="text-[var(--text-secondary)]">metric:</strong> {message.parsedIntent.metric}</span>}
                  {message.parsedIntent.category && <span><strong className="text-[var(--text-secondary)]">category:</strong> {message.parsedIntent.category}</span>}
                  <span><strong className="text-[var(--text-secondary)]">confidence:</strong> {Math.round(message.parsedIntent.confidence * 100)}%</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Chart */}
        {!isUser && message.chart && (
          <div className="mt-3 glass-card-static px-3 py-3">
            <p className="text-[11px] font-medium text-[var(--text-secondary)] mb-2">{message.chart.title}</p>
            <ChatChart chart={message.chart} />
          </div>
        )}

        {/* Evidence */}
        {!isUser && message.evidence && (
          <div className="mt-2 rounded-lg px-3 py-2" style={{ background: 'var(--accent-sky-glow)', border: '1px solid rgba(14, 165, 233, 0.15)' }}>
            <div className="flex items-center gap-1.5 mb-1.5">
              <svg className="w-3 h-3 text-[var(--accent-sky)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
              <span className="text-[10px] font-medium text-[var(--accent-sky)] uppercase tracking-wider">Evidence</span>
              <span className="badge-official text-[9px] px-1.5 py-0.5 rounded-full font-medium">
                {message.evidence.data_type === 'official' ? 'OFFICIAL CGWB/IN-GRES' : 'DEMO'}
              </span>
              <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium" style={{
                background: message.evidence.confidence === 'High' ? 'var(--safe-glow)' : message.evidence.confidence === 'Medium' ? 'var(--semi-critical-glow)' : 'var(--danger-glow)',
                color: message.evidence.confidence === 'High' ? 'var(--safe)' : message.evidence.confidence === 'Medium' ? 'var(--semi-critical)' : 'var(--danger)',
              }}>
                {message.evidence.confidence}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-[10px] text-[var(--text-muted)]">
              <span>Source: <strong className="text-[var(--text-secondary)]">{message.evidence.source}</strong></span>
              <span>Records: <strong className="text-[var(--text-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{message.evidence.records_used}</strong></span>
              <span>Year: <strong className="text-[var(--text-secondary)]" style={{ fontFamily: 'var(--font-mono)' }}>{message.evidence.assessment_year ?? 'All years'}</strong></span>
              <span>Location: <strong className="text-[var(--text-secondary)]">{message.evidence.location}</strong></span>
            </div>
            {message.evidence.source_url && (
              <div className="mt-1 text-[9px] text-[var(--text-faint)]">
                URL: <a href={message.evidence.source_url} target="_blank" rel="noopener noreferrer" className="text-[var(--accent-sky)] hover:underline">{message.evidence.source_url}</a>
              </div>
            )}
          </div>
        )}

        {/* Risk Score */}
        {!isUser && message.riskScore && (
          <div className="mt-2 glass-card-static px-3 py-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5 text-[var(--accent-amber)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <span className="text-[11px] font-semibold text-[var(--text-secondary)]">Risk Score</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold" style={{
                  fontFamily: 'var(--font-mono)',
                  color: message.riskScore.risk_level === 'Low' ? 'var(--safe)' : message.riskScore.risk_level === 'Medium' ? 'var(--semi-critical)' : message.riskScore.risk_level === 'High' ? 'var(--critical)' : 'var(--danger)',
                }}>
                  {message.riskScore.risk_score}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{
                  background: message.riskScore.risk_level === 'Low' ? 'var(--safe-glow)' : message.riskScore.risk_level === 'Medium' ? 'var(--semi-critical-glow)' : message.riskScore.risk_level === 'High' ? 'var(--critical-glow)' : 'var(--danger-glow)',
                  color: message.riskScore.risk_level === 'Low' ? 'var(--safe)' : message.riskScore.risk_level === 'Medium' ? 'var(--semi-critical)' : message.riskScore.risk_level === 'High' ? 'var(--critical)' : 'var(--danger)',
                }}>
                  {message.riskScore.risk_level}
                </span>
              </div>
            </div>

            <div className="w-full h-1.5 bg-[var(--bg-elevated)] rounded-full mb-2 overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${message.riskScore.risk_score}%`,
                  backgroundColor: message.riskScore.risk_level === 'Low' ? 'var(--safe)' : message.riskScore.risk_level === 'Medium' ? 'var(--semi-critical)' : message.riskScore.risk_level === 'High' ? 'var(--critical)' : 'var(--danger)',
                }}
              />
            </div>

            <div className="space-y-1 mb-2">
              {message.riskScore.factors.map((f, i) => (
                <div key={i} className="flex items-center justify-between text-[10px]">
                  <span className="text-[var(--text-muted)]">{f.factor}</span>
                  <span className="font-medium" style={{
                    fontFamily: 'var(--font-mono)',
                    color: f.contribution > 0 ? 'var(--danger)' : f.contribution < 0 ? 'var(--safe)' : 'var(--text-muted)',
                  }}>
                    {f.contribution > 0 ? '+' : ''}{f.contribution} pts
                  </span>
                </div>
              ))}
            </div>

            <p className="text-[9px] text-[var(--text-faint)] italic leading-tight">
              {message.riskScore.disclaimer}
            </p>
          </div>
        )}

        {/* Follow-up suggestions */}
        {!isUser && message.suggestedFollowups && message.suggestedFollowups.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {message.suggestedFollowups.map((q) => (
              <button
                key={q}
                onClick={() => onFollowup(q)}
                className="text-[11px] px-2.5 py-1 rounded-lg text-[var(--text-muted)] bg-[var(--bg-elevated)]/50 border border-[var(--border-subtle)] hover:border-[var(--accent-amber)]/30 hover:text-[var(--accent-amber)] hover:bg-[var(--accent-amber)]/5 transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-[10px] text-[var(--text-faint)] mt-1 ${isUser ? 'text-right' : ''}`} style={{ fontFamily: 'var(--font-mono)' }}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[var(--accent-amber)] animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 rounded-full bg-[var(--accent-amber)] animate-bounce" style={{ animationDelay: '150ms', opacity: 0.7 }} />
          <div className="w-2 h-2 rounded-full bg-[var(--accent-amber)] animate-bounce" style={{ animationDelay: '300ms', opacity: 0.5 }} />
        </div>
      </div>
    </div>
  )
}

function ChatChart({ chart }: { chart: ChartData }) {
  const { type, data } = chart

  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
          <XAxis dataKey="year" tick={{ fontSize: 11, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} />
          <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-medium)', borderRadius: 8, fontSize: 11, boxShadow: 'var(--shadow-elevated)', color: 'var(--text-primary)' }}
            labelStyle={{ color: 'var(--text-secondary)' }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)' }} />
          <Line type="monotone" dataKey="extraction" stroke="var(--accent-amber)" strokeWidth={2} dot={{ fill: 'var(--accent-amber)', r: 3, stroke: 'var(--bg-surface)', strokeWidth: 2 }} name="Extraction (MCM)" />
          <Line type="monotone" dataKey="recharge" stroke="var(--accent-teal)" strokeWidth={2} dot={{ fill: 'var(--accent-teal)', r: 3, stroke: 'var(--bg-surface)', strokeWidth: 2 }} name="Recharge (MCM)" />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} angle={-15} textAnchor="end" height={50} />
          <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} />
          <Tooltip
            contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-medium)', borderRadius: 8, fontSize: 11, boxShadow: 'var(--shadow-elevated)', color: 'var(--text-primary)' }}
            labelStyle={{ color: 'var(--text-secondary)' }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)' }} />
          <Bar dataKey="extraction" fill="var(--accent-amber)" radius={[4, 4, 0, 0]} name="Extraction (MCM)" />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            nameKey="name"
            label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
            labelLine={{ stroke: 'var(--text-muted)' }}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: 'var(--bg-surface)', border: '1px solid var(--border-medium)', borderRadius: 8, fontSize: 11, boxShadow: 'var(--shadow-elevated)', color: 'var(--text-primary)' }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)' }} />
        </PieChart>
      </ResponsiveContainer>
    )
  }

  return null
}

function FormattedText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i} className="font-semibold" style={{ color: 'var(--text-primary)' }}>{part.slice(2, -2)}</strong>
        }
        return <span key={i}>{part}</span>
      })}
    </>
  )
}
