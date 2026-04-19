import { PortalLayout } from "@/layouts/PortalLayout";

const navItems = [
  { label: "Overview", to: "/admin" },
  { label: "Inventory", to: "/admin/inventory" },
  { label: "Hospitals", to: "/admin/hospitals" },
];

export function AdminLayout() {
  return <PortalLayout portalName="Admin Operations Hub" portalLabel="Admin" navItems={navItems} />;
}
