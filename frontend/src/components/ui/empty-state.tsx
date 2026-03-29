import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface EmptyStateAction {
  label: string;
  onClick?: () => void;
  href?: string;
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
}

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: EmptyStateAction;
  secondaryAction?: EmptyStateAction;
  className?: string;
}

function ActionButton({ action }: { action: EmptyStateAction }) {
  const button = (
    <Button variant={action.variant ?? "primary"} onClick={action.onClick}>
      {action.label}
    </Button>
  );

  if (action.href) {
    return <Link href={action.href}>{button}</Link>;
  }

  return button;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-border bg-surface-raised/70 p-8 text-center sm:p-10",
        className
      )}
    >
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-border bg-surface-overlay text-text-muted">
        {icon}
      </div>
      <h3 className="mt-5 text-xl font-bold text-text-primary">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-secondary">{description}</p>
      {(action || secondaryAction) && (
        <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
          {action ? <ActionButton action={action} /> : null}
          {secondaryAction ? <ActionButton action={secondaryAction} /> : null}
        </div>
      )}
    </div>
  );
}
