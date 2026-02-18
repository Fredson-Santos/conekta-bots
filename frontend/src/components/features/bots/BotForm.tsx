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
import { useBots } from "@/hooks/useBots";
import { SheetClose } from "@/components/ui/sheet";

const formSchema = z.object({
    nome: z.string().min(2, {
        message: "Nome deve ter pelo menos 2 caracteres.",
    }),
    api_id: z.string().min(1, { message: "API ID é obrigatório." }),
    api_hash: z.string().min(1, { message: "API Hash é obrigatório." }),
    phone: z.string().min(1, { message: "Telefone é obrigatório." }),
    tipo: z.enum(["user", "bot"]),
    bot_token: z.string().optional(),
});

type BotFormValues = z.infer<typeof formSchema>;

export function BotForm({ onSuccess }: { onSuccess?: () => void }) {
    const { createBot, isCreating } = useBots();

    const form = useForm<BotFormValues>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            nome: "",
            api_id: "",
            api_hash: "",
            phone: "",
            tipo: "user",
            bot_token: "",
        },
    });

    const onSubmit = (data: BotFormValues) => {
        createBot(data, {
            onSuccess: () => {
                form.reset();
                onSuccess?.();
            }
        });
    };

    const tipo = form.watch("tipo");

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
                <FormField
                    control={form.control}
                    name="nome"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nome</FormLabel>
                            <FormControl>
                                <Input placeholder="Meu Bot" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="api_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>API ID</FormLabel>
                            <FormControl>
                                <Input placeholder="123456" {...field} />
                            </FormControl>
                            <FormDescription>Obtenha em my.telegram.org</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="api_hash"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>API Hash</FormLabel>
                            <FormControl>
                                <Input placeholder="abcdef123456..." type="password" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="phone"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Telefone</FormLabel>
                            <FormControl>
                                <Input placeholder="+5511999999999" {...field} />
                            </FormControl>
                            <FormDescription>Formato internacional (+55...)</FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="tipo"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Tipo</FormLabel>
                            <FormControl>
                                <select
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    {...field}
                                >
                                    <option value="user">Userbot (Conta Pessoal)</option>
                                    <option value="bot">Bot API</option>
                                </select>
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                {tipo === "bot" && (
                    <FormField
                        control={form.control}
                        name="bot_token"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Bot Token</FormLabel>
                                <FormControl>
                                    <Input placeholder="123456:ABC-DEF..." {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                )}

                <div className="flex justify-end gap-2 pt-4">
                    <SheetClose asChild>
                        <Button type="button" variant="outline">Cancelar</Button>
                    </SheetClose>
                    <Button type="submit" disabled={isCreating}>
                        {isCreating ? "Criando..." : "Criar Bot"}
                    </Button>
                </div>
            </form>
        </Form>
    );
}
