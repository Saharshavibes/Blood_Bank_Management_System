import { Button } from "@/components/ui/Button";

type DegradedStateBannerProps = {
  title: string;
  message: string;
  onRetry?: () => void;
  isRetrying?: boolean;
};

export function DegradedStateBanner({
  title,
  message,
  onRetry,
  isRetrying = false,
}: DegradedStateBannerProps) {
  return (
    <div className="rounded-xl border border-amber-300/70 bg-amber-50/85 p-4 text-amber-900">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-amber-700">Degraded Mode</p>
          <p className="mt-1 text-sm font-semibold">{title}</p>
          <p className="mt-1 text-sm text-amber-800/90">{message}</p>
        </div>
        {onRetry ? (
          <Button variant="outline" onClick={onRetry} disabled={isRetrying} className="border-amber-400 bg-amber-100/80">
            {isRetrying ? "Retrying..." : "Retry live data"}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
