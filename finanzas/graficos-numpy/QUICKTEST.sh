#!/bin/bash
# Quick Test Script - Prueba rápida del entorno

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Prueba Rápida del Entorno NumPy + Matplotlib                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar entorno
echo "📋 Paso 1/4: Verificando entorno..."
python3 verificar_entorno.py
if [ $? -eq 0 ]; then
    echo "✅ Verificación exitosa"
else
    echo "❌ Error en verificación"
    exit 1
fi

echo ""
echo "📊 Paso 2/4: Generando gráfico básico..."
python3 test_plot.py
if [ $? -eq 0 ]; then
    echo "✅ Gráfico básico generado"
else
    echo "❌ Error en gráfico básico"
    exit 1
fi

echo ""
echo "📈 Paso 3/4: Generando ejemplos intermedios..."
python3 ejemplos_graficos.py
if [ $? -eq 0 ]; then
    echo "✅ Ejemplos intermedios generados"
else
    echo "❌ Error en ejemplos intermedios"
    exit 1
fi

echo ""
echo "🎯 Paso 4/4: Generando análisis avanzados..."
python3 ejemplos_avanzados.py
if [ $? -eq 0 ]; then
    echo "✅ Análisis avanzados generados"
else
    echo "❌ Error en análisis avanzados"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ PRUEBA COMPLETADA EXITOSAMENTE                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Gráficos generados:"
ls -lh *.png 2>/dev/null | tail -11 | awk '{printf "   • %-35s %s\n", $9, $5}'
echo ""
echo "🎓 Próximos pasos:"
echo "   1. Revisa los archivos PNG generados"
echo "   2. Lee INDEX.md para navegación completa"
echo "   3. Estudia los scripts .py para aprender"
echo "   4. Personaliza con tus propios datos"
echo ""
