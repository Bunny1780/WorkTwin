import { useState, type FormEvent } from 'react'
import { Bot, ChevronRight, Send, Sparkles, UserRound } from 'lucide-react'

import { Button } from './components/ui/button'

type Agent = {
  name: string
  role: string
  initials: string
  color: string
}

type Message = {
  id: number
  author: 'user' | 'agent'
  content: string
}

const agents: Agent[] = [
  { name: 'Maya Chen', role: 'Product Manager', initials: 'MC', color: 'bg-violet-500' },
  { name: 'Alex Rivera', role: 'Backend Engineer', initials: 'AR', color: 'bg-sky-500' },
  { name: 'Sam Wilson', role: 'Frontend Engineer', initials: 'SW', color: 'bg-emerald-500' },
  { name: 'Jordan Lee', role: 'QA Engineer', initials: 'JL', color: 'bg-amber-500' },
]

function App() {
  const [selectedAgent, setSelectedAgent] = useState(agents[0])
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      author: 'agent',
      content: 'Hi! I’m Maya, your WorkTwin product partner. What would you like to work through?',
    },
  ])
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const message = draft.trim()
    if (!message || isSending) return

    const userMessage: Message = { id: Date.now(), author: 'user', content: message }
    setMessages((current) => [...current, userMessage])
    setDraft('')
    setError(null)
    setIsSending(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })
      const payload = (await response.json()) as { reply?: string; detail?: string }
      if (!response.ok || !payload.reply) {
        throw new Error(payload.detail ?? 'The WorkTwin service could not answer right now.')
      }
      setMessages((current) => [
        ...current,
        { id: Date.now() + 1, author: 'agent', content: payload.reply! },
      ])
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to send your message.')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <main className="flex min-h-screen bg-slate-950 text-slate-100">
      <aside className="hidden w-80 shrink-0 border-r border-slate-800 bg-slate-900/70 p-5 md:flex md:flex-col">
        <div className="mb-9 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-sky-500 shadow-lg shadow-sky-500/20">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="font-semibold tracking-tight">WorkTwin</h1>
            <p className="text-xs text-slate-400">Organizational memory</p>
          </div>
        </div>

        <div className="mb-3 flex items-center justify-between px-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Your agents</span>
          <Sparkles size={15} className="text-sky-400" />
        </div>
        <nav className="space-y-1" aria-label="WorkTwin agents">
          {agents.map((agent) => {
            const active = agent.name === selectedAgent.name
            return (
              <button
                key={agent.name}
                type="button"
                onClick={() => setSelectedAgent(agent)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition ${
                  active ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                <span className={`grid h-9 w-9 place-items-center rounded-full text-xs font-semibold text-white ${agent.color}`}>
                  {agent.initials}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium">{agent.name}</span>
                  <span className="block truncate text-xs text-slate-500">{agent.role}</span>
                </span>
                {active && <ChevronRight size={16} className="text-sky-400" />}
              </button>
            )
          })}
        </nav>

        <div className="mt-auto rounded-xl border border-slate-800 bg-slate-900 p-4 text-xs leading-5 text-slate-400">
          <p className="font-medium text-slate-300">Human approval required</p>
          <p className="mt-1">Your agents can draft and advise, but critical decisions stay with you.</p>
        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-800 px-5 py-4 sm:px-8">
          <span className={`grid h-10 w-10 place-items-center rounded-full text-sm font-semibold ${selectedAgent.color}`}>
            {selectedAgent.initials}
          </span>
          <div>
            <h2 className="font-semibold">{selectedAgent.name}</h2>
            <p className="text-xs text-emerald-400">● Available · {selectedAgent.role}</p>
          </div>
        </header>

        <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-5 py-8 sm:px-8">
          <div className="flex-1 space-y-6">
            {messages.map((message) => (
              <article key={message.id} className={`flex gap-3 ${message.author === 'user' ? 'justify-end' : ''}`}>
                {message.author === 'agent' && (
                  <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold ${selectedAgent.color}`}>
                    {selectedAgent.initials}
                  </span>
                )}
                <p className={`max-w-[82%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${
                  message.author === 'user' ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-200'
                }`}>
                  {message.content}
                </p>
                {message.author === 'user' && <UserRound size={20} className="mt-2 shrink-0 text-slate-500" />}
              </article>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-8">
            {error && <p role="alert" className="mb-3 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{error}</p>}
            <div className="flex items-end gap-3 rounded-2xl border border-slate-700 bg-slate-900 p-2 shadow-xl shadow-black/10 focus-within:border-sky-500">
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder={`Ask ${selectedAgent.name.split(' ')[0]} about your work…`}
                rows={1}
                className="min-h-11 flex-1 resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500"
                disabled={isSending}
              />
              <Button type="submit" size="icon" aria-label="Send message" disabled={!draft.trim() || isSending}>
                <Send size={17} />
              </Button>
            </div>
            <p className="mt-3 text-center text-xs text-slate-500">WorkTwin responses are suggestions. Verify critical decisions with your team.</p>
          </form>
        </div>
      </section>
    </main>
  )
}

export default App
