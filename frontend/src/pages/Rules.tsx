import { useState } from "react";
import { useRules } from "@/hooks/useRules";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, List, Trash2 } from "lucide-react";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import { RuleForm } from "@/components/features/rules/RuleForm";

export function Rules() {
    const { rules, isLoading, deleteRule } = useRules();
    const [isSheetOpen, setIsSheetOpen] = useState(false);

    if (isLoading) {
        return <div className="p-8">Carregando regras...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Regras de Automação</h2>
                    <p className="text-muted-foreground">
                        Configure respostas automáticas para seus bots.
                    </p>
                </div>

                <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Nova Regra
                        </Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>Adicionar Nova Regra</SheetTitle>
                            <SheetDescription>
                                Defina um gatilho e uma resposta.
                            </SheetDescription>
                        </SheetHeader>
                        <RuleForm onSuccess={() => setIsSheetOpen(false)} />
                    </SheetContent>
                </Sheet>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {rules?.map((rule) => (
                    <Card key={rule.id}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {rule.nome}
                            </CardTitle>
                            <List className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-sm font-bold mt-2">Gatilho: <span className="font-normal font-mono bg-muted px-1 rounded">{rule.gatilho}</span></div>
                            <div className="text-sm font-bold mt-1">Resposta: <span className="font-normal text-muted-foreground line-clamp-2">{rule.resposta}</span></div>

                            <div className="mt-4 text-xs flex items-center gap-2">
                                <span className={`inline-block w-2 h-2 rounded-full ${rule.ativo ? "bg-green-500" : "bg-red-500"}`} />
                                {rule.ativo ? "Ativa" : "Inativa"}
                            </div>
                        </CardContent>
                        <CardFooter className="flex justify-end">
                            <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => deleteRule(rule.id)}>
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                ))}

                {rules?.length === 0 && (
                    <div className="col-span-full text-center py-12 border rounded-lg border-dashed">
                        <h3 className="text-lg font-medium">Nenhuma regra encontrada</h3>
                        <p className="text-sm text-muted-foreground mt-2">Crie sua primeira automação.</p>
                        <Button className="mt-4" variant="outline" onClick={() => setIsSheetOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Nova Regra
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
