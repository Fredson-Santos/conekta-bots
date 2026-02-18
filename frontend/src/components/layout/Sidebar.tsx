import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Bot, Calendar, FileText, Home, List, Shield } from "lucide-react";

const navItems = [
    { name: "Dashboard", href: "/", icon: Home },
    { name: "Meus Bots", href: "/bots", icon: Bot },
    { name: "Regras", href: "/rules", icon: List },
    { name: "Agendamentos", href: "/schedules", icon: Calendar },
    { name: "Logs & Analytics", href: "/logs", icon: FileText },
];

export function Sidebar() {
    const location = useLocation();

    return (
        <aside className="hidden md:flex h-screen w-64 flex-col border-r bg-background">
            <div className="flex h-16 items-center border-b px-6">
                <Shield className="mr-2 h-6 w-6 text-primary" />
                <span className="text-lg font-bold">ConektaBots</span>
            </div>
            <nav className="flex-1 space-y-1 p-4">
                {navItems.map((item) => (
                    <Link
                        key={item.href}
                        to={item.href}
                        className={cn(
                            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                            location.pathname === item.href
                                ? "bg-primary/10 text-primary"
                                : "text-muted-foreground"
                        )}
                    >
                        <item.icon className="h-4 w-4" />
                        <span>{item.name}</span>
                    </Link>
                ))}
            </nav>
            <div className="border-t p-4">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <span className="text-xs font-bold text-primary">FS</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium">Admin User</span>
                        <span className="text-xs text-muted-foreground">Pro Plan</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
