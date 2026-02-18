import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Login } from "@/pages/Login";
import { Register } from "@/pages/Register";
import { Dashboard } from "@/pages/Dashboard";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { useAuthStore } from "@/store/authStore";

/* Optional: PublicRoute to redirect authenticated users away from login */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        {/* Protected Routes */}
        <Route element={<RequireAuth />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bots" element={<div>Bots Page (Todo)</div>} />
            <Route path="/rules" element={<div>Rules Page (Todo)</div>} />
            <Route path="/schedules" element={<div>Schedules Page (Todo)</div>} />
            <Route path="/logs" element={<div>Logs Page (Todo)</div>} />
          </Route>
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
