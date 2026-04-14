import { Navigate } from "react-router-dom";
import { isAuthenticated, getSession } from "../lib/auth";

export default function ProtectedRoute({
  children,
  requireSuperadmin = false,
}: {
  children: React.ReactNode;
  requireSuperadmin?: boolean;
}) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  if (requireSuperadmin && !getSession()?.usuario.es_superadmin) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}