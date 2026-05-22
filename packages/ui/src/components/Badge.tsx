import * as React from "react";
import { cn } from "../utils";

type Tone = "neutral" | "active" | "warn" | "danger" | "info" | "archived" | "gold";

const toneClasses: Record<Tone, string> = {
  neutral: "bg-cream text-ink",
  active: "bg-status-activeBg text-status-active",
  warn: "bg-status-warnBg text-status-warn",
  danger: "bg-status-dangerBg text-status-danger",
  info: "bg-status-infoBg text-status-info",
  archived: "bg-status-archived text-status-archivedFg",
  gold: "bg-gold-soft text-gold-dark",
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function Badge({ tone = "neutral", className, children, ...rest }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wide",
        toneClasses[tone],
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  );
}
