import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Shell from "./components/Shell";
import { getSession, getToken } from "./lib/auth";
import { api } from "./lib/api";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ClienteDashboardPage from "./pages/ClienteDashboardPage";
import LeadsPage from "./pages/LeadsPage";
import LeadDetailPage from "./pages/LeadDetailPage";
import PropiedadesPage from "./pages/PropiedadesPage";
import PropiedadFormPage from "./pages/PropiedadFormPage";
import EmpresasPage from "./pages/EmpresasPage";
import EmpresaFormPage from "./pages/EmpresaFormPage";
import UsuariosPage from "./pages/UsuariosPage";
import UsuarioFormPage from "./pages/UsuarioFormPage";
import ImportacionesPage from "./pages/ImportacionesPage";

function DashboardRouter() {
  const session = getSession();
  if (session?.usuario.es_superadmin) return <DashboardPage />;
  return <ClienteDashboardPage />;
}

export default function App() {
  useEffect(() => {
    if (getToken()) {
      api.get("/admin/auth/me").catch(() => {});
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Shell />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"                        element={<DashboardRouter />} />
          <Route path="propiedades"                      element={<PropiedadesPage />} />
          <Route path="propiedades/nueva"                element={<PropiedadFormPage />} />
          <Route path="propiedades/:id/editar"           element={<PropiedadFormPage />} />
          <Route path="leads"                            element={<LeadsPage />} />
          <Route path="leads/:id"                        element={<LeadDetailPage />} />
          <Route path="empresas" element={<ProtectedRoute requireSuperadmin><EmpresasPage /></ProtectedRoute>} />
          <Route path="empresas/:id/editar" element={<ProtectedRoute requireSuperadmin><EmpresaFormPage /></ProtectedRoute>} />
          <Route path="usuarios" element={<ProtectedRoute requireSuperadmin><UsuariosPage /></ProtectedRoute>} />
          <Route path="usuarios/:id/editar" element={<ProtectedRoute requireSuperadmin><UsuarioFormPage /></ProtectedRoute>} />
          <Route path="importaciones" element={<ProtectedRoute requireSuperadmin><ImportacionesPage /></ProtectedRoute>} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}