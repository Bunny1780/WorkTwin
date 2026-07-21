import { CheckCircle2, Database, Github, Mail, MessageSquare, ShieldCheck, Webhook, X } from 'lucide-react'

import { Button } from './ui/button'

const sources = [
  { name: 'Slack', detail: 'Messages and decision threads', count: '5 demo artifacts', icon: MessageSquare, color: 'text-violet-300' },
  { name: 'GitHub', detail: 'Pull requests, reviews, commits, and issues', count: '5 demo artifacts', icon: Github, color: 'text-slate-100' },
  { name: 'Email', detail: 'Decisions, handovers, and approvals', count: '4 demo artifacts', icon: Mail, color: 'text-sky-300' },
]

type DataSourceOnboardingProps = { onClose: () => void }

export function DataSourceOnboarding({ onClose }: DataSourceOnboardingProps) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/85 p-5 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="data-sources-title">
      <section className="max-h-full w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl shadow-black/40 sm:p-8">
        <div className="flex items-start justify-between gap-5">
          <div>
            <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-sky-300"><Database size={14} /> Data sources</div>
            <h2 id="data-sources-title" className="text-xl font-semibold text-white">Northstar Labs organizational memory</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">This hackathon workspace uses controlled, repeatable imports that preserve the same identity, provenance, timestamp, and access-scope contract as production connectors.</p>
          </div>
          <Button type="button" variant="ghost" size="icon" aria-label="Close data sources" onClick={onClose}><X size={18} /></Button>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {sources.map(({ name, detail, count, icon: Icon, color }) => (
            <article key={name} className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
              <div className="flex items-center justify-between"><Icon size={20} className={color} /><CheckCircle2 size={17} className="text-emerald-400" /></div>
              <h3 className="mt-4 text-sm font-semibold text-slate-100">{name}</h3>
              <p className="mt-1 min-h-10 text-xs leading-5 text-slate-400">{detail}</p>
              <p className="mt-3 text-xs font-medium text-emerald-300">Demo connected · {count}</p>
            </article>
          ))}
        </div>

        <div className="mt-5 rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm leading-6 text-amber-100">
          <div className="flex items-center gap-2 font-medium"><ShieldCheck size={17} /> Evidence and access are preserved</div>
          <p className="mt-1 text-amber-100/80">Each imported record remains linked to its source identity, canonical URL, timestamp, and company-shared or restricted access scope before it can be retrieved by a Twin.</p>
        </div>

        <div className="mt-5 rounded-xl border border-sky-500/20 bg-sky-500/10 p-4 text-sm leading-6 text-sky-100">
          <div className="flex items-center gap-2 font-medium"><Webhook size={17} /> Production connector path</div>
          <p className="mt-1 text-sky-100/80">In production, an administrator connects Slack, GitHub, and email through OAuth, chooses approved scopes, then keeps this same ingestion contract current through webhooks and scheduled syncs.</p>
        </div>
      </section>
    </div>
  )
}
