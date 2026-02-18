import { useState } from "react";
import { useSchedules } from "@/hooks/useSchedules";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Calendar, Trash2 } from "lucide-react";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import { ScheduleForm } from "@/components/features/schedules/ScheduleForm";

export function Schedules() {
    const { schedules, isLoading, deleteSchedule } = useSchedules();
    const [isSheetOpen, setIsSheetOpen] = useState(false);

    if (isLoading) {
        return <div className="p-8">Carregando agendamentos...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Agendamentos</h2>
                    <p className="text-muted-foreground">
                        Envie mensagens automáticas em horários específicos.
                    </p>
                </div>

                <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Novo Agendamento
                        </Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>Criar Agendamento</SheetTitle>
                            <SheetDescription>
                                Configure a mensagem e o horário.
                            </SheetDescription>
                        </SheetHeader>
                        <ScheduleForm onSuccess={() => setIsSheetOpen(false)} />
                    </SheetContent>
                </Sheet>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {schedules?.map((schedule) => (
                    <Card key={schedule.id}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {schedule.cron_expr}
                            </CardTitle>
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm mt-2 font-medium">Mensagem:</div>
                            <div className="text-sm text-muted-foreground line-clamp-2">{schedule.mensagem}</div>

                            <div className="mt-4 text-xs flex items-center gap-2">
                                <span className={`inline-block w-2 h-2 rounded-full ${schedule.ativo ? "bg-green-500" : "bg-red-500"}`} />
                                {schedule.ativo ? "Ativo" : "Inativo"}
                            </div>
                        </CardContent>
                        <CardFooter className="flex justify-end">
                            <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => deleteSchedule(schedule.id)}>
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                ))}

                {schedules?.length === 0 && (
                    <div className="col-span-full text-center py-12 border rounded-lg border-dashed">
                        <h3 className="text-lg font-medium">Nenhum agendamento</h3>
                        <p className="text-sm text-muted-foreground mt-2">Crie seu primeiro agendamento.</p>
                        <Button className="mt-4" variant="outline" onClick={() => setIsSheetOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Agendar
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
