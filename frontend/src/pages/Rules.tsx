import { useState } from "react";
import { useBots } from "@/hooks/useBots";
import { useRules } from "@/hooks/useRules";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { RuleForm } from "@/components/features/rules/RuleForm";
import { Plus, Trash2, Pause, Play, ArrowRight } from "lucide-react";

export function Rules() {
    const { bots } = useBots();
    const { rules, createRule, deleteRule, toggleRule, isCreating } = useRules();
    const [open, setOpen] = useState(false);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">⚡ Regras de Repasse</h1>
                    <p className="text-muted-foreground">
                        Gerencie as regras de encaminhamento de mensagens
                    </p>
                </div>
                <Sheet open={open} onOpenChange={setOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Nova Regra
                        </Button>
                    </SheetTrigger>
                    <SheetContent className="sm:max-w-lg overflow-y-auto">
                        <SheetHeader>
                            <SheetTitle>Adicionar Nova Regra</SheetTitle>
                        </SheetHeader>
                        <div className="mt-4">
                            <RuleForm
                                bots={bots || []}
                                onSubmit={(data) => {
                                    createRule(data, {
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
                {rules?.map((rule) => (
                    <Card key={rule.id} className={!rule.ativo ? "opacity-60" : ""}>
                        <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-lg flex items-center gap-2">
                                    {rule.nome}
                                    {!rule.ativo && (
                                        <span className="text-xs text-red-500 font-bold border border-red-200 px-1.5 py-0.5 rounded">
                                            PAUSADO
                                        </span>
                                    )}
                                    {rule.converter_shopee && (
                                        <span className="text-xs text-orange-600 font-bold border border-orange-200 bg-orange-50 dark:bg-orange-900/30 px-1.5 py-0.5 rounded">
                                            🛍️ Shopee
                                        </span>
                                    )}
                                </CardTitle>
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() => toggleRule({ ruleId: rule.id, botId: rule.bot_id })}
                                        title={rule.ativo ? "Pausar" : "Retomar"}
                                    >
                                        {rule.ativo ? (
                                            <Pause className="h-4 w-4 text-yellow-600" />
                                        ) : (
                                            <Play className="h-4 w-4 text-green-600" />
                                        )}
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() => deleteRule({ ruleId: rule.id, botId: rule.bot_id })}
                                    >
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                    </Button>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-2 mb-3">
                                <span className="bg-muted px-2 py-1 rounded text-sm font-mono">
                                    {rule.origem}
                                </span>
                                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                                <span className="bg-muted px-2 py-1 rounded text-sm font-mono">
                                    {rule.destino}
                                </span>
                            </div>
                            <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                                {rule.filtro && (
                                    <span className="bg-yellow-100 dark:bg-yellow-900/30 px-2 py-0.5 rounded">
                                        ✂️ Filtro: {rule.filtro}
                                    </span>
                                )}
                                {rule.substituto && (
                                    <span className="bg-yellow-100 dark:bg-yellow-900/30 px-2 py-0.5 rounded">
                                        🔄 Substituto: {rule.substituto}
                                    </span>
                                )}
                                {rule.bloqueios && (
                                    <span className="bg-red-100 dark:bg-red-900/30 px-2 py-0.5 rounded">
                                        🚫 Bloqueios: {rule.bloqueios}
                                    </span>
                                )}
                                {rule.somente_se_tiver && (
                                    <span className="bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded">
                                        ✅ Whitelist: {rule.somente_se_tiver}
                                    </span>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {(!rules || rules.length === 0) && (
                    <div className="text-center text-muted-foreground py-12">
                        Nenhuma regra cadastrada. Clique em "Nova Regra".
                    </div>
                )}
            </div>
        </div>
    );
}
