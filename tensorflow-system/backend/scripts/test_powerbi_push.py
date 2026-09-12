#!/usr/bin/env python3
"""
Valida la Push URL del Streaming Dataset de Power BI.

Uso:
  1. Crea el dataset en app.powerbi.com (ver POWERBI_STREAMING_SETUP.md)
  2. Copia la URL de la pestaña Raw → .env como POWERBI_PUSH_URL
  3. Ejecuta:

     export POWERBI_PUSH_URL="https://api.powerbi.com/beta/..."
     python scripts/test_powerbi_push.py

     # Solo mostrar el payload de muestra (sin enviar)
     python scripts/test_powerbi_push.py --dry-run

     # Schema mínimo (ID_Registro, Probabilidad, Fecha_Prediccion)
     python scripts/test_powerbi_push.py --schema minimal
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND.parent / ".env")
    load_dotenv(BACKEND / ".env")
except ImportError:
    pass

from integrations.powerbi_exporter import PowerBIPushClient


def print_schema_instructions(mode: str):
    schema = PowerBIPushClient.schema_definition(mode)
    print("=" * 60)
    print("📋 CAMPOS A CREAR EN POWER BI SERVICE")
    print("   Nuevo → Conjunto de datos de streaming → API")
    print("   Nombre sugerido: Predicciones_TensorFlow")
    print("=" * 60)
    print(f"{'Nombre del valor':<22} {'Tipo':<12}")
    print("-" * 34)
    for name, pbi_type in schema.items():
        print(f"{name:<22} {pbi_type:<12}")
    print()
    print("⚠️  Activa 'Análisis de datos históricos' ANTES de Crear.")
    print("   Sin eso, Power BI solo cachea en tiempo real y pierde histórico.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Test Power BI Push URL")
    parser.add_argument(
        "--schema",
        choices=["full", "minimal"],
        default=os.getenv("POWERBI_STREAMING_SCHEMA", "full"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo imprime payload de muestra, no envía",
    )
    parser.add_argument("--url", default=None, help="Override POWERBI_PUSH_URL")
    args = parser.parse_args()

    print_schema_instructions(args.schema)

    sample = PowerBIPushClient.sample_payload(args.schema)
    print("📦 Payload de muestra (debe coincidir con el de Power BI):")
    print(json.dumps(sample, indent=2, ensure_ascii=False))
    print()

    if args.dry_run:
        print("Dry-run: no se envió nada.")
        return 0

    client = PowerBIPushClient(push_url=args.url, schema_mode=args.schema)

    if not client.enabled:
        print("❌ POWERBI_PUSH_URL no configurada.")
        print()
        print("Pasos:")
        print("  1. app.powerbi.com → Área de trabajo → Nuevo")
        print("  2. Conjunto de datos de streaming → API → Siguiente")
        print("  3. Crear campos de la tabla de arriba")
        print("  4. Encender 'Análisis de datos históricos'")
        print("  5. Crear → copiar URL de la pestaña Raw")
        print('  6. export POWERBI_PUSH_URL="https://api.powerbi.com/..."')
        print("  7. python scripts/test_powerbi_push.py")
        return 1

    print(f"🚀 Enviando fila de prueba a Push URL...")
    print(f"   URL: {client.push_url[:60]}...")
    result = client.test_connection()
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    if result.get("status") == "ok":
        print()
        print("✅ Push OK (HTTP 200). La fila ya está en Predicciones_TensorFlow.")
        print("   Abre el dataset / un tile de streaming en app.powerbi.com para verla.")
        return 0

    print()
    print("❌ Push falló. Causas frecuentes:")
    print("   - Schema distinto (nombre o tipo de campo)")
    print("   - URL incompleta (usa la pestaña Raw, no cURL/PowerShell)")
    print("   - Dataset recreado → URL antigua inválida")
    return 1


if __name__ == "__main__":
    sys.exit(main())
