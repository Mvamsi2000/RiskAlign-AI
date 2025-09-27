import type { PropsWithChildren, ReactNode } from "react";

interface CardProps {
  title?: ReactNode;
  description?: ReactNode;
}

export function Card({ title, description, children }: PropsWithChildren<CardProps>) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="space-y-2 p-5">
        {title ? <h3 className="text-lg font-semibold text-slate-900">{title}</h3> : null}
        {description ? <p className="text-sm text-slate-500">{description}</p> : null}
        {children}
      </div>
    </div>
  );
}
