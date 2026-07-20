import { Bot, ChevronRight, Plus, Sparkles } from 'lucide-react'

import { Button } from './ui/button'

export type AgentProfile = {
  id: string
  name: string
  role: string
  department: string
  seniority: string
  expertise: string[]
  personality: Record<string, string>
  working_style: Record<string, string>
}

type AgentDirectoryProps = {
  agents: AgentProfile[]
  selectedAgentId: string | null
  isLoading: boolean
  error: string | null
  onSelect: (agent: AgentProfile) => void
  onCreate: () => void
}

const avatarColors = ['bg-violet-500', 'bg-sky-500', 'bg-emerald-500', 'bg-amber-500']

export function agentInitials(agent: AgentProfile) {
  return agent.name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((name) => name[0])
    .join('')
    .toUpperCase()
}

export function agentAvatarColor(agent: AgentProfile) {
  const value = [...agent.id].reduce((total, character) => total + character.charCodeAt(0), 0)
  return avatarColors[value % avatarColors.length]
}

export function AgentDirectory({ agents, selectedAgentId, isLoading, error, onSelect, onCreate }: AgentDirectoryProps) {
  return (
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
        {isLoading && <p className="px-3 py-2 text-sm text-slate-500">Loading agents…</p>}
        {error && <p role="alert" className="rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{error}</p>}
        {!isLoading && !error && agents.length === 0 && (
          <p className="px-3 py-2 text-sm text-slate-500">No employee agents yet.</p>
        )}
        {agents.map((agent) => {
          const active = agent.id === selectedAgentId
          return (
            <button
              key={agent.id}
              type="button"
              onClick={() => onSelect(agent)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition ${
                active ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <span className={`grid h-9 w-9 place-items-center rounded-full text-xs font-semibold text-white ${agentAvatarColor(agent)}`}>
                {agentInitials(agent)}
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
      <Button type="button" variant="ghost" className="mt-4 justify-start gap-2" onClick={onCreate}>
        <Plus size={16} /> Create agent
      </Button>

      <div className="mt-auto rounded-xl border border-slate-800 bg-slate-900 p-4 text-xs leading-5 text-slate-400">
        <p className="font-medium text-slate-300">Human approval required</p>
        <p className="mt-1">Your agents can draft and advise, but critical decisions stay with you.</p>
      </div>
    </aside>
  )
}
