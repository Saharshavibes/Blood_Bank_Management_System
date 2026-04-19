import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/context/AuthContext";
import type { UserRole } from "@/types/auth";

const roleHome: Record<UserRole, string> = {
  donor: "/donor",
  admin: "/admin",
  hospital: "/hospital",
};

type ProtectedRouteProps = {
  roles?: UserRole[];
};

export function ProtectedRoute({ roles }: ProtectedRouteProps) {
  const { isAuthenticated, isBootstrapping, user } = useAuth();

  if (isBootstrapping) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="glass-card px-8 py-6 text-sm font-semibold">Warming up secure session...</div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/auth/login" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to={roleHome[user.role]} replace />;
  }

  return <Outlet />;
}
