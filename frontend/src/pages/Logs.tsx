import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Log } from "@/types";
import { ScrollText } from "lucide-react";

export function Logs() {
    const { data: logs, isLoading } = useQuery({
        queryKey: ["logs"],
        queryFn: async (): Promise<Log[]> => {
            const { data } = await api.get<Log[]>("/analytics/logs/recent");
            return data;
        },
    });

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">📜 Logs de Atividade</h1>
                <p className="text-muted-foreground">
                    Últimas atividades dos seus bots
                </p>
            </div>

            {isLoading ? (
                <div className="text-center text-muted-foreground py-12">
                    Carregando logs...
                </div>
            ) : (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <ScrollText className="h-5 w-5" />
                            Atividades Recentes
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left">
                                        <th className="pb-3 pr-4 font-medium text-muted-foreground">Data/Hora</th>
                                        <th className="pb-3 pr-4 font-medium text-muted-foreground">Bot</th>
                                        <th className="pb-3 pr-4 font-medium text-muted-foreground">Origem → Destino</th>
                                        <th className="pb-3 pr-4 font-medium text-muted-foreground">Status</th>
                                        <th className="pb-3 font-medium text-muted-foreground">Mensagem</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs?.map((log) => (
                                        <tr key={log.id} className="border-b last:border-0">
                                            <td className="py-3 pr-4 text-muted-foreground whitespace-nowrap">
                                                {new Date(log.data_hora).toLocaleString("pt-BR")}
                                            </td>
                                            <td className="py-3 pr-4 font-medium text-blue-600">
                                                {log.bot_nome}
                                            </td>
                                            <td className="py-3 pr-4">
                                                <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                                                    {log.origem}
                                                </span>
                                                <span className="text-muted-foreground mx-1">→</span>
                                                <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                                                    {log.destino}
                                                </span>
                                            </td>
                                            <td className="py-3 pr-4">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${log.status === "sucesso"
                                                        ? "bg-green-100 text-green-700"
                                                        : log.status === "erro"
                                                            ? "bg-red-100 text-red-700"
                                                            : "bg-yellow-100 text-yellow-700"
                                                    }`}>
                                                    {log.status}
                                                </span>
                                            </td>
                                            <td className="py-3 text-muted-foreground truncate max-w-xs">
                                                {log.mensagem}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {(!logs || logs.length === 0) && (
                                <div className="text-center text-muted-foreground py-8">
                                    Nenhum log de atividade encontrado.
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
