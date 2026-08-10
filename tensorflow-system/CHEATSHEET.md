# 📋 Cheat Sheet - Comandos Rápidos

## 🚀 Instalación

```bash
# Instalación completa (incluye entrenamiento)
cd tensorflow-system
./install.sh

# Verificar instalación
python verify_installation.py
```

## 🔧 Desarrollo

```bash
# Activar entorno virtual
cd backend
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de test
pip install -r tests/requirements.txt
```

## 🏋️  Entrenamiento

```bash
# Entrenar todos los modelos
cd backend
python scripts/train_all_models.py

# Entrenar modelo específico
python models/real_estate_opportunity.py
python models/social_media_optimizer.py
python models/personal_decision_models.py
```

## 🌐 API

```bash
# Iniciar API (producción)
cd tensorflow-system
./start_api.sh

# O manual
cd backend
source venv/bin/activate
cd api
python api.py

# API estará en: http://localhost:3001
# Docs en: http://localhost:3001/docs
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
cd backend
pytest tests/ -v

# Con coverage
pytest tests/ --cov=backend --cov-report=html

# Test específico
pytest tests/test_system.py::TestRealEstateAPI -v

# Solo tests de API
pytest tests/test_system.py::TestAPI -v
```

## 🐳 Docker

```bash
# Levantar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f tensorflow-api

# Detener
docker-compose down

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

## 🔌 Uso de API

### Inmobiliario

```bash
# Predecir oportunidad
curl -X POST http://localhost:3001/api/predict/real-estate \
  -H "Content-Type: application/json" \
  -d '{
    "precio_m2": 45000,
    "ubicacion": "Querétaro",
    "amenidades": 12,
    "velocidad_ventas": 0.85,
    "cap_rate": 7.2
  }'

# Análisis batch
curl -X POST http://localhost:3001/api/analyze/real-estate-batch \
  -H "Content-Type: application/json" \
  -d '[
    {"precio_m2": 45000, "ubicacion": "Querétaro", ...},
    {"precio_m2": 52000, "ubicacion": "CDMX", ...}
  ]'
```

### Redes Sociales

```bash
# Predecir post
curl -X POST http://localhost:3001/api/predict/social-media-post \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_contenido": "Reel",
    "hora": 9,
    "dia_semana": 1,
    "num_hashtags": 5,
    "tema_categoria": "Cap Rate",
    "longitud_caption": 150
  }'

# Calendario semanal
curl -X POST http://localhost:3001/api/generate/weekly-content-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "temas_disponibles": ["Cap Rate", "Estrategia Inmobiliaria", "ExO"]
  }'
```

### Personal

```bash
# Calcular TCO
curl -X POST http://localhost:3001/api/calculate/tco \
  -H "Content-Type: application/json" \
  -d '{
    "precio_inicial": 650000,
    "gasolina_mensual": 800,
    "seguro_anual": 12000,
    "mantenimiento_anual": 8000,
    "depreciacion_anual": 65000,
    "km_anuales": 20000,
    "rendimiento_km_l": 25,
    "es_electrico": 1
  }'

# Comparar vehículos
curl -X POST http://localhost:3001/api/compare/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle1": {...},
    "vehicle2": {...},
    "vehicle1_name": "Geely",
    "vehicle2_name": "RAV4"
  }'

# Optimizar tenis
curl -X POST http://localhost:3001/api/optimize/tennis-setup \
  -H "Content-Type: application/json" \
  -d '{
    "temperatura": 24,
    "rival_nivel": 6,
    "dia_semana": 1,
    "horas_descanso": 2
  }'
```

### Integraciones

```bash
# Health check
curl http://localhost:3001/health

# Reporte WhatsApp
curl -X POST "http://localhost:3001/api/integrations/whatsapp-report?tipo=inmobiliario"

# Datos Power BI (JSON / Get Data → Web)
curl http://localhost:3001/api/integrations/powerbi-data

# Estado integración Power BI (SQL + Push)
curl http://localhost:3001/api/integrations/powerbi/status

# Exportar predicciones → SQL (+ Push si hay POWERBI_PUSH_URL)
curl -X POST "http://localhost:3001/api/integrations/powerbi/export?source=live&write_mode=append"

# Script orquestador (recomendado en cron / GitHub Actions)
cd backend && python scripts/export_to_powerbi.py --source live --mode hybrid

# Postgres local (Docker)
docker-compose up -d postgres
export DATABASE_URL="postgresql+psycopg2://tensorflow:tensorflow@localhost:5432/tensorflow_bi"
```

## 📊 Datos

```bash
# Ver estructura de datos
cat backend/data/README.md

# Agregar datos manualmente
echo "nuevo_desarrollo,48000,CDMX,14,0.78,6.9,1,22500000,178" >> \
  backend/data/real_estate/training_data.csv

# Backup de datos
tar -czf data_backup_$(date +%Y%m%d).tar.gz backend/data/

# Restaurar backup
tar -xzf data_backup_20240810.tar.gz
```

## 🔄 Re-entrenamiento

```bash
# Re-entrenar con nuevos datos
cd backend
python scripts/train_all_models.py

