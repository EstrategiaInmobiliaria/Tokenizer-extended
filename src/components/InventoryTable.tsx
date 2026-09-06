import { useState, useMemo } from "react";
import type { PalmDiamanteUnit, TorreType, ModelType, UnitStatus } from "~/types/palm-diamante";
import { calculateFinancingPlan, formatCurrency } from "~/utils/payment-calculator";
import { SAMPLE_UNITS, INVENTORY_STATS } from "~/data/inventory";

export function InventoryTable() {
  const [filterTorre, setFilterTorre] = useState<TorreType | "all">("all");
  const [filterModel, setFilterModel] = useState<ModelType | "all">("all");
  const [filterStatus, setFilterStatus] = useState<UnitStatus | "all">("disponible");

  const filteredUnits = useMemo(() => {
    return SAMPLE_UNITS.filter((unit) => {
      if (filterTorre !== "all" && unit.torre !== filterTorre) return false;
      if (filterModel !== "all" && unit.model !== filterModel) return false;
      if (filterStatus !== "all" && unit.status !== filterStatus) return false;
      return true;
    });
  }, [filterTorre, filterModel, filterStatus]);

  const exportToCSV = () => {
    const headers = [
      "ID",
      "Torre",
      "Modelo",
      "m²",
      "Precio Total",
      "Aparta",
      "Firma 7%",
      "Resta Firma",
      "13% Total",
      "Mensualidad 24m",
      "80% Hipoteca",
      "Status",
    ];

    const rows = SAMPLE_UNITS.map((unit) => {
      const plan = calculateFinancingPlan(unit);
      return [
        unit.id,
        unit.torre,
        unit.model,
        unit.metrosCuadrados,
        plan.unit.precioTotal,
        plan.aparta,
        plan.firma7Percent,
        plan.restaFirma,
        plan.percent13Total,
        plan.mensualidad24Meses,
        plan.percent80Hipoteca,
        unit.status,
      ];
    });

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "palm-diamante-inventory.csv";
    a.click();
  };

  return (
    <div className="flex flex-col gap-6 rounded-lg border-2 border-slate-200 bg-white p-6 shadow-lg">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              Inventario Palm Diamante
            </h2>
            <p className="text-sm text-slate-600">
              {INVENTORY_STATS.disponibles} unidades disponibles de {INVENTORY_STATS.total} totales
            </p>
          </div>
          <button
            onClick={exportToCSV}
            className="rounded-md bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition-colors hover:bg-green-700"
          >
            📊 Exportar a Excel/CSV
          </button>
        </div>

        {/* Stats rápidos */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <div className="text-2xl font-bold text-green-600">
              {INVENTORY_STATS.torres["III"].disponibles}
            </div>
            <div className="text-xs text-slate-600">
              Torre III - 24 meses (VOLUMEN)
            </div>
          </div>
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <div className="text-2xl font-bold text-blue-600">
              {INVENTORY_STATS.torres["II"].disponibles}
            </div>
            <div className="text-xs text-slate-600">Torre II - 9 meses</div>
          </div>
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <div className="text-2xl font-bold text-amber-600">
              {INVENTORY_STATS.torres["I"].disponibles}
            </div>
            <div className="text-xs text-slate-600">Torre I - 5 meses</div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="grid gap-3 md:grid-cols-3">
        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-700">
            Filtrar por Torre
          </label>
          <select
            value={filterTorre}
            onChange={(e) => setFilterTorre(e.target.value as TorreType | "all")}
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todas las Torres</option>
            <option value="I-A">Torre I-A (5 meses)</option>
            <option value="I-B">Torre I-B (5 meses)</option>
            <option value="II-A">Torre II-A (9 meses)</option>
            <option value="II-B">Torre II-B (9 meses)</option>
            <option value="III-A">Torre III-A (24 meses) ⭐</option>
            <option value="III-B">Torre III-B (24 meses) ⭐</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-700">
            Filtrar por Modelo
          </label>
          <select
            value={filterModel}
            onChange={(e) => setFilterModel(e.target.value as ModelType | "all")}
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todos los Modelos</option>
            <option value="B1">B1 - Entrada</option>
            <option value="A1">A1 - Intermedio</option>
            <option value="A2">A2 - Intermedio Plus</option>
            <option value="Roof Garden">Roof Garden</option>
            <option value="Garden House">Garden House</option>
            <option value="Penthouse">Penthouse</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-700">
            Status
          </label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as UnitStatus | "all")}
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todos</option>
            <option value="disponible">Disponible</option>
            <option value="apartado">Apartado</option>
            <option value="reservado">Reservado</option>
            <option value="vendido">Vendido</option>
          </select>
        </div>
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b-2 border-slate-300 bg-slate-100">
            <tr>
              <th className="px-3 py-2 text-left font-semibold text-slate-700">Torre</th>
              <th className="px-3 py-2 text-left font-semibold text-slate-700">Modelo</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">m²</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">Precio Total</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">Aparta</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">Firma 7%</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">Mensualidad</th>
              <th className="px-3 py-2 text-right font-semibold text-slate-700">80% Hipoteca</th>
              <th className="px-3 py-2 text-center font-semibold text-slate-700">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filteredUnits.map((unit) => {
              const plan = calculateFinancingPlan(unit);
              return (
                <tr
                  key={unit.id}
                  className={`transition-colors hover:bg-slate-50 ${
                    unit.status === "disponible" ? "" : "opacity-60"
                  }`}
                >
                  <td className="px-3 py-2 text-slate-900">
                    {unit.torre}
                    {(unit.torre === "III-A" || unit.torre === "III-B") && (
                      <span className="ml-1 text-xs text-green-600">⭐</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-slate-900">{unit.model}</td>
                  <td className="px-3 py-2 text-right text-slate-900">
                    {unit.metrosCuadrados}
                  </td>
                  <td className="px-3 py-2 text-right font-semibold text-slate-900">
                    {formatCurrency(plan.unit.precioTotal)}
                  </td>
                  <td className="px-3 py-2 text-right text-green-700">
                    {formatCurrency(plan.aparta)}
                  </td>
                  <td className="px-3 py-2 text-right font-semibold text-blue-700">
                    {formatCurrency(plan.firma7Percent)}
                  </td>
                  <td className="px-3 py-2 text-right text-slate-700">
                    {formatCurrency(plan.mensualidad24Meses)}
                    <span className="ml-1 text-xs text-slate-500">
                      /{plan.mesesFinanciamiento}m
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right text-slate-900">
                    {formatCurrency(plan.percent80Hipoteca)}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-semibold ${
                        unit.status === "disponible"
                          ? "bg-green-100 text-green-700"
                          : unit.status === "apartado"
                          ? "bg-amber-100 text-amber-700"
                          : unit.status === "reservado"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {unit.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-slate-500">
        Mostrando {filteredUnits.length} unidades. Torre III (⭐) tiene 24 meses de financiamiento.
      </p>
    </div>
  );
}
