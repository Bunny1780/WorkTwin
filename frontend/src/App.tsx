import { useEffect, useState } from 'react'

import { TwinDirectory, twinAvatarColor, twinInitials, type TwinDirectoryEntry } from './components/agent-directory'

function App() {
  const [twins, setTwins] = useState<TwinDirectoryEntry[]>([])
  const [selectedTwin, setSelectedTwin] = useState<TwinDirectoryEntry | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadTwins() {
      try {
        const response = await fetch('/api/twins')
        const payload = (await response.json()) as TwinDirectoryEntry[] | { detail?: string }
        if (!response.ok || !Array.isArray(payload)) throw new Error('detail' in payload ? payload.detail : 'Unable to load employee Twins.')
        setTwins(payload)
        setSelectedTwin((current) => current ?? payload[0] ?? null)
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : 'Unable to load employee Twins.')
      } finally {
        setIsLoading(false)
      }
    }
    void loadTwins()
  }, [])

  const former = selectedTwin?.employment_status === 'departed'
  return (
    <main className="flex min-h-screen bg-slate-950 text-slate-100">
      <TwinDirectory twins={twins} selectedTwinId={selectedTwin?.id ?? null} isLoading={isLoading} error={error} onSelect={setSelectedTwin} />
      <section className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-800 px-5 py-4 sm:px-8">
          <span className={`grid h-10 w-10 place-items-center rounded-full text-sm font-semibold ${selectedTwin ? twinAvatarColor(selectedTwin) : 'bg-slate-700'}`}>{selectedTwin ? twinInitials(selectedTwin) : '—'}</span>
          <div>
            <h2 className="font-semibold">{selectedTwin?.display_name ?? 'Select an employee Twin'}</h2>
            <p className={`text-xs ${former ? 'text-amber-400' : 'text-emerald-400'}`}>{selectedTwin ? (former ? 'Historical, evidence-based representation' : `Active employee · ${selectedTwin.role}`) : 'Load the employee directory to begin'}</p>
          </div>
        </header>
        <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col justify-center px-5 py-8 sm:px-8">
          {selectedTwin ? (
            <article className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/10">
              {former && <p className="mb-5 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">This Twin represents historical work evidence from a former employee. It is not a real-time message from {selectedTwin.display_name}.</p>}
              <p className="text-sm text-slate-400">{selectedTwin.role} · {selectedTwin.department}</p>
              <h3 className="mt-6 text-sm font-semibold uppercase tracking-wider text-slate-500">Evidence-derived expertise</h3>
              <div className="mt-3 flex flex-wrap gap-2">{selectedTwin.expertise.length ? selectedTwin.expertise.map((item) => <span key={item} className="rounded-full bg-sky-500/10 px-3 py-1 text-sm text-sky-200">{item}</span>) : <span className="text-sm text-slate-500">No derived expertise yet.</span>}</div>
              <dl className="mt-7 grid gap-4 border-t border-slate-800 pt-5 sm:grid-cols-2">
                <div><dt className="text-xs uppercase tracking-wider text-slate-500">Source artifacts</dt><dd className="mt-1 text-2xl font-semibold">{selectedTwin.source_artifact_count}</dd></div>
                <div><dt className="text-xs uppercase tracking-wider text-slate-500">Last evidence</dt><dd className="mt-1 text-sm text-slate-300">{selectedTwin.source_last_occurred_at ? new Date(selectedTwin.source_last_occurred_at).toLocaleDateString() : 'Not available'}</dd></div>
              </dl>
              <p className="mt-8 rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-400">Evidence-backed Twin Q&A and source citations will be available in the next step.</p>
            </article>
          ) : <p className="text-center text-sm text-slate-500">No employee Twins are available.</p>}
        </div>
      </section>
    </main>
  )
}

export default App
