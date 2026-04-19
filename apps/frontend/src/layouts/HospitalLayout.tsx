import { PortalLayout } from "@/layouts/PortalLayout";

const navItems = [
  { label: "Request Dashboard", to: "/hospital" },
  { label: "Urgent Requests", to: "/hospital/urgent" },
];

export function HospitalLayout() {
  return <PortalLayout portalName="Hospital Coordination Desk" portalLabel="Hospital" navItems={navItems} />;
}
