#!/bin/bash
# Script de prueba del bootloader

set -e

echo "========================================="
echo "  Verificación del Bootloader"
echo "========================================="
echo ""

# Verificar que existe
if [ ! -f boot.bin ]; then
    echo "❌ boot.bin no existe. Compila primero con: make"
    exit 1
fi

# Verificar tamaño
SIZE=$(stat -c%s boot.bin 2>/dev/null || stat -f%z boot.bin 2>/dev/null)
if [ "$SIZE" -eq 512 ]; then
    echo "✓ Tamaño correcto: 512 bytes"
else
    echo "❌ Tamaño incorrecto: $SIZE bytes (esperado 512)"
    exit 1
fi

# Verificar firma mágica 0x55AA (little-endian)
MAGIC=$(tail -c 2 boot.bin | od -An -tx1 | tr -d ' \n')
if [ "$MAGIC" = "55aa" ] || [ "$MAGIC" = "aa55" ]; then
    echo "✓ Firma mágica presente: 0x55AA"
else
    echo "❌ Firma mágica incorrecta: 0x$MAGIC (esperado 0x55AA)"
    exit 1
fi

# Mostrar primeros bytes
echo ""
echo "Primeros 32 bytes (código de inicio):"
hexdump -C boot.bin | head -3

echo ""
echo "Últimos 16 bytes (incluye firma mágica):"
hexdump -C boot.bin | tail -2

echo ""
echo "========================================="
echo "✓ Bootloader válido y listo para ejecutar"
echo "========================================="
echo ""
echo "Para probarlo:"
echo "  make run"
echo ""
echo "Nota: Necesitas QEMU instalado:"
echo "  sudo apt install qemu-system-x86"
