import { useEffect, useState, type FormEvent } from 'react'
import { Send, UserRound } from 'lucide-react'

import { TwinDirectory, twinAvatarColor, twinInitials, type TwinDirectoryEntry } from './components/agent-directory'
import { EvidencePanel, type EvidenceCitation } from './components/evidence-panel'
import { Button } from './components/ui/button'

type Message = { id: number; author: 'user' | 'twin'; content: string; historical: boolean }

function App() {
  const [twins, setTwins] = useState<TwinDirectoryEntry[]>([])
  const [selectedTwin, setSelectedTwin] = useState<TwinDirectoryEntry | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [directoryError, setDirectoryError] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [citations, setCitations] = useState<EvidenceCitation[]>([])
  const [includeCompanyShared, setIncludeCompanyShared] = useState(true)
  const [isAsking, setIsAsking] = useState(false)
  const [queryError, setQueryError] = useState<string | null>(null)

  useEffect(() => {
    async function loadTwins() {
      try {
        const response = await fetch('/api/twins')
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
      const response = await fetch(`/api/twins/${selectedTwin.id}/query`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmedQuestion, include_company_shared: includeCompanyShared }),
      })
      const payload = (await response.json()) as { reply?: string; citations?: EvidenceCitation[]; representation?: string; detail?: string }
      if (!response.ok || !payload.reply || !payload.citations || !payload.representation) throw new Error(payload.detail ?? 'The Twin could not answer right now.')
      setMessages((current) => [...current, { id: Date.now() + 1, author: 'twin', content: payload.reply!, historical: payload.representation === 'historical_evidence_based' }])
      setCitations(payload.citations)
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

  const former = selectedTwin?.employment_status === 'departed'
  return (
    <main className="flex min-h-screen bg-slate-950 text-slate-100">
      <TwinDirectory twins={twins} selectedTwinId={selectedTwin?.id ?? null} isLoading={isLoading} error={directoryError} onSelect={selectTwin} />
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-800 px-5 py-4 sm:px-8">
          <span className={`grid h-10 w-10 place-items-center rounded-full text-sm font-semibold ${selectedTwin ? twinAvatarColor(selectedTwin) : 'bg-slate-700'}`}>{selectedTwin ? twinInitials(selectedTwin) : '—'}</span>
          <div><h2 className="font-semibold">{selectedTwin?.display_name ?? 'Select an employee Twin'}</h2><p className={`text-xs ${former ? 'text-amber-400' : 'text-emerald-400'}`}>{selectedTwin ? (former ? 'Historical, evidence-based representation' : `Active employee · ${selectedTwin.role}`) : 'Load the employee directory to begin'}</p></div>
        </header>
        <div className="mx-auto grid w-full max-w-6xl flex-1 gap-6 px-5 py-8 lg:grid-cols-[minmax(0,1fr)_21rem] sm:px-8">
          <div className="flex min-w-0 flex-col">
            {selectedTwin ? <>
              {former && <p className="mb-5 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">This Twin represents historical work evidence from a former employee. It is not a real-time message from {selectedTwin.display_name}.</p>}
              <div className="flex-1 space-y-5">{messages.length === 0 && <p className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-sm text-slate-400">Ask about decisions, implementation context, or working patterns. Answers are grounded only in permitted organizational evidence.</p>}
                {messages.map((message) => <article key={message.id} className={`flex gap-3 ${message.author === 'user' ? 'justify-end' : ''}`}>
                  {message.author === 'twin' && <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold ${twinAvatarColor(selectedTwin)}`}>{twinInitials(selectedTwin)}</span>}
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${message.author === 'user' ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-200'}`}>
                    {message.historical && <p className="mb-2 text-xs font-semibold text-amber-300">Historical evidence-based representation</p>}{message.content}
                  </div>{message.author === 'user' && <UserRound size={20} className="mt-2 shrink-0 text-slate-500" />}
                </article>)}
              </div>
              <form onSubmit={askTwin} className="mt-7">
                {queryError && <p role="alert" className="mb-3 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{queryError}</p>}
                <label className="mb-3 flex items-center gap-2 text-xs text-slate-400"><input type="checkbox" checked={includeCompanyShared} onChange={(event) => setIncludeCompanyShared(event.target.checked)} className="accent-sky-500" /> Include company-shared organizational memory</label>
                <div className="flex items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-2 focus-within:border-sky-500"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={`Ask ${selectedTwin.display_name.split(' ')[0]} about the available evidence…`} rows={1} disabled={isAsking} className="min-h-11 flex-1 resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500" /><Button type="submit" size="icon" aria-label="Ask Twin" disabled={!question.trim() || isAsking}><Send size={17} /></Button></div>
              </form>
            </> : <p className="text-center text-sm text-slate-500">No employee Twins are available.</p>}
          </div>
          <EvidencePanel citations={citations} />
        </div>
      </section>
    </main>
  )
}

export default App
