import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { settingsService } from "@/services/settingsService";
import type { SettingsUpdate } from "@/services/settingsService";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function Settings() {
    const queryClient = useQueryClient();

    const { data: config, isLoading } = useQuery({
        queryKey: ["settings"],
        queryFn: settingsService.getSettings,
    });

    const [shopeeAppId, setShopeeAppId] = useState("");
    const [shopeeAppSecret, setShopeeAppSecret] = useState("");
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        if (config) {
            setShopeeAppId(config.shopee_app_id ?? "");
            setShopeeAppSecret(config.shopee_app_secret ?? "");
        }
    }, [config]);

    const { mutate: save, isPending } = useMutation({
        mutationFn: (data: SettingsUpdate) => settingsService.updateSettings(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["settings"] });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        },
    });

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        save({
            shopee_app_id: shopeeAppId || null,
            shopee_app_secret: shopeeAppSecret || null,
        });
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
                Carregando configurações...
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">⚙️ Configurações</h1>
                <p className="text-muted-foreground">
                    Gerencie suas integrações e credenciais
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        🛍️ Shopee Afiliados
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="shopee_app_id">App ID</Label>
                            <Input
                                id="shopee_app_id"
                                placeholder="Ex: 123456789"
                                value={shopeeAppId}
                                onChange={(e) => setShopeeAppId(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="shopee_app_secret">App Secret</Label>
                            <Input
                                id="shopee_app_secret"
                                type="password"
                                placeholder="••••••••••••"
                                value={shopeeAppSecret}
                                onChange={(e) => setShopeeAppSecret(e.target.value)}
                            />
                        </div>

                        <p className="text-xs text-muted-foreground">
                            Obtenha suas credenciais no{" "}
                            <a
                                href="https://affiliate.shopee.com.br"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="underline text-primary"
                            >
                                Painel de Afiliados da Shopee
                            </a>
                            . Essas credenciais são usadas para converter links Shopee em links de afiliado
                            nas regras que tiverem a opção "Converter Links Shopee" ativada.
                        </p>

                        <div className="flex items-center gap-3">
                            <Button type="submit" disabled={isPending}>
                                {isPending ? "Salvando..." : "Salvar"}
                            </Button>
                            {saved && (
                                <span className="text-sm text-green-600 font-medium">
                                    ✅ Configurações salvas!
                                </span>
                            )}
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
