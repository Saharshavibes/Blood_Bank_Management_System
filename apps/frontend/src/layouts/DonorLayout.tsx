import { PortalLayout } from "@/layouts/PortalLayout";

const navItems = [
  { label: "My Dashboard", to: "/donor" },
  { label: "Appointments", to: "/donor/appointments" },
];

export function DonorLayout() {
  return <PortalLayout portalName="Donor Center" portalLabel="Donor" navItems={navItems} />;
}
