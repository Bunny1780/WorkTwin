import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '../../lib/utils'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl shadow-black/10', className)} {...props} />
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex flex-col gap-1.5 p-5', className)} {...props} />
}

export function CardTitle({ children, className, ...props }: HTMLAttributes<HTMLHeadingElement> & { children: ReactNode }) {
  return <h3 className={cn('text-sm font-semibold text-slate-100', className)} {...props}>{children}</h3>
}

export function CardDescription({ children, className, ...props }: HTMLAttributes<HTMLParagraphElement> & { children: ReactNode }) {
  return <p className={cn('text-xs text-slate-500', className)} {...props}>{children}</p>
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('px-5 pb-5', className)} {...props} />
}
