import * as React from "react";
import { cn } from "../utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, className, ...rest },
  ref,
) {
  return (
    <label className="block">
      {label && (
        <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-ink-soft">
          {label}
        </span>
      )}
      <input
        ref={ref}
        className={cn(
          "w-full rounded-md border border-cream bg-white px-3 py-2 text-sm",
          "focus:border-gold focus:outline-none focus:ring-1 focus:ring-gold/40",
          error && "border-status-danger",
          className,
        )}
        {...rest}
      />
      {error && <span className="mt-1 block text-xs text-status-danger">{error}</span>}
    </label>
  );
});
