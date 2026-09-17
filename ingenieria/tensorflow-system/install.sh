#!/bin/bash

# Script de instalación del Sistema de Inteligencia TensorFlow
# Compatible con macOS y Linux

set -e

echo "================================================================"
echo "🚀 INSTALACIÓN SISTEMA DE INTELIGENCIA TENSORFLOW"
echo "================================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de log
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
log_info "Python $PYTHON_VERSION detectado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 no está instalado"
    exit 1
fi

# Crear directorio de instalación
INSTALL_DIR="$(pwd)/tensorflow-system"
log_info "Instalando en: $INSTALL_DIR"

# Instalar dependencias de Python
echo ""
echo "📦 Instalando dependencias de Python..."
cd "$INSTALL_DIR/backend"

# Crear entorno virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Entorno virtual creado"
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar requirements
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    log_info "Dependencias instaladas correctamente"
else
    log_error "Error instalando dependencias"
    exit 1
fi

# Entrenar modelos
echo ""
echo "🧠 Entrenando modelos de TensorFlow Lite..."
echo "   (Esto puede tomar 2-3 minutos)"
echo ""

python scripts/train_all_models.py

if [ $? -eq 0 ]; then
    log_info "Modelos entrenados correctamente"
else
    log_error "Error entrenando modelos"
    exit 1
fi

# Verificar que los modelos se generaron
MODELS_DIR="$INSTALL_DIR/backend/models"
EXPECTED_MODELS=(
    "real_estate_opportunity.tflite"
    "social_content_optimizer.tflite"
    "tco_calculator.tflite"
    "tennis_optimizer.tflite"
)

echo ""
echo "🔍 Verificando modelos generados..."
for model in "${EXPECTED_MODELS[@]}"; do
    if [ -f "$MODELS_DIR/$model" ]; then
        SIZE=$(du -h "$MODELS_DIR/$model" | cut -f1)
        log_info "$model ($SIZE)"
    else
        log_error "$model no encontrado"
    fi
done

# Crear script de inicio
echo ""
echo "📝 Creando scripts de inicio..."

cat > "$INSTALL_DIR/start_api.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/backend"
source venv/bin/activate
cd api
python api.py
EOF

chmod +x "$INSTALL_DIR/start_api.sh"
log_info "Script start_api.sh creado"

cat > "$INSTALL_DIR/run_examples.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source backend/venv/bin/activate
python examples/usage_examples.py
EOF

chmod +x "$INSTALL_DIR/run_examples.sh"
log_info "Script run_examples.sh creado"

# Información de n8n
echo ""
echo "================================================================"
echo "📋 INSTALACIÓN COMPLETADA"
echo "================================================================"
echo ""
echo "🚀 Para iniciar el sistema:"
echo ""
echo "   1. Iniciar API:"
echo "      cd $INSTALL_DIR"
echo "      ./start_api.sh"
echo ""
echo "   2. Ejecutar ejemplos (en otra terminal):"
echo "      cd $INSTALL_DIR"
echo "      ./run_examples.sh"
echo ""
echo "📊 Endpoints disponibles:"
echo "   - API: http://localhost:3001"
echo "   - Docs: http://localhost:3001/docs"
echo "   - Health: http://localhost:3001/health"
echo ""
echo "🔌 Integraciones:"
echo "   1. n8n workflows: $INSTALL_DIR/workflows/"
echo "      - instagram_collector.json"
echo "      - real_estate_scanner.json"
echo ""
echo "   2. Plugin Obsidian: $INSTALL_DIR/obsidian-plugin/"
echo "      Copiar a: .obsidian/plugins/tensorflow-intelligence-sync/"
echo ""
echo "   3. Power BI: Conectar a http://localhost:3001/api/integrations/powerbi-data"
echo ""
echo "📚 Documentación completa: $INSTALL_DIR/README.md"
echo ""
echo "================================================================"
echo "✅ Sistema listo para producción"
echo "================================================================"
