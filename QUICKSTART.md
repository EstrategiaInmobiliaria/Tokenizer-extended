# 🚀 Inicio Rápido - Sistema de Calificación de Leads con IA

## ⚡ Instalación en 3 Pasos

### 1️⃣ Instalar Dependencias
```bash
yarn install
```

### 2️⃣ Iniciar Servidor de Desarrollo
```bash
yarn dev
```

### 3️⃣ Abrir Dashboard
```
http://localhost:3000/lead-scoring
```

## 🎮 Demo Rápido

Ejecuta el script de demostración para ver el sistema en acción:

```bash
npx tsx scripts/demo.ts
```

Esto analizará varios leads de ejemplo y mostrará:
- Scores detallados
- Categorización automática
- Banderas rojas y verdes
- Recomendaciones
- Análisis financiero
- ROI estimado

## 📝 Uso Básico

### 1. Agregar un Lead

Haz clic en "➕ Nuevo Lead" y completa:

**Mínimo requerido:**
- Nombre
- Email
- Rango de precio
- Tipo de propiedad
- Timeline

**Opcional pero recomendado:**
- Teléfono
- Edad
- Perfiles sociales
- Información financiera
- Comportamiento en sitio

### 2. Ver Resultados

El sistema analiza automáticamente y muestra:

- **Score general** (0-100)
- **Categoría:**
  - 🔥 Hot (75-100) - ¡Contactar YA!
  - ⚡ Tibio (50-74) - Seguimiento en 24-48h
  - ❄️ Frío (30-49) - Campaña nurturing
  - 🚫 Descalificado (0-29) - NO priorizar

- **Probabilidad de conversión** (%)
- **Valor estimado de comisión** (MXN)
- **Recomendaciones accionables**

### 3. Tomar Acción

Sigue las recomendaciones del sistema:

**Para Hot Leads (🔥):**
```
✅ Llamar por teléfono AHORA
✅ Preparar propuesta personalizada
✅ Agendar visita en 24-48 horas
✅ Asignar a tu mejor vendedor
```

**Para Tibios (⚡):**
```
📧 Email con catálogo personalizado
📱 WhatsApp con información
📋 Seguimiento cada 3-5 días
```

**Para Fríos (❄️):**
```
📨 Agregar a campaña de email
📚 Contenido educativo
⏳ Seguimiento mensual
```

**Para Descalificados (🚫):**
```
⛔ NO contactar
🗑️ Descalificar de lista activa
```

## 🎯 Ejemplo Rápido

### Lead Ejemplo: Inversionista Serio

```javascript
{
  name: "Carlos Empresario",
  email: "carlos@empresa.com",
  phone: "+52 55 1234 5678",
  age: 42,
  source: "referral",
  
  propertyInterest: {
    priceRange: { min: 3000000, max: 5000000 },
    propertyType: "apartment",
    purpose: "investment",
    timeline: "immediate",
    financingStatus: "cash_buyer"
  },
  
  financialSignals: {
    employmentStatus: "business_owner",
    companySize: "large",
    estimatedIncome: "very_high",
    investmentExperience: true,
    propertyOwnership: true,
    creditScore: "excellent"
  }
}
```

**Resultado:**
```
🔥 HOT LEAD
Score: 92/100
Probabilidad Conversión: 85%
Valor Estimado: $76,500 MXN
Acción: ☎️ CONTACTAR INMEDIATAMENTE
```

## 📊 Métricas Clave

El dashboard muestra:

- **Total de leads** analizados
- **Distribución** por categoría
- **Score promedio** de tu pipeline
- **Valor total estimado** en comisiones

Usa estas métricas para:
- Priorizar tu tiempo
- Medir calidad de fuentes
- Optimizar tus campañas
- Proyectar ingresos

## 🔍 Cómo Funciona

### 1. Análisis Multi-Dimensional (6 factores)

**💰 Capacidad Financiera (30%)**
- Empleo y tamaño de empresa
- Ingresos estimados
- Historial crediticio
- Experiencia en inversiones

**🎯 Intención de Compra (25%)**
- Propósito (inversión vs residencia)
- Timeline de urgencia
- Comportamiento en sitio
- Documentos descargados

**✅ Autenticidad (20%)**
- Completitud de información
- Calidad de interacción
- Fuente del lead
- Consistencia de datos

**📱 Engagement (10%)**
- Páginas vistas
- Tiempo en sitio
- Videos vistos
- Visitas recurrentes

**🌐 Credibilidad Social (10%)**
- Perfiles verificados
- Presencia en LinkedIn
- Actividad profesional

**⏱️ Urgencia (5%)**
- Timeline de compra
- Disponibilidad

### 2. Detección Automática

**🚩 Banderas Rojas:**
- Email temporal
- Bajo engagement (< 30 seg)
- Inconsistencias
- Sin contacto

**✅ Banderas Verdes:**
- Cash buyer
- Timeline urgente
- Inversionista experimentado
- Perfil verificado

### 3. Recomendaciones

El sistema genera recomendaciones específicas:
- Qué hacer
- Cuándo hacerlo
- Cómo priorizar
- Qué evitar

## 💡 Tips para Mejores Resultados

### ✅ DO (Hacer)

1. **Captura toda la información posible**
   - Más datos = score más preciso
   - Busca perfiles sociales
   - Pregunta por situación financiera

2. **Actualiza información regularmente**
   - Después de cada contacto
   - Cuando cambie el timeline
   - Si mejora la calificación

3. **Prioriza Hot Leads**
   - Responde en < 2 horas
   - Asigna a tus mejores
   - Dale seguimiento diario

4. **Usa los filtros**
   - Ver solo Hot cuando estés ocupado
   - Revisar Tibios al final del día
   - Fríos una vez por semana

### ❌ DON'T (No Hacer)

1. **No ignores las banderas rojas**
   - Sistema detecta señales
   - Ahorra tu tiempo
   - Enfócate en calificados

2. **No trates todos igual**
   - Hot = urgente
   - Frío = puede esperar
   - Descalificado = skip

3. **No olvides seguimiento**
   - Hot: cada 1-2 días
   - Tibio: cada 3-5 días
   - Frío: cada 2 semanas

## 🆘 Problemas Comunes

### "No veo el dashboard"
```bash
# Asegúrate de estar en la ruta correcta:
http://localhost:3000/lead-scoring
# No solo: http://localhost:3000
```

### "El build falla"
```bash
# Reinstalar dependencias:
rm -rf node_modules
yarn install
```

### "TypeScript errors"
```bash
# Verificar tipos:
npx tsc --noEmit
```

## 📚 Más Información

- **Guía Completa:** [LEAD_SCORING_GUIDE.md](./LEAD_SCORING_GUIDE.md)
- **Documentación:** [README.md](./README.md)
- **Ejemplos de Código:** [examples/lead-examples.ts](./examples/lead-examples.ts)

## 🚀 Próximos Pasos

1. ✅ Completar quickstart
2. 📖 Leer guía completa
3. 🧪 Probar con tus leads reales
4. 📊 Revisar métricas
5. 🎯 Optimizar tu proceso

---

**¡Listo para maximizar tu ROI! 🎉**

¿Preguntas? Ver [LEAD_SCORING_GUIDE.md](./LEAD_SCORING_GUIDE.md) para más detalles.
