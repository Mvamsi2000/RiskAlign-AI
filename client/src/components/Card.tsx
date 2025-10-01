import type { PropsWithChildren, ReactNode } from "react";

interface CardProps {
  title?: ReactNode;
  description?: ReactNode;
}

export function Card({ title, description, children }: PropsWithChildren<CardProps>) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/70">
      <div className="space-y-2 p-5">
        {title ? <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3> : null}
        {description ? <p className="text-sm text-slate-500 dark:text-slate-300">{description}</p> : null}
        {children}
      </div>
    </div>
  );
}
