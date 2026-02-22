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
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import type { Bot } from "@/types";

const ruleFormSchema = z.object({
    nome: z.string().min(1, "Nome é obrigatório").max(100),
    origem: z.string().min(1, "Origem é obrigatória"),
    destino: z.string().min(1, "Destino é obrigatório"),
    bot_id: z.string().min(1, "Selecione um bot"),
    filtro: z.string().optional(),
    substituto: z.string().optional(),
    bloqueios: z.string().optional(),
    somente_se_tiver: z.string().optional(),
    converter_shopee: z.boolean().default(false),
});

type RuleFormValues = z.infer<typeof ruleFormSchema>;

interface RuleFormProps {
    bots: Bot[];
    onSubmit: (data: any) => void;
    isLoading?: boolean;
}

export function RuleForm({ bots, onSubmit, isLoading }: RuleFormProps) {
    const form = useForm<RuleFormValues>({
        resolver: zodResolver(ruleFormSchema),
        defaultValues: {
            nome: "",
            origem: "",
            destino: "",
            bot_id: "",
            filtro: "",
            substituto: "",
            bloqueios: "",
            somente_se_tiver: "",
            converter_shopee: false,
        },
    });

    function handleSubmit(values: RuleFormValues) {
        onSubmit({
            nome: values.nome,
            origem: values.origem,
            destino: values.destino,
            bot_id: parseInt(values.bot_id),
            filtro: values.filtro || undefined,
            substituto: values.substituto || undefined,
            bloqueios: values.bloqueios || undefined,
            somente_se_tiver: values.somente_se_tiver || undefined,
            converter_shopee: values.converter_shopee,
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
                            <FormLabel>Nome da Regra</FormLabel>
                            <FormControl>
                                <Input placeholder="Ex: Promoções VIP" {...field} />
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
                                <FormLabel>Origem (Username ou ID)</FormLabel>
                                <FormControl>
                                    <Input placeholder="@canal_origem" {...field} />
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
                                <FormLabel>Destino (Username ou ID)</FormLabel>
                                <FormControl>
                                    <Input placeholder="@meu_canal" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="space-y-4 rounded-md border p-4 bg-muted/50">
                    <h4 className="text-sm font-semibold">✂️ Substituição de Texto</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <FormField
                            control={form.control}
                            name="filtro"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Texto para remover (Regex)</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Ex: @canalantigo" {...field} />
                                    </FormControl>
                                    <FormDescription>Padrão regex para filtrar</FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="substituto"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Texto novo</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Ex: @meucanal" {...field} />
                                    </FormControl>
                                    <FormDescription>Texto que substituirá o filtro</FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                </div>

                <div className="space-y-4 rounded-md border p-4 bg-green-50 dark:bg-green-950/20">
                    <h4 className="text-sm font-semibold text-green-800 dark:text-green-300">✅ Whitelist</h4>
                    <FormField
                        control={form.control}
                        name="somente_se_tiver"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Só enviar se conter (separar por vírgula)</FormLabel>
                                <FormControl>
                                    <Textarea
                                        placeholder="Ex: promoção, oferta, grátis"
                                        className="resize-none"
                                        rows={2}
                                        {...field}
                                    />
                                </FormControl>
                                <FormDescription>
                                    Se a mensagem NÃO tiver uma dessas palavras, será ignorada.
                                </FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="space-y-4 rounded-md border p-4 bg-red-50 dark:bg-red-950/20">
                    <h4 className="text-sm font-semibold text-red-800 dark:text-red-300">🚫 Blacklist</h4>
                    <FormField
                        control={form.control}
                        name="bloqueios"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Não enviar se conter (separar por vírgula)</FormLabel>
                                <FormControl>
                                    <Input placeholder="Ex: aposta, cassino, tigrinho" {...field} />
                                </FormControl>
                                <FormDescription>
                                    Se a mensagem tiver qualquer uma dessas palavras, será descartada.
                                </FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="space-y-4 rounded-md border p-4 bg-orange-50 dark:bg-orange-950/20">
                    <h4 className="text-sm font-semibold text-orange-800 dark:text-orange-300">🛍️ Shopee Afiliados</h4>
                    <FormField
                        control={form.control}
                        name="converter_shopee"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                                <FormControl>
                                    <Checkbox
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                    />
                                </FormControl>
                                <div className="space-y-1 leading-none">
                                    <FormLabel>Converter Links Shopee</FormLabel>
                                    <FormDescription>
                                        Converte automaticamente links Shopee em links de afiliado.
                                        Configure as credenciais em Configurações.
                                    </FormDescription>
                                </div>
                            </FormItem>
                        )}
                    />
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Salvando..." : "Salvar Regra"}
                </Button>
            </form>
        </Form>
    );
}
