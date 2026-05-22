import * as React from "react";
import { cn } from "../utils";

type Variant = "primary" | "ghost" | "danger" | "subtle";
type Size = "sm" | "md" | "lg";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-gold text-navy hover:bg-gold-dark hover:text-white border border-gold disabled:opacity-50",
  ghost:
    "bg-transparent text-navy border border-gold/60 hover:bg-gold/10 disabled:opacity-50",
  danger:
    "bg-status-danger text-white border border-status-danger hover:opacity-90",
  subtle:
    "bg-cream text-navy border border-cream hover:bg-gold-soft",
};

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "primary", size = "md", loading, disabled, children, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-colors",
        variantClasses[variant],
        sizeClasses[size],
        loading && "cursor-wait",
        className,
      )}
      {...rest}
    >
      {loading ? "..." : children}
    </button>
  );
});