# Verificar modelos generados
ls -lh models/*.tflite

# Ver tamaño de modelos
du -sh models/*.tflite
```

## 📝 Obsidian Plugin

```bash
# Instalar plugin
cp -r obsidian-plugin ~/.obsidian/plugins/tensorflow-intelligence-sync/

# Compilar (si modificas)
cd obsidian-plugin
npm install
npm run build
```

## 🤖 n8n

```bash
# Instalar n8n
npm install -g n8n

# Iniciar n8n
n8n start

# Importar workflow
# 1. Ir a http://localhost:5678
# 2. Workflows → Import from File
# 3. Seleccionar workflows/instagram_collector.json
```

## 📈 Monitoreo

```bash
# Ver logs de API
tail -f backend/logs/tensorflow-api.log

# Ver métricas en tiempo real
watch -n 1 'curl -s http://localhost:3001/health | jq'

# Monitorear uso de CPU/RAM
top -p $(pgrep -f "python api.py")
```

## 🐛 Debugging

```bash
# Verificar puerto en uso
lsof -i :3001

# Matar proceso en puerto
kill -9 $(lsof -t -i:3001)

# Ver logs Docker
docker-compose logs -f --tail=100

# Entrar al container
docker exec -it tensorflow-api bash

# Python REPL con modelos
cd backend
python
>>> from models.real_estate_opportunity import RealEstateOpportunityDetector
>>> detector = RealEstateOpportunityDetector()
>>> detector.predict({...})
```

## 🗑️  Limpieza

```bash
# Limpiar cache Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Limpiar logs
rm -rf backend/logs/*.log

# Limpiar modelos entrenados (cuidado!)
rm -rf backend/models/*.tflite
rm -rf backend/models/*.pkl

# Limpiar Docker
docker-compose down -v
docker system prune -a
```

## 🔐 Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar variables
nano .env

# Cargar variables en shell
source .env
export $(cat .env | xargs)
```

## 📦 Deployment

```bash
# Build Docker image
docker build -t tensorflow-intelligence:latest backend/

# Tag para registry
docker tag tensorflow-intelligence:latest myregistry/tensorflow-intelligence:v1.0

# Push a registry
docker push myregistry/tensorflow-intelligence:v1.0

# Deploy en servidor
scp -r tensorflow-system/ user@server:/opt/
ssh user@server "cd /opt/tensorflow-system && ./install.sh"
```

## 🎯 Ejemplos Rápidos

```bash
# Tour visual
cd tensorflow-system
python WELCOME.py

# Ejecutar ejemplos
./run_examples.sh

# Ejemplo específico en Python
cd backend
python << EOF
from models.real_estate_opportunity import RealEstateOpportunityDetector
detector = RealEstateOpportunityDetector()
result = detector.predict({
    'precio_m2': 45000,
    'ubicacion': 'Querétaro',
    'amenidades': 12,
    'velocidad_ventas': 0.85,
    'cap_rate': 7.2
})
print(f"Probabilidad: {result['certeza']}")
print(f"Precio: ${result['precio_estimado']:,.0f}")
EOF
```

## 📚 Documentación

```bash
# Ver README
cat README.md | less

# Ver Quick Start
cat QUICKSTART.md | less

# Ver arquitectura
cat ARCHITECTURE.md | less

# Ver resumen ejecutivo
cat SUMMARY.md | less

# Abrir docs en browser
open http://localhost:3001/docs  # macOS
xdg-open http://localhost:3001/docs  # Linux
```

## 🔍 Búsqueda

```bash
# Buscar en código
grep -r "real_estate" backend/

# Buscar en logs
grep "ERROR" backend/logs/tensorflow-api.log

# Buscar modelos
find backend/models -name "*.tflite"

# Contar líneas de código
find tensorflow-system -name "*.py" -exec wc -l {} + | tail -1
```

## 🚑 Troubleshooting Rápido

```bash
# API no responde
curl http://localhost:3001/health
# Si falla: revisar logs o reiniciar

# Modelos no existen
python backend/scripts/train_all_models.py

# Error de imports
cd backend && source venv/bin/activate
pip install -r requirements.txt

# Port already in use
lsof -i :3001
kill -9 <PID>

# Permission denied
chmod +x install.sh
chmod +x start_api.sh
chmod +x verify_installation.py
```

## 🎓 Comandos Avanzados

```bash
# Benchmark de modelos
cd backend
python << EOF
import time
from models.real_estate_opportunity import RealEstateOpportunityDetector

detector = RealEstateOpportunityDetector()
test_data = {'precio_m2': 45000, 'ubicacion': 'Querétaro', ...}

times = []
for i in range(1000):
    start = time.time()
    detector.predict(test_data)
    times.append(time.time() - start)

print(f"Avg: {sum(times)/len(times)*1000:.2f}ms")
print(f"P95: {sorted(times)[int(len(times)*0.95)]*1000:.2f}ms")
EOF

# Exportar modelo a otro formato
python << EOF
import tensorflow as tf
model = tf.keras.models.load_model('backend/models/real_estate_opportunity.h5')
model.save('backend/models/real_estate_savedmodel', save_format='tf')
EOF
```

---

## 📞 Ayuda Rápida

```bash
# Sistema completo
./install.sh && ./start_api.sh

# Verificar todo funciona
python verify_installation.py

# Ejecutar ejemplos
./run_examples.sh

# Ver documentación
cat SUMMARY.md
```

---

**Tip**: Guarda este archivo como referencia rápida. Todos estos comandos son funcionales después de ejecutar `./install.sh`.
