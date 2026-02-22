import { useState } from "react";
import { useBots } from "@/hooks/useBots";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Bot as BotIcon, Power, PowerOff, Trash2 } from "lucide-react";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import { BotForm } from "@/components/features/bots/BotForm";

export function Bots() {
    const { bots, isLoading, toggleBot, deleteBot } = useBots();
    const [isSheetOpen, setIsSheetOpen] = useState(false);

    if (isLoading) {
        return <div className="p-8">Carregando bots...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Meus Bots</h2>
                    <p className="text-muted-foreground">
                        Gerencie seus bots do Telegram aqui.
                    </p>
                </div>

                <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                    <SheetTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            Novo Bot
                        </Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>Adicionar Novo Bot</SheetTitle>
                            <SheetDescription>
                                Preencha os dados do seu bot ou userbot do Telegram.
                            </SheetDescription>
                        </SheetHeader>
                        <BotForm onSuccess={() => setIsSheetOpen(false)} />
                    </SheetContent>
                </Sheet>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {bots?.map((bot) => (
                    <Card key={bot.id} className={!bot.ativo ? "opacity-70" : ""}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {bot.nome}
                            </CardTitle>
                            <BotIcon className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{bot.phone || "Sem número"}</div>
                            <p className="text-xs text-muted-foreground">
                                {bot.tipo === 'user' ? 'Userbot' : 'Bot API'}
                            </p>
                            <div className="mt-2 text-xs flex items-center gap-2">
                                <span className={`inline-block w-2 h-2 rounded-full ${bot.ativo ? "bg-green-500" : "bg-red-500"}`} />
                                {bot.ativo ? "Ativo" : "Inativo"}
                            </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                            <Button variant="ghost" size="sm" onClick={() => toggleBot(bot.id)}>
                                {bot.ativo ? <PowerOff className="h-4 w-4 mr-2" /> : <Power className="h-4 w-4 mr-2" />}
                                {bot.ativo ? "Parar" : "Iniciar"}
                            </Button>
                            <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => deleteBot(bot.id)}>
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                ))}

                {bots?.length === 0 && (
                    <div className="col-span-full text-center py-12 border rounded-lg border-dashed">
                        <h3 className="text-lg font-medium">Nenhum bot encontrado</h3>
                        <p className="text-sm text-muted-foreground mt-2">Comece criando seu primeiro bot.</p>
                        <Button className="mt-4" variant="outline" onClick={() => setIsSheetOpen(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            Novo Bot
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
