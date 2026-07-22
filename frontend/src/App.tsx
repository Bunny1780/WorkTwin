import { useEffect, useState, type FormEvent, type KeyboardEvent } from 'react'
import { Database, Send, UserRound } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

import { TwinDirectory, twinAvatarColor, twinInitials, type TwinDirectoryEntry } from './components/agent-directory'
import { EvidencePanel, type EvidenceCitation } from './components/evidence-panel'
import { DataSourceOnboarding } from './components/data-source-onboarding'
import { Button } from './components/ui/button'

type Message = { id: number; author: 'user' | 'twin'; content: string; historical: boolean }
type ResponseMode = 'advice' | 'implementation_plan' | 'code_draft'
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? ''

function App() {
  const [twins, setTwins] = useState<TwinDirectoryEntry[]>([])
  const [selectedTwin, setSelectedTwin] = useState<TwinDirectoryEntry | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [directoryError, setDirectoryError] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [citations, setCitations] = useState<EvidenceCitation[]>([])
  const [includeCompanyShared, setIncludeCompanyShared] = useState(true)
  const [responseMode, setResponseMode] = useState<ResponseMode>('advice')
  const [policy, setPolicy] = useState('Twins may draft and advise, but deployment, pull-request approval, production changes, and access to restricted artifacts require human approval.')
  const [isAsking, setIsAsking] = useState(false)
  const [queryError, setQueryError] = useState<string | null>(null)
  const [isDataSourcesOpen, setIsDataSourcesOpen] = useState(false)

  useEffect(() => {
    async function loadTwins() {
      try {
        const response = await fetch(`${apiBaseUrl}/api/twins`)
        const payload = (await response.json()) as TwinDirectoryEntry[] | { detail?: string }
        if (!response.ok || !Array.isArray(payload)) throw new Error('detail' in payload ? payload.detail : 'Unable to load employee Twins.')
        setTwins(payload)
        setSelectedTwin((current) => current ?? payload[0] ?? null)
      } catch (requestError) {
        setDirectoryError(requestError instanceof Error ? requestError.message : 'Unable to load employee Twins.')
      } finally {
        setIsLoading(false)
      }
    }
    void loadTwins()
  }, [])

  async function askTwin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmedQuestion = question.trim()
    if (!selectedTwin || !trimmedQuestion || isAsking) return
    setMessages((current) => [...current, { id: Date.now(), author: 'user', content: trimmedQuestion, historical: false }])
    setQuestion('')
    setQueryError(null)
    setIsAsking(true)
    try {
      const response = await fetch(`${apiBaseUrl}/api/twins/${selectedTwin.id}/query`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmedQuestion, include_company_shared: includeCompanyShared, response_mode: responseMode }),
      })
      const payload = (await response.json()) as { reply?: string; citations?: EvidenceCitation[]; representation?: string; response_mode?: ResponseMode; policy?: string; detail?: string }
      if (!response.ok || !payload.reply || !payload.citations || !payload.representation) throw new Error(payload.detail ?? 'The Twin could not answer right now.')
      setMessages((current) => [...current, { id: Date.now() + 1, author: 'twin', content: payload.reply!, historical: payload.representation === 'historical_evidence_based' }])
      setCitations(payload.citations)
      if (payload.policy) setPolicy(payload.policy)
    } catch (requestError) {
      setQueryError(requestError instanceof Error ? requestError.message : 'Unable to query this Twin.')
    } finally {
      setIsAsking(false)
    }
  }

  function selectTwin(twin: TwinDirectoryEntry) {
    setSelectedTwin(twin)
    setMessages([])
    setCitations([])
    setQueryError(null)
  }

  function loadCitationDemo() {
    setQuestion('Why must every Twin answer include citations? Give me an implementation plan for enforcing that contract.')
    setResponseMode('implementation_plan')
  }

  function submitOnEnter(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  const former = selectedTwin?.employment_status === 'departed'
  return (
    <main className="flex h-dvh overflow-hidden bg-slate-950 text-slate-100">
      <TwinDirectory twins={twins} selectedTwinId={selectedTwin?.id ?? null} isLoading={isLoading} error={directoryError} onSelect={selectTwin} />
      <section className="flex h-dvh min-h-0 min-w-0 flex-1 flex-col">
        <header className="shrink-0 flex items-center justify-between gap-3 border-b border-slate-800 px-5 py-4 sm:px-8">
          <div className="flex min-w-0 items-center gap-3"><span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full text-sm font-semibold ${selectedTwin ? twinAvatarColor(selectedTwin) : 'bg-slate-700'}`}>{selectedTwin ? twinInitials(selectedTwin) : '—'}</span>
            <div className="min-w-0"><h2 className="truncate font-semibold">{selectedTwin?.display_name ?? 'Select an employee Twin'}</h2><p className={`truncate text-xs ${former ? 'text-amber-400' : 'text-emerald-400'}`}>{selectedTwin ? (former ? 'Historical, evidence-based representation' : `Active employee · ${selectedTwin.role}`) : 'Load the employee directory to begin'}</p></div></div>
          <Button type="button" variant="ghost" className="shrink-0 gap-2 border border-slate-700 px-3 text-xs" onClick={() => setIsDataSourcesOpen(true)}><Database size={15} /> Data sources</Button>
        </header>
        <div className="mx-auto grid h-full min-h-0 w-full max-w-6xl flex-1 gap-6 overflow-hidden px-5 py-5 lg:grid-cols-[minmax(0,1fr)_21rem] sm:px-8">
          <div className="flex h-full min-h-0 min-w-0 flex-col">
            {selectedTwin ? <div className="flex min-h-0 flex-1 flex-col">
              {former && <p className="mb-5 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">This Twin represents historical work evidence from a former employee. It is not a real-time message from {selectedTwin.display_name}.</p>}
              {former && messages.length === 0 && <div className="mb-5 rounded-lg border border-sky-500/20 bg-sky-500/10 p-4"><p className="text-sm font-medium text-sky-100">Hackathon demo prompt</p><p className="mt-1 text-sm text-slate-300">Show how a departed engineer's historical rationale becomes a cited implementation plan.</p><Button type="button" variant="ghost" className="mt-3 h-8 border border-sky-400/30 px-3 text-xs" onClick={loadCitationDemo}>Load citation-contract story</Button></div>}
              <div className="min-h-0 flex-1 space-y-5 overflow-y-auto pr-2">{messages.length === 0 && <p className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-sm text-slate-400">Ask about decisions, implementation context, or working patterns. Answers are grounded only in permitted organizational evidence.</p>}
                {messages.map((message) => <article key={message.id} className={`flex gap-3 ${message.author === 'user' ? 'justify-end' : ''}`}>
                  {message.author === 'twin' && <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold ${twinAvatarColor(selectedTwin)}`}>{twinInitials(selectedTwin)}</span>}
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 [&_a]:underline [&_code]:rounded [&_code]:bg-black/20 [&_code]:px-1 [&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_p:not(:last-child)]:mb-3 [&_pre]:my-3 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-black/20 [&_pre]:p-3 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5 ${message.author === 'user' ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-200'}`}>
                    {message.historical && <p className="mb-2 text-xs font-semibold text-amber-300">Historical evidence-based representation</p>}<ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>{message.author === 'user' && <UserRound size={20} className="mt-2 shrink-0 text-slate-500" />}
                </article>)}
                {isAsking && <article className="flex gap-3" role="status" aria-live="polite" aria-label={`${selectedTwin.display_name} is typing`}>
                  <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold ${twinAvatarColor(selectedTwin)}`}>{twinInitials(selectedTwin)}</span>
                  <div className="flex items-center gap-2 rounded-2xl bg-slate-800 px-4 py-3 text-sm text-slate-300">
                    <span>{selectedTwin.display_name.split(' ')[0]} is reviewing the evidence</span>
                    <span className="flex gap-1" aria-hidden="true"><span className="typing-dot" /><span className="typing-dot [animation-delay:150ms]" /><span className="typing-dot [animation-delay:300ms]" /></span>
                  </div>
                </article>}
              </div>
              <form onSubmit={askTwin} className="mt-4 shrink-0 border-t border-slate-800 bg-slate-950 pt-4">
                {queryError && <p role="alert" className="mb-3 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{queryError}</p>}
                <div className="mb-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-400"><label className="flex items-center gap-2"><input type="checkbox" checked={includeCompanyShared} onChange={(event) => setIncludeCompanyShared(event.target.checked)} className="accent-sky-500" /> Include company-shared organizational memory</label><label className="flex items-center gap-2">Response mode <select value={responseMode} onChange={(event) => setResponseMode(event.target.value as ResponseMode)} className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-slate-200"><option value="advice">Advice</option><option value="implementation_plan">Implementation plan</option><option value="code_draft">Code draft</option></select></label></div>
                <div className="flex items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-2 focus-within:border-sky-500"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={submitOnEnter} placeholder={`Ask ${selectedTwin.display_name.split(' ')[0]} about the available evidence…`} rows={1} disabled={isAsking} className="min-h-11 max-h-36 flex-1 resize-y bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500" /><Button type="submit" size="icon" aria-label="Ask Twin" disabled={!question.trim() || isAsking}><Send size={17} /></Button></div>
                <p className="mt-3 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-xs leading-5 text-amber-100">Human approval required: {policy}</p>
              </form>
            </div> : <p className="text-center text-sm text-slate-500">No employee Twins are available.</p>}
          </div>
          <div className="min-h-0 overflow-y-auto pr-2"><EvidencePanel citations={citations} /></div>
        </div>
      </section>
      {isDataSourcesOpen && <DataSourceOnboarding onClose={() => setIsDataSourcesOpen(false)} />}
    </main>
  )
}

export default App
