import { NavLink } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import {
    LayoutDashboard,
    Bot,
    Zap,
    Calendar,
    ScrollText,
    LogOut,
    Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard },
    { to: "/bots", label: "Bots", icon: Bot },
    { to: "/rules", label: "Regras", icon: Zap },
    { to: "/schedules", label: "Agendamentos", icon: Calendar },
    { to: "/logs", label: "Logs", icon: ScrollText },
    { to: "/configuracoes", label: "Configurações", icon: Settings },
];

export function Sidebar() {
    const user = useAuthStore((state) => state.user);
    const logout = useAuthStore((state) => state.logout);

    const initials = user?.email
        ? user.email.substring(0, 2).toUpperCase()
        : "?";

    return (
        <aside className="flex h-full w-64 flex-col border-r bg-card">
            <div className="flex h-14 items-center border-b px-4">
                <h2 className="text-lg font-bold">🤖 ConektaBots</h2>
            </div>

            <nav className="flex-1 space-y-1 p-3">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        end={item.to === "/"}
                        className={({ isActive }) =>
                            `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${isActive
                                ? "bg-primary text-primary-foreground"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                            }`
                        }
                    >
                        <item.icon className="h-4 w-4" />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div className="border-t p-3">
                <div className="flex items-center gap-3 rounded-md px-3 py-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">
                        {initials}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="truncate text-sm font-medium">
                            {user?.email || "Carregando..."}
                        </p>
                        <p className="truncate text-xs text-muted-foreground">
                            {user?.plan || "—"}
                        </p>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={logout}
                        title="Sair"
                    >
                        <LogOut className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </aside>
    );
}
