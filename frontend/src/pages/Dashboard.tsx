export function Dashboard() {
    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-medium text-slate-500">Bots Ativos</h3>
                    <p className="text-3xl font-bold mt-2">0</p>
                </div>
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-medium text-slate-500">Regras Ativas</h3>
                    <p className="text-3xl font-bold mt-2">0</p>
                </div>
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <h3 className="text-lg font-medium text-slate-500">Execuções Hoje</h3>
                    <p className="text-3xl font-bold mt-2">0</p>
                </div>
            </div>
        </div>
    );
}
