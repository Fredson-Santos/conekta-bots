import { useBots } from "@/hooks/useBots";
import { useRules } from "@/hooks/useRules";
import { useSchedules } from "@/hooks/useSchedules";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, Calendar, List, Activity } from "lucide-react";

export function Dashboard() {
    const { bots } = useBots();
    const { rules } = useRules();
    const { schedules } = useSchedules();

    const activeBots = bots?.filter(b => b.ativo).length || 0;
    const totalBots = bots?.length || 0;
    const totalRules = rules?.length || 0;
    const totalSchedules = schedules?.length || 0;

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                <p className="text-muted-foreground">
                    Visão geral do sistema ConektaBots.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Total de Bots
                        </CardTitle>
                        <Bot className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalBots}</div>
                        <p className="text-xs text-muted-foreground">
                            {activeBots} bots ativos
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Regras Criadas
                        </CardTitle>
                        <List className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalRules}</div>
                        <p className="text-xs text-muted-foreground">
                            Automações de resposta
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Agendamentos
                        </CardTitle>
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalSchedules}</div>
                        <p className="text-xs text-muted-foreground">
                            Mensagens programadas
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Execuções (24h)
                        </CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">0</div>
                        <p className="text-xs text-muted-foreground">
                            +0% em relação a ontem
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Visão Geral</CardTitle>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <div className="h-[200px] flex items-center justify-center text-muted-foreground text-sm">
                            Gráfico de atividade (Em breve)
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Bots Recentes</CardTitle>
                        <div className="text-sm text-muted-foreground">
                            Últimos bots adicionados.
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {bots?.slice(0, 5).map(bot => (
                                <div key={bot.id} className="flex items-center">
                                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
                                        <Bot className="h-4 w-4 text-primary" />
                                    </div>
                                    <div className="ml-4 space-y-1">
                                        <p className="text-sm font-medium leading-none">{bot.nome}</p>
                                        <p className="text-xs text-muted-foreground">{bot.phone || "Sem número"}</p>
                                    </div>
                                    <div className="ml-auto font-medium text-xs">
                                        {bot.ativo ? "Ativo" : "Inativo"}
                                    </div>
                                </div>
                            ))}
                            {(!bots || bots.length === 0) && (
                                <div className="text-sm text-muted-foreground text-center">Nenhum bot recente.</div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
