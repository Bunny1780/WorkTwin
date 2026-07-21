export type EvidenceCitation = {
  artifact_id: string
  source_type: string
  title: string | null
  occurred_at: string
  source_uri: string
  excerpt: string
}

type EvidencePanelProps = {
  citations: EvidenceCitation[]
}

export function EvidencePanel({ citations }: EvidencePanelProps) {
  return (
    <aside className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <h3 className="text-sm font-semibold">Evidence used</h3>
      <p className="mt-1 text-xs text-slate-500">Inspect the source records grounding the latest answer.</p>
      {citations.length === 0 ? <p className="mt-5 text-sm text-slate-500">Ask a Twin question to view supporting evidence.</p> : (
        <ol className="mt-5 space-y-4">
          {citations.map((citation, index) => (
            <li key={`${citation.artifact_id}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <div className="flex items-start justify-between gap-3"><span className="text-xs font-semibold text-sky-300">[{index + 1}] {citation.source_type.replace(/_/g, ' ')}</span><time className="shrink-0 text-xs text-slate-500">{new Date(citation.occurred_at).toLocaleDateString()}</time></div>
              <a href={citation.source_uri} target="_blank" rel="noreferrer" className="mt-2 block text-sm font-medium text-slate-200 hover:text-sky-300">{citation.title ?? 'Untitled source'}</a>
              <p className="mt-2 text-sm leading-6 text-slate-400">{citation.excerpt}</p>
            </li>
          ))}
        </ol>
      )}
    </aside>
  )
}
