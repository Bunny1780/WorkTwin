import { useEffect, useState, type FormEvent } from 'react'
import { Send, UserRound } from 'lucide-react'

import { AgentDirectory, agentAvatarColor, agentInitials, type AgentProfile } from './components/agent-directory'
import { Button } from './components/ui/button'

type Message = {
  id: number
  author: 'user' | 'agent'
  content: string
}

function App() {
  const [agents, setAgents] = useState<AgentProfile[]>([])
  const [selectedAgent, setSelectedAgent] = useState<AgentProfile | null>(null)
  const [isLoadingAgents, setIsLoadingAgents] = useState(true)
  const [agentsError, setAgentsError] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadAgents() {
      try {
        const response = await fetch('/api/agents')
        const payload = (await response.json()) as AgentProfile[] | { detail?: string }
        if (!response.ok || !Array.isArray(payload)) {
          throw new Error('detail' in payload ? payload.detail : 'Unable to load employee agents.')
        }
        setAgents(payload)
        setSelectedAgent((current) => current ?? payload[0] ?? null)
      } catch (requestError) {
        setAgentsError(requestError instanceof Error ? requestError.message : 'Unable to load employee agents.')
      } finally {
        setIsLoadingAgents(false)
      }
    }

    void loadAgents()
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const message = draft.trim()
    if (!message || isSending || !selectedAgent) return

    const userMessage: Message = { id: Date.now(), author: 'user', content: message }
    setMessages((current) => [...current, userMessage])
    setDraft('')
    setError(null)
    setIsSending(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, agent_id: selectedAgent.id }),
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
      <AgentDirectory
        agents={agents}
        selectedAgentId={selectedAgent?.id ?? null}
        isLoading={isLoadingAgents}
        error={agentsError}
        onSelect={setSelectedAgent}
      />

      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-800 px-5 py-4 sm:px-8">
          <span className={`grid h-10 w-10 place-items-center rounded-full text-sm font-semibold ${selectedAgent ? agentAvatarColor(selectedAgent) : 'bg-slate-700'}`}>
            {selectedAgent ? agentInitials(selectedAgent) : '—'}
          </span>
          <div>
            <h2 className="font-semibold">{selectedAgent?.name ?? 'Select an agent'}</h2>
            <p className="text-xs text-emerald-400">{selectedAgent ? `● Available · ${selectedAgent.role}` : 'Load or create an employee agent to begin'}</p>
          </div>
        </header>

        <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-5 py-8 sm:px-8">
          <div className="flex-1 space-y-6">
            {messages.map((message) => (
              <article key={message.id} className={`flex gap-3 ${message.author === 'user' ? 'justify-end' : ''}`}>
                {message.author === 'agent' && (
                  <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold ${selectedAgent ? agentAvatarColor(selectedAgent) : 'bg-slate-700'}`}>
                    {selectedAgent ? agentInitials(selectedAgent) : '—'}
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
                placeholder={selectedAgent ? `Ask ${selectedAgent.name.split(' ')[0]} about your work…` : 'Select an employee agent to begin…'}
                rows={1}
                className="min-h-11 flex-1 resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-500"
                disabled={isSending || !selectedAgent}
              />
              <Button type="submit" size="icon" aria-label="Send message" disabled={!draft.trim() || isSending || !selectedAgent}>
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
