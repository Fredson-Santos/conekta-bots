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
import { useRules } from "@/hooks/useRules";
import { useBots } from "@/hooks/useBots";
import { SheetClose } from "@/components/ui/sheet";

const formSchema = z.object({
    nome: z.string().min(2, {
        message: "Nome deve ter pelo menos 2 caracteres.",
    }),
    gatilho: z.string().min(1, { message: "Gatilho é obrigatório (/comando)." }),
    resposta: z.string().min(1, { message: "Resposta é obrigatória." }),
    bot_id: z.string().min(1, { message: "Selecione um bot." }), // form handles string, convert to number on submit
    ativo: z.boolean(),
});

type RuleFormValues = z.infer<typeof formSchema>;

export function RuleForm({ onSuccess }: { onSuccess?: () => void }) {
    const { createRule, isCreating } = useRules();
    const { bots } = useBots();

    const form = useForm<RuleFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            nome: "",
            gatilho: "",
            resposta: "",
            ativo: true,
            bot_id: "",
        },
    });

    const onSubmit = (data: RuleFormValues) => {
        createRule({
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
                    name="nome"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nome da Regra</FormLabel>
                            <FormControl>
                                <Input placeholder="Boas Vindas" {...field} />
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
                    name="gatilho"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Gatilho (ex: /start)</FormLabel>
                            <FormControl>
                                <Input placeholder="/comando" {...field} />
                            </FormControl>
                            <FormDescription>Comando ou texto exato que dispara a regra.</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="resposta"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Resposta</FormLabel>
                            <FormControl>
                                <Input placeholder="Olá! Como posso ajudar?" {...field} />
                            </FormControl>
                            <FormDescription>Texto a ser enviado.</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end gap-2 pt-4">
                    <SheetClose asChild>
                        <Button type="button" variant="outline">Cancelar</Button>
                    </SheetClose>
                    <Button type="submit" disabled={isCreating}>
                        {isCreating ? "Criando..." : "Criar Regra"}
                    </Button>
                </div>
            </form>
        </Form>
    );
}
