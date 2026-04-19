import { NavLink, Outlet, useLocation } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { useAuth } from "@/context/AuthContext";

type NavItem = {
  label: string;
  to: string;
};

type PortalLayoutProps = {
  portalName: string;
  portalLabel: string;
  navItems: NavItem[];
};

export function PortalLayout({ portalName, portalLabel, navItems }: PortalLayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (target: string) => location.pathname === target || location.pathname.startsWith(`${target}/`);

  return (
    <div className="min-h-screen bg-hero-mesh">
      <header className="border-b border-black/10 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-3 px-4 py-4 lg:px-6">
          <div>
            <p className="text-xs font-mono uppercase tracking-[0.2em] text-black/55">Blood Bank Management</p>
            <h1 className="text-lg font-bold text-black/90">{portalName}</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="pill border border-calm/25 bg-calm/10 text-calm">{portalLabel}</span>
            <span className="hidden text-sm text-black/65 sm:block">{user?.email}</span>
            <Button variant="outline" onClick={logout}>Sign out</Button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-5 px-4 py-6 lg:grid-cols-[250px_1fr] lg:px-6">
        <aside className="glass-card h-fit p-3">
          <nav className="grid gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={`rounded-xl px-3 py-2 text-sm font-medium transition ${
                  isActive(item.to)
                    ? "bg-ink text-white"
                    : "bg-transparent text-black/75 hover:bg-black/5 hover:text-black"
                }`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="fade-in-up space-y-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
