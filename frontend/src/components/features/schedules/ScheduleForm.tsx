import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
    FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import type { Bot } from "@/types";

const scheduleFormSchema = z.object({
    nome: z.string().min(1, "Nome é obrigatório").max(100),
    bot_id: z.string().min(1, "Selecione um bot"),
    origem: z.string().min(1, "Origem é obrigatória"),
    destino: z.string().min(1, "Destino é obrigatório"),
    msg_id_atual: z.string().min(1, "ID da mensagem é obrigatório"),
    tipo_envio: z.string().min(1, "Tipo de envio é obrigatório"),
    horario: z.string().min(1, "Horário é obrigatório"),
});

type ScheduleFormValues = z.infer<typeof scheduleFormSchema>;

interface ScheduleFormProps {
    bots: Bot[];
    onSubmit: (data: any) => void;
    isLoading?: boolean;
}

export function ScheduleForm({ bots, onSubmit, isLoading }: ScheduleFormProps) {
    const form = useForm<ScheduleFormValues>({
        resolver: zodResolver(scheduleFormSchema),
        defaultValues: {
            nome: "",
            bot_id: "",
            origem: "",
            destino: "",
            msg_id_atual: "",
            tipo_envio: "sequencial",
            horario: "",
        },
    });

    function handleSubmit(values: ScheduleFormValues) {
        onSubmit({
            nome: values.nome,
            bot_id: parseInt(values.bot_id),
            origem: values.origem,
            destino: values.destino,
            msg_id_atual: parseInt(values.msg_id_atual),
            tipo_envio: values.tipo_envio,
            horario: values.horario,
        });
        form.reset();
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
                <FormField
                    control={form.control}
                    name="nome"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nome da Tarefa</FormLabel>
                            <FormControl>
                                <Input placeholder="Ex: Oferta Manhã" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="bot_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Bot Responsável</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione um bot" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {bots.map((bot) => (
                                        <SelectItem key={bot.id} value={String(bot.id)}>
                                            {bot.nome}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="origem"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Origem (ID ou User do Canal)</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ex: -100123456789" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="destino"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Destino (ID ou User do Canal)</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ex: @meucanal" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="horario"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Horários (separados por vírgula)</FormLabel>
                            <FormControl>
                                <Input placeholder="Ex: 09:00, 12:30, 18:00" {...field} />
                            </FormControl>
                            <FormDescription>
                                O bot verificará todos esses horários.
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="space-y-4 rounded-md border p-4 bg-muted/50">
                    <h4 className="text-sm font-semibold">📋 Configuração de Mensagem</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                            control={form.control}
                            name="msg_id_atual"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>ID da Mensagem Inicial</FormLabel>
                                    <FormControl>
                                        <Input type="number" placeholder="Ex: 1045" {...field} />
                                    </FormControl>
                                    <FormDescription>
                                        Pegue o ID clicando em "Copiar Link" no Telegram
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="tipo_envio"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Tipo de Envio</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione o tipo" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="sequencial">🔄 Sequencial (101, 102, 103...)</SelectItem>
                                            <SelectItem value="fixo">⏹ Fixo (sempre a mesma)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormDescription>
                                        Sequencial avança o ID automaticamente.
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Salvando..." : "Salvar Agendamento"}
                </Button>
            </form>
        </Form>
    );
}
