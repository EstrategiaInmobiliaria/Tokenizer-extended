"""
Example Script - Complete Workflow
Demonstrates full integration of WACC, DCF, and Optimization
"""

import sys
sys.path.append('.')

from core import (
    WACCEngine, MarketParameters, CapitalStructure,
    RealEstateDCF, ProjectAssumptions, RealEstateCashFlows, TerminalValueAssumptions,
    scenario_analysis,
    OperationsOptimizer, Product, ResourceConstraint, DemandConstraint
)


def main():
    print("=" * 80)
    print("MASTER BLUEPRINT - EJEMPLO COMPLETO DE FLUJO DE TRABAJO")
    print("=" * 80)
    
    # ========================================================================
    # PASO 1: Calcular WACC (Costo de Capital)
    # ========================================================================
    print("\n" + "─" * 80)
    print("PASO 1: CÁLCULO DEL WACC")
    print("─" * 80)
    
    market = MarketParameters(
        risk_free_rate=0.05,      # Bonos del tesoro Chile
        market_return=0.12,        # Retorno IPSA histórico
        corporate_tax_rate=0.27    # Tasa corporativa Chile
    )
    
    capital = CapitalStructure(
        equity_value=800_000_000,   # $800M CLP
        debt_value=400_000_000,     # $400M CLP
        beta=1.15,                  # Beta sector inmobiliario
        debt_rate=0.08             # 8% costo deuda
    )
    
    wacc_engine = WACCEngine(market, capital)
    wacc_breakdown = wacc_engine.get_detailed_breakdown()
    
    print(f"\n📊 Estructura de Capital:")
    print(f"   Patrimonio: ${wacc_breakdown['equity_value']:,.0f} ({wacc_breakdown['equity_weight']*100:.1f}%)")
    print(f"   Deuda:      ${wacc_breakdown['debt_value']:,.0f} ({wacc_breakdown['debt_weight']*100:.1f}%)")
    
    print(f"\n💰 Costos de Capital:")
    print(f"   Re (Cost of Equity): {wacc_breakdown['cost_of_equity']*100:.2f}%")
    print(f"   Rd (After Tax):      {wacc_breakdown['cost_of_debt_after_tax']*100:.2f}%")
    
    print(f"\n🎯 WACC = {wacc_breakdown['wacc_percentage']:.2f}%")
    print(f"   → Tasa de descuento para evaluación del proyecto")
    
    # ========================================================================
    # PASO 2: Análisis DCF del Proyecto
    # ========================================================================
    print("\n" + "─" * 80)
    print("PASO 2: ANÁLISIS DCF (Discounted Cash Flow)")
    print("─" * 80)
    
    project_assumptions = ProjectAssumptions(
        project_name="Edificio Residencial Las Condes",
        initial_investment=1_200_000_000,
        discount_rate=wacc_breakdown['wacc'],  # Usar WACC calculado
        projection_years=5
    )
    
    cash_flows = RealEstateCashFlows(
        rental_income=[150_000_000, 165_000_000, 180_000_000, 195_000_000, 210_000_000],
        sales_revenue=[0, 0, 200_000_000, 300_000_000, 400_000_000],
        operating_costs=[50_000_000, 52_000_000, 54_000_000, 56_000_000, 58_000_000],
        capex=[20_000_000, 15_000_000, 15_000_000, 10_000_000, 10_000_000],
        taxes=[25_000_000, 28_000_000, 35_000_000, 45_000_000, 55_000_000]
    )
    
    terminal_assumptions = TerminalValueAssumptions(
        method="perpetuity",
        perpetual_growth_rate=0.02
    )
    
    dcf = RealEstateDCF(project_assumptions, cash_flows, terminal_assumptions)
    dcf_analysis = dcf.get_comprehensive_analysis()
    
    print(f"\n🏢 Proyecto: {dcf_analysis['project_name']}")
    print(f"   Inversión Inicial: ${dcf_analysis['initial_investment']:,.0f}")
    print(f"   WACC (Descuento):  {dcf_analysis['discount_rate']*100:.2f}%")
    
    print(f"\n📈 Resultados DCF:")
    print(f"   VPN (NPV):            ${dcf_analysis['npv']:,.0f}")
    print(f"   TIR (IRR):            {dcf_analysis['irr']*100:.2f}%")
    print(f"   Índice Rentabilidad:  {dcf_analysis['profitability_index']:.2f}")
    print(f"   Payback:              {dcf_analysis['payback_period']:.1f} años")
    
    print(f"\n{'✅' if dcf_analysis['accept_project'] else '❌'} DECISIÓN:")
    print(f"   {dcf_analysis['decision_rationale']}")
    
    # Análisis de escenarios
    print(f"\n📊 Análisis de Escenarios:")
    scenarios = scenario_analysis(dcf)
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n   {scenario_name.upper()}:")
        print(f"      VPN: ${scenario_data['npv']:,.0f}")
        print(f"      TIR: {scenario_data['irr']*100:.2f}%")
    
    # ========================================================================
    # PASO 3: Optimización de Mix de Productos
    # ========================================================================
    print("\n" + "─" * 80)
    print("PASO 3: OPTIMIZACIÓN DE MIX DE PRODUCTOS")
    print("─" * 80)
    
    products = [
        Product(
            name="Apartamento Tipo A (45m²)",
            unit_price=4_500_000,
            variable_cost=2_800_000
        ),
        Product(
            name="Apartamento Tipo B (65m²)",
            unit_price=6_000_000,
            variable_cost=3_500_000
        )
    ]
    
    constraints = [
        ResourceConstraint(
            name="Área Total Construible (m²)",
            total_available=15_000,
            consumption_rates=[45, 65]
        ),
        ResourceConstraint(
            name="Presupuesto de Construcción",
            total_available=300_000_000,
            consumption_rates=[2_800_000, 3_500_000]
        )
    ]
    
    demand = DemandConstraint(
        min_demand=[20, 15],
        max_demand=[200, 150]
    )
    
    optimizer = OperationsOptimizer(
        products=products,
        resource_constraints=constraints,
        demand_constraints=demand,
        fixed_costs=50_000_000
    )
    
    optimization_result = optimizer.optimize_linear_programming()
    
    if optimization_result["success"]:
        print(f"\n✅ Solución Óptima Encontrada:")
        
        for product, qty in zip(optimization_result["products"], optimization_result["optimal_quantities"]):
            print(f"   {product}: {qty:.0f} unidades")
        
        print(f"\n💰 Beneficio Óptimo: ${optimization_result['optimal_profit']:,.0f}")
        
        breakdown = optimization_result["detailed_breakdown"]
        summary = breakdown["summary"]
        
        print(f"\n📊 Resumen Financiero:")
        print(f"   Ingresos Totales:       ${summary['total_revenue']:,.0f}")
        print(f"   Costos Variables:       ${summary['total_variable_costs']:,.0f}")
        print(f"   Margen Contribución:    ${summary['total_contribution_margin']:,.0f}")
        print(f"   Costos Fijos:           ${summary['fixed_costs']:,.0f}")
        print(f"   EBIT:                   ${summary['ebit']:,.0f}")
        print(f"   Margen Contribución %:  {summary['contribution_margin_ratio']:.1f}%")
        
        print(f"\n🔧 Análisis de Restricciones:")
        for constraint in breakdown["constraints"]:
            status_icon = "🔴" if constraint["is_binding"] else "🟢"
            status_text = "ACTIVA (Limitante)" if constraint["is_binding"] else "Con holgura"
            print(f"   {status_icon} {constraint['constraint']}:")
            print(f"      Disponible: {constraint['available']:,.0f}")
            print(f"      Usado:      {constraint['used']:,.0f} ({constraint['utilization_percentage']:.1f}%)")
            print(f"      Holgura:    {constraint['slack']:,.0f}")
            print(f"      Estado:     {status_text}")
    
    # ========================================================================
    # RESUMEN EJECUTIVO FINAL
    # ========================================================================
    print("\n" + "=" * 80)
    print("RESUMEN EJECUTIVO")
    print("=" * 80)
    
    print(f"\n1️⃣  COSTO DE CAPITAL (WACC): {wacc_breakdown['wacc_percentage']:.2f}%")
    print(f"   → Tasa mínima de retorno requerida")
    
    print(f"\n2️⃣  EVALUACIÓN DEL PROYECTO:")
    print(f"   VPN: ${dcf_analysis['npv']:,.0f}")
    print(f"   TIR: {dcf_analysis['irr']*100:.2f}%")
    print(f"   Decisión: {'✅ ACEPTAR' if dcf_analysis['accept_project'] else '❌ RECHAZAR'}")
    
    if optimization_result["success"]:
        print(f"\n3️⃣  MIX ÓPTIMO DE PRODUCTOS:")
        for product, qty in zip(optimization_result["products"], optimization_result["optimal_quantities"]):
            print(f"   {product}: {qty:.0f} unidades")
        print(f"   Beneficio Proyectado: ${optimization_result['optimal_profit']:,.0f}")
    
    print(f"\n{'=' * 80}")
    print("FIN DEL ANÁLISIS")
    print("=" * 80)
    
    # Generar visualización (si es posible)
    try:
        optimizer.plot_2d_optimization(save_path="optimization_plot.png")
        print("\n📊 Gráfico de optimización guardado: optimization_plot.png")
    except:
        pass


if __name__ == "__main__":
    main()
