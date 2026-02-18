import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useSchedules } from "@/hooks/useSchedules";
import { useBots } from "@/hooks/useBots";
import { SheetClose } from "@/components/ui/sheet";

const formSchema = z.object({
    mensagem: z.string().min(1, { message: "Mensagem é obrigatória." }),
    cron_expr: z.string().min(1, { message: "Expressão Cron é obrigatória." }),
    bot_id: z.string().min(1, { message: "Selecione um bot." }),
    ativo: z.boolean(),
});

type ScheduleFormValues = z.infer<typeof formSchema>;

export function ScheduleForm({ onSuccess }: { onSuccess?: () => void }) {
    const { createSchedule, isCreating } = useSchedules();
    const { bots } = useBots();

    const form = useForm<ScheduleFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            mensagem: "",
            cron_expr: "0 9 * * *", // Default 9am daily
            ativo: true,
            bot_id: "",
        },
    });

    const onSubmit = (data: ScheduleFormValues) => {
        createSchedule({
            ...data,
            bot_id: parseInt(data.bot_id),
        }, {
            onSuccess: () => {
                form.reset();
                onSuccess?.();
            }
        });
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                    control={form.control}
                    name="bot_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Bot</FormLabel>
                            <FormControl>
                                <select
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    {...field}
                                >
                                    <option value="" disabled>Selecione um bot</option>
                                    {bots?.map(bot => (
                                        <option key={bot.id} value={bot.id.toString()}>
                                            {bot.nome}
                                        </option>
                                    ))}
                                </select>
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="cron_expr"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Cron Expression (Agendamento)</FormLabel>
                            <FormControl>
                                <Input placeholder="0 9 * * *" {...field} />
                            </FormControl>
                            <FormDescription>Ex: "0 9 * * *" para todo dia às 9h.</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="mensagem"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Mensagem</FormLabel>
                            <FormControl>
                                <Input placeholder="Bom dia!" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end gap-2 pt-4">
                    <SheetClose asChild>
                        <Button type="button" variant="outline">Cancelar</Button>
                    </SheetClose>
                    <Button type="submit" disabled={isCreating}>
                        {isCreating ? "Agendar" : "Agendar Mensagem"}
                    </Button>
                </div>
            </form>
        </Form>
    );
}
