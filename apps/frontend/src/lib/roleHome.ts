import type { UserRole } from "@/types/auth";

export const roleHomePath: Record<UserRole, string> = {
  donor: "/donor",
  admin: "/admin",
  hospital: "/hospital",
};
