import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="glass-card w-full max-w-md p-8 text-center">
        <p className="text-xs font-mono uppercase tracking-[0.2em] text-black/50">404</p>
        <h1 className="mt-2 text-2xl font-extrabold">Route not found</h1>
        <p className="mt-2 text-sm text-black/65">The page you requested is outside the current portal map.</p>
        <Link
          to="/auth/login"
          className="mt-5 inline-flex rounded-xl bg-ink px-4 py-2 text-sm font-semibold text-white"
        >
          Back to login
        </Link>
      </div>
    </div>
  );
}
