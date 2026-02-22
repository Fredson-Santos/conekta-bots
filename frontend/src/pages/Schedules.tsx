import { useState } from "react";
import { useBots } from "@/hooks/useBots";
import { useSchedules } from "@/hooks/useSchedules";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { ScheduleForm } from "@/components/features/schedules/ScheduleForm";
import { Plus, Trash2, Pause, Play, ArrowRight, Clock } from "lucide-react";

export function Schedules() {
    const { bots } = useBots();
    const { schedules, createSchedule, deleteSchedule, toggleSchedule, isCreating } = useSchedules();
    const [open, setOpen] = useState(false);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">📅 Agendamentos</h1>
                    <p className="text-muted-foreground">
                        Gerencie o agendamento de postagens automáticas
                    </p>
                </div>
                <Sheet open={open} onOpenChange={setOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Novo Agendamento
                        </Button>
                    </SheetTrigger>
                    <SheetContent className="sm:max-w-lg overflow-y-auto">
                        <SheetHeader>
                            <SheetTitle>Novo Agendamento</SheetTitle>
                        </SheetHeader>
                        <div className="mt-4">
                            <ScheduleForm
                                bots={bots || []}
                                onSubmit={(data) => {
                                    createSchedule(data, {
                                        onSuccess: () => setOpen(false),
                                    });
                                }}
                                isLoading={isCreating}
                            />
                        </div>
                    </SheetContent>
                </Sheet>
            </div>

            <div className="grid gap-4">
                {schedules?.map((schedule) => (
                    <Card key={schedule.id} className={!schedule.ativo ? "opacity-60" : ""}>
                        <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-blue-600" />
                                    {schedule.horario}
                                    <span className="text-sm font-normal text-muted-foreground">
                                        — {schedule.nome}
                                    </span>
                                    {!schedule.ativo && (
                                        <span className="text-xs text-red-500 font-bold border border-red-200 px-1.5 py-0.5 rounded">
                                            PAUSADO
                                        </span>
                                    )}
                                </CardTitle>
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() => toggleSchedule({ scheduleId: schedule.id, botId: schedule.bot_id })}
                                        title={schedule.ativo ? "Pausar" : "Retomar"}
                                    >
                                        {schedule.ativo ? (
                                            <Pause className="h-4 w-4 text-yellow-600" />
                                        ) : (
                                            <Play className="h-4 w-4 text-green-600" />
                                        )}
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() => deleteSchedule({ scheduleId: schedule.id, botId: schedule.bot_id })}
                                    >
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                    </Button>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-2 mb-3">
                                <span className="bg-muted px-2 py-1 rounded text-sm font-mono">
                                    {schedule.origem}
                                </span>
                                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                                <span className="bg-muted px-2 py-1 rounded text-sm font-mono">
                                    {schedule.destino}
                                </span>
                            </div>
                            <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                                <span className="bg-muted px-2 py-0.5 rounded font-mono">
                                    📋 Próximo ID: {schedule.msg_id_atual}
                                </span>
                                <span className={`px-2 py-0.5 rounded font-bold uppercase ${schedule.tipo_envio === "sequencial"
                                        ? "bg-green-100 dark:bg-green-900/30 text-green-700"
                                        : "bg-gray-100 dark:bg-gray-800 text-gray-600"
                                    }`}>
                                    {schedule.tipo_envio === "sequencial" ? "🔄 Sequencial" : "⏹ Fixo"}
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {(!schedules || schedules.length === 0) && (
                    <div className="text-center text-muted-foreground py-12">
                        Nenhum agendamento cadastrado. Clique em "Novo Agendamento".
                    </div>
                )}
            </div>
        </div>
    );
}
