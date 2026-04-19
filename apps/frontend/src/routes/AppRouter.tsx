import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "@/context/AuthContext";
import { AdminLayout } from "@/layouts/AdminLayout";
import { DonorLayout } from "@/layouts/DonorLayout";
import { HospitalLayout } from "@/layouts/HospitalLayout";
import { roleHomePath } from "@/lib/roleHome";
import { AdminDashboardPage } from "@/pages/admin/AdminDashboardPage";
import { AdminHospitalsPage } from "@/pages/admin/AdminHospitalsPage";
import { AdminInventoryPage } from "@/pages/admin/AdminInventoryPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterDonorPage } from "@/pages/auth/RegisterDonorPage";
import { RegisterHospitalPage } from "@/pages/auth/RegisterHospitalPage";
import { DonorAppointmentsPage } from "@/pages/donor/DonorAppointmentsPage";
import { DonorDashboardPage } from "@/pages/donor/DonorDashboardPage";
import { HospitalDashboardPage } from "@/pages/hospital/HospitalDashboardPage";
import { HospitalUrgentPage } from "@/pages/hospital/HospitalUrgentPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

function HomeRedirect() {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated || !user) {
    return <Navigate to="/auth/login" replace />;
  }
  return <Navigate to={roleHomePath[user.role]} replace />;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />

      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register-donor" element={<RegisterDonorPage />} />
      <Route path="/auth/register-hospital" element={<RegisterHospitalPage />} />

      <Route element={<ProtectedRoute roles={["admin"]} />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="inventory" element={<AdminInventoryPage />} />
          <Route path="hospitals" element={<AdminHospitalsPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={["donor"]} />}>
        <Route path="/donor" element={<DonorLayout />}>
          <Route index element={<DonorDashboardPage />} />
          <Route path="appointments" element={<DonorAppointmentsPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={["hospital"]} />}>
        <Route path="/hospital" element={<HospitalLayout />}>
          <Route index element={<HospitalDashboardPage />} />
          <Route path="urgent" element={<HospitalUrgentPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
