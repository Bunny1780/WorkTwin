import { useState, type FormEvent } from 'react'
import { X } from 'lucide-react'

import type { AgentProfile } from './agent-directory'
import { Button } from './ui/button'

export type AgentProfileInput = Omit<AgentProfile, 'id'>

type AgentEditorProps = {
  agent: AgentProfile | null
  onClose: () => void
  onSave: (profile: AgentProfileInput) => Promise<void>
}

type AgentForm = {
  name: string
  role: string
  department: string
  seniority: string
  expertise: string
  communicationStyle: string
  decisionPreferences: string
  riskTolerance: string
  writingStyle: string
  planningProcess: string
  problemSolvingStrategy: string
  documentationHabits: string
}

function formFromAgent(agent: AgentProfile | null): AgentForm {
  return {
    name: agent?.name ?? '',
    role: agent?.role ?? '',
    department: agent?.department ?? '',
    seniority: agent?.seniority ?? '',
    expertise: agent?.expertise.join(', ') ?? '',
    communicationStyle: agent?.personality.communication_style ?? '',
    decisionPreferences: agent?.personality.decision_preferences ?? '',
    riskTolerance: agent?.personality.risk_tolerance ?? '',
    writingStyle: agent?.personality.writing_style ?? '',
    planningProcess: agent?.working_style.planning_process ?? '',
    problemSolvingStrategy: agent?.working_style.problem_solving_strategy ?? '',
    documentationHabits: agent?.working_style.documentation_habits ?? '',
  }
}

function populatedFields(fields: Record<string, string>) {
  return Object.fromEntries(Object.entries(fields).filter(([, value]) => value.trim()))
}

export function AgentEditor({ agent, onClose, onSave }: AgentEditorProps) {
  const [form, setForm] = useState(() => formFromAgent(agent))
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateField(field: keyof AgentForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSaving(true)
    try {
      await onSave({
        name: form.name.trim(),
        role: form.role.trim(),
        department: form.department.trim(),
        seniority: form.seniority.trim(),
        expertise: form.expertise.split(',').map((item) => item.trim()).filter(Boolean),
        personality: populatedFields({
          communication_style: form.communicationStyle,
          decision_preferences: form.decisionPreferences,
          risk_tolerance: form.riskTolerance,
          writing_style: form.writingStyle,
        }),
        working_style: populatedFields({
          planning_process: form.planningProcess,
          problem_solving_strategy: form.problemSolvingStrategy,
          documentation_habits: form.documentationHabits,
        }),
      })
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to save this agent.')
    } finally {
      setIsSaving(false)
    }
  }

  const fields: Array<{ field: keyof AgentForm; label: string; placeholder: string }> = [
    { field: 'name', label: 'Name', placeholder: 'Maya Chen' },
    { field: 'role', label: 'Role', placeholder: 'Product Manager' },
    { field: 'department', label: 'Department', placeholder: 'Product' },
    { field: 'seniority', label: 'Seniority', placeholder: 'Senior' },
    { field: 'expertise', label: 'Expertise', placeholder: 'Roadmaps, discovery, analytics' },
    { field: 'communicationStyle', label: 'Communication style', placeholder: 'Concise and outcome-focused' },
    { field: 'decisionPreferences', label: 'Decision preferences', placeholder: 'Use evidence and clear trade-offs' },
    { field: 'riskTolerance', label: 'Risk tolerance', placeholder: 'Balanced' },
    { field: 'writingStyle', label: 'Writing style', placeholder: 'Structured with clear next steps' },
    { field: 'planningProcess', label: 'Planning process', placeholder: 'Start with outcomes and milestones' },
    { field: 'problemSolvingStrategy', label: 'Problem-solving strategy', placeholder: 'Clarify constraints before proposing options' },
    { field: 'documentationHabits', label: 'Documentation habits', placeholder: 'Record decisions and owners' },
  ]

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/75 p-4 backdrop-blur-sm sm:p-8">
      <section role="dialog" aria-modal="true" aria-labelledby="agent-editor-title" className="mx-auto flex h-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
        <header className="flex items-center justify-between border-b border-slate-800 px-5 py-4 sm:px-7">
          <div>
            <h2 id="agent-editor-title" className="font-semibold">{agent ? 'Edit employee agent' : 'Create employee agent'}</h2>
            <p className="mt-1 text-sm text-slate-400">Define the identity and working style that guide this WorkTwin.</p>
          </div>
          <Button type="button" variant="ghost" size="icon" aria-label="Close agent editor" onClick={onClose} disabled={isSaving}>
            <X size={18} />
          </Button>
        </header>

        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-5 py-6 sm:px-7">
          {error && <p role="alert" className="mb-5 rounded-lg bg-rose-500/10 px-3 py-2 text-sm text-rose-300">{error}</p>}
          <div className="grid gap-4 sm:grid-cols-2">
            {fields.map(({ field, label, placeholder }) => (
              <label key={field} className={field === 'expertise' || field === 'problemSolvingStrategy' || field === 'documentationHabits' ? 'sm:col-span-2' : ''}>
                <span className="mb-1.5 block text-sm font-medium text-slate-300">{label}</span>
                <input
                  value={form[field]}
                  onChange={(event) => updateField(field, event.target.value)}
                  placeholder={placeholder}
                  required={['name', 'role', 'department', 'seniority'].includes(field)}
                  disabled={isSaving}
                  className="h-10 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-sky-500"
                />
              </label>
            ))}
          </div>
          <footer className="mt-7 flex justify-end gap-3 border-t border-slate-800 pt-5">
            <Button type="button" variant="ghost" onClick={onClose} disabled={isSaving}>Cancel</Button>
            <Button type="submit" disabled={isSaving}>{isSaving ? 'Saving…' : agent ? 'Save changes' : 'Create agent'}</Button>
          </footer>
        </form>
      </section>
    </div>
  )
}
