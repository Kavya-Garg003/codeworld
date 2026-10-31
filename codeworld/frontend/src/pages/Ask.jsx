import React, { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import { Badge, Spinner, useFetch, useRepo } from '../components/common.jsx'
import Markdown from '../components/Markdown.jsx'

const MODES = [['graph', 'Graph-RAG (BM25 + vectors + call graph)'], ['hybrid', 'Hybrid (BM25 + vectors)'], ['vector', 'Vectors only'], ['bm25', 'BM25 only']]

export default function Ask() {
  const { id, repo } = useRepo()
  const nav = useNavigate()
  const [sp] = useSearchParams()
  const [msgs, setMsgs] = useState([])
  const [text, setText] = useState(sp.get('q') || '')
  const [mode, setMode] = useState('graph')
  const [agent, setAgent] = useState(true)
  const [busy, setBusy] = useState(false)
  const end = useRef()
  const { data: health } = useFetch(() => api.get('/api/health'), [])
  const { data: ov } = useFetch(() => api.get(`/api/repos/${id}/onboarding`), [id])
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs, busy])
  const send = async (qtext) => {
    const question = (qtext ?? text).trim()
    if (!question || busy) return
    const history = msgs.slice(-6).map((m) => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }))
    setMsgs((m) => [...m, { role: 'user', text: question }]); setText(''); setBusy(true)
    try { const r = await api.post(`/api/repos/${id}/ask`, { question, mode, agent, history }); setMsgs((m) => [...m, { role: 'bot', text: r.answer, r }]) }
    catch (e) { setMsgs((m) => [...m, { role: 'bot', text: '**Error:** ' + e.message }]) }
    setBusy(false)
  }
  const first = ov?.key_modules?.[0]?.path
  const ep = ov?.entry_points?.find((e) => e.kind === 'endpoint')
  const sug = ['What does this project do and how is it organised?', ep && `How does ${ep.name} work end to end?`, first && `What breaks if I change ${first}?`, 'Is there any security risk in this codebase?', 'Which code has no tests?'].filter(Boolean)
  return (
    <div className="chat">
      <div className="topbar"><span className="name">Ask {repo.name}</span><span className="grow" />
        <Badge kind={health?.llm?.provider === 'none' ? 'medium' : 'ok'}>{health?.llm?.provider === 'none' ? 'offline mode · no LLM' : `${health?.llm?.provider} · ${health?.llm?.model}`}</Badge></div>
      <div className="msgs">
        {msgs.length === 0 && <div className="card" style={{ maxWidth: 760 }}><h2>Ask anything about this codebase</h2>
          <p className="muted">Answers are grounded in retrieved code and every citation is verified against what was actually retrieved. Try:</p>
          <div className="row">{sug.map((s) => <span key={s} className="badge chip" onClick={() => send(s)}>{s}</span>)}</div></div>}
        {msgs.map((m, i) => m.role === 'user' ? <div key={i} className="msg user">{m.text}</div> : (
          <div key={i} className="msg bot">
            <Markdown text={m.text} repoId={id} />
            {m.r && <div style={{ marginTop: 10 }}>
              <div className="row small muted">
                <Badge>{m.r.intent}</Badge><span>{m.r.provider}</span><span>{m.r.latency_ms} ms</span>
                {m.r.citation_precision != null && <Badge kind={m.r.citation_precision === 1 ? 'ok' : 'medium'}>{Math.round(m.r.citation_precision * 100)}% citations verified</Badge>}
                {m.r.highlight?.length > 0 && <button className="ghost" onClick={() => nav(`/r/${id}/map?hl=${encodeURIComponent(m.r.highlight.join('|'))}`)}>⌖ show on map</button>}
              </div>
              {m.r.notes?.map((n, k) => <div key={k} className="small" style={{ color: 'var(--warn)' }}>{n}</div>)}
              <details><summary>How this answer was built ({m.r.trace.length} step{m.r.trace.length === 1 ? '' : 's'})</summary>
                {m.r.trace.map((t, k) => <div key={k} className="small mono" style={{ padding: '3px 0' }}>{t.tool}({JSON.stringify(t.args).slice(0, 90)}) → {t.summary}</div>)}</details>
            </div>}
          </div>))}
        {busy && <div className="msg bot"><Spinner label="searching the graph…" /></div>}
        <div ref={end} />
      </div>
      <div className="composer">
        <div className="row" style={{ marginBottom: 8 }}>
          <select style={{ width: 'auto' }} value={mode} onChange={(e) => setMode(e.target.value)}>{MODES.map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select>
          <label className="small"><input type="checkbox" checked={agent} onChange={(e) => setAgent(e.target.checked)} /> agent tools (callers, impact, tests…)</label>
        </div>
        <div className="row"><input type="text" value={text} placeholder="e.g. who calls verify_password? · how does login work? · what breaks if I change X?"
          onChange={(e) => setText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} /><button className="primary" disabled={busy || !text.trim()} onClick={() => send()}>Ask</button></div>
      </div>
    </div>
  )
}
