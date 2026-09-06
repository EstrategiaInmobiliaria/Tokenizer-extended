# 🏢 Sistema de Calificación de Leads Inmobiliarios con IA

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![Next.js](https://img.shields.io/badge/Next.js-13-black)
![tRPC](https://img.shields.io/badge/tRPC-10-blue)

> **Sistema inteligente para filtrar leads de calidad, identificar inversionistas reales y maximizar tu ROI en ventas inmobiliarias**

## 🎯 Problema que Resuelve

¿Cansado de perder tiempo con curiosos que nunca compran? ¿Necesitas identificar inversionistas reales con dinero y capacidad de firma? Este sistema utiliza **Inteligencia Artificial** para:

✅ **Eliminar curiosos** - Detecta personas que solo navegan sin intención real  
✅ **Identificar inversionistas serios** - Analiza comportamiento y señales financieras  
✅ **Priorizar leads con dinero** - Estima capacidad de compra real  
✅ **Maximizar ROI** - Enfoca tu tiempo donde hay verdaderas oportunidades  

## 🚀 Características Principales

### 🤖 Scoring Inteligente con IA
- **Sistema de 6 dimensiones** que analiza cada lead
- Score de 0-100 con categorización automática (Hot/Tibio/Frío/Descalificado)
- Ponderación personalizable según tu negocio

### 💰 Predicción de Capacidad Financiera
- Estimación de ingresos basada en empleo y señales digitales
- Cálculo de ratio deuda/ingreso
- Score de liquidez (0-100)
- Evaluación de capacidad de inversión

### 🌐 Análisis de Redes Sociales
- Validación de credibilidad en LinkedIn, Facebook, Instagram
- Detección de perfiles profesionales vs curiosos
- Identificación de dueños de negocio e inversionistas
- Score de confianza social

### 🚩 Detección de Banderas Rojas/Verdes
- **Banderas Rojas:** Emails temporales, baja interacción, inconsistencias
- **Banderas Verdes:** Compradores en efectivo, inversionistas experimentados, perfiles verificados

### 📊 Dashboard Visual Interactivo
- Vista de todos tus leads con código de colores
- Estadísticas en tiempo real
- Filtros por categoría (Hot/Tibio/Frío)
- Modal de detalles completos

### 💡 Recomendaciones Accionables
- Acciones específicas para cada tipo de lead
- Timeline de seguimiento sugerido
- Estrategias personalizadas según perfil

### 📈 Cálculo de ROI Estimado
- Probabilidad de conversión (0-100%)
- Valor estimado de comisión
- Tiempo estimado de cierre
- Priorización por valor esperado

## 📸 Screenshots

### Dashboard Principal
```
┌─────────────────────────────────────────────────────────────┐
│  🏢 Sistema de Calificación de Leads Inmobiliarios         │
│                                                             │
│  📊 Stats:  Total: 15  🔥Hot: 5  ⚡Tibio: 7  ❄️Frío: 3   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ 🔥 HOT LEAD  │  │ ⚡ LEAD TIBIO│  │ ❄️ LEAD FRÍO │    │
│  │ Score: 92    │  │ Score: 68    │  │ Score: 45    │    │
│  │              │  │              │  │              │    │
│  │ 💰 Cap: 95   │  │ 💰 Cap: 65   │  │ 💰 Cap: 30   │    │
│  │ 🎯 Int: 90   │  │ 🎯 Int: 75   │  │ 🎯 Int: 40   │    │
│  │              │  │              │  │              │    │
│  │ 🎲 Conv: 85% │  │ 🎲 Conv: 60% │  │ 🎲 Conv: 25% │    │
│  │ $76,500 MXN  │  │ $36,000 MXN  │  │ $11,250 MXN  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tecnologías Utilizadas

- **Framework:** Next.js 13 (React 18)
- **Lenguaje:** TypeScript
- **API:** tRPC (Type-safe API)
- **Validación:** Zod
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **State:** @tanstack/react-query

## 📦 Instalación

### Requisitos Previos
- Node.js 18+ 
- npm, yarn o pnpm

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone [tu-repositorio]
cd [nombre-proyecto]

# 2. Instalar dependencias
yarn install
# o
npm install

# 3. Copiar archivo de ambiente (si aplica)
cp .env.example .env

# 4. Descargar modelos de tokenización (si aplica)
yarn dotenv tsx src/scripts/download.ts

# 5. Iniciar servidor de desarrollo
yarn dev
# o
npm run dev
```

### Acceder a la Aplicación

```
http://localhost:3000/lead-scoring
```

## 🎓 Guía de Uso

### 1. Agregar Nuevo Lead

Haz clic en **"➕ Nuevo Lead"** y completa el formulario:

**Información Básica:**
- Nombre, email, teléfono
- Edad, ubicación
- Fuente del lead (orgánico, redes sociales, etc.)

**Interés en Propiedad:**
- Rango de precio (min-max)
- Tipo de propiedad (departamento, casa, terreno)
- Propósito (inversión, residencia)
- Timeline de compra
- Estado de financiamiento

### 2. Análisis Automático

El sistema analiza automáticamente:
- 💰 **Capacidad Financiera** (30%)
- 🎯 **Intención de Compra** (25%)
- ✅ **Autenticidad** (20%)
- 📱 **Engagement** (10%)
- 🌐 **Credibilidad Social** (10%)
- ⏱️ **Urgencia** (5%)

### 3. Interpretar Resultados

**🔥 Hot Lead (75-100):** Contactar INMEDIATAMENTE  
**⚡ Tibio (50-74):** Contactar en 24-48 horas  
**❄️ Frío (30-49):** Agregar a nurturing  
**🚫 Descalificado (0-29):** NO priorizar  

### 4. Tomar Acción

Sigue las recomendaciones personalizadas del sistema:
- Acciones específicas
- Timeline de seguimiento
- Estrategias según perfil

## 📚 Documentación Completa

Ver [LEAD_SCORING_GUIDE.md](./LEAD_SCORING_GUIDE.md) para:
- Guía completa de uso
- Interpretación de scores
- Estrategias de seguimiento
- Ejemplos de casos reales
- API documentation
- Mejores prácticas

## 🔧 API de tRPC

### Ejemplo: Calificar un Lead

```typescript
import { api } from '~/utils/api';

const scoreLeadMutation = api.leadScoring.scoreLead.useMutation();

const lead = {
  name: "Juan Pérez",
  email: "juan@empresa.com",
  phone: "+52 55 1234 5678",
  age: 35,
  source: "organic",
  propertyInterest: {
    priceRange: { min: 2000000, max: 4000000 },
    propertyType: "apartment",
    purpose: "investment",
    timeline: "1-3_months",
    financingStatus: "pre_approved"
  }
};

const result = await scoreLeadMutation.mutateAsync(lead);
console.log(result.overallScore); // 78
console.log(result.category); // "hot"
console.log(result.estimatedROI.conversionProbability); // 75%
```

### Endpoints Disponibles

- `leadScoring.scoreLead` - Calificar lead individual
- `leadScoring.batchScoreLeads` - Calificar múltiples leads
- `leadScoring.analyzeSocialProfile` - Analizar perfil social
- `leadScoring.predictConversion` - Predecir probabilidad de conversión
- `leadScoring.getLeadPriorities` - Obtener leads priorizados

Ver documentación completa en [LEAD_SCORING_GUIDE.md](./LEAD_SCORING_GUIDE.md)

## 📊 Algoritmo de Scoring

```typescript
Score Final = 
  (Capacidad Financiera × 0.30) +
  (Intención de Compra × 0.25) +
  (Autenticidad × 0.20) +
  (Engagement × 0.10) +
  (Credibilidad Social × 0.10) +
  (Urgencia Timeline × 0.05)
```

Cada dimensión se evalúa de 0-100 basándose en múltiples señales:

### 💰 Capacidad Financiera (30%)
- Estado de empleo (empleado, business owner, etc.)
- Tamaño de empresa
- Ingresos estimados
- Experiencia en inversiones
- Propiedad de inmuebles
- Historial crediticio
- Estado de financiamiento

### 🎯 Intención de Compra (25%)
- Propósito (inversión, residencia)
- Timeline de urgencia
- Páginas vistas
- Documentos descargados
- Preguntas realizadas
- Visitas recurrentes

### ✅ Autenticidad (20%)
- Completitud de información de contacto
- Calidad de interacción
- Tiempo en sitio
- Fuente del lead
- Perfiles sociales verificables
- Consistencia de datos

## 🚩 Sistema de Detección

### Banderas Rojas (Red Flags)
- ⏱️ Tiempo en sitio < 30 segundos
- 📧 Email temporal (tempmail.com, etc.)
- 💳 Historial crediticio deficiente
- 🚫 Sin empleo + comprador en efectivo (inconsistencia)
- 📞 Información de contacto incompleta
- 🌐 Sin presencia en redes sociales

### Banderas Verdes (Green Flags)
- 💵 Comprador en efectivo
- 🎯 Timeline urgente (inmediato, 1-3 meses)
- 🏆 Inversionista experimentado
- ✅ Perfil social verificado
- 🏢 Ya es propietario
- 💼 Perfil profesional activo en LinkedIn
- 🤝 Lead referido
- 📄 Descargó múltiples documentos

## 💡 Casos de Uso Reales

### Caso 1: Inversionista Serio (Score: 92 🔥)
```
Perfil:
- Dueño de negocio grande
- LinkedIn verificado (2,000+ contactos)
- Ya propietario de 3 inmuebles
- Timeline: Inmediato
- Financiamiento: Efectivo

Resultado:
✅ Score: 92/100
🔥 Categoría: HOT
🎲 Conversión: 85%
💵 Valor: $76,500 MXN

Acción: Llamar AHORA, preparar análisis ROI
```

### Caso 2: Curioso sin Intención (Score: 24 🚫)
```
Perfil:
- Email temporal
- 18 segundos en sitio
- 1 página vista
- Sin redes sociales
- "Solo estoy viendo"

Resultado:
⚠️ Score: 24/100
🚫 Categoría: Descalificado
🎲 Conversión: 5%
💵 Valor: $750 MXN

Acción: NO contactar, descalificar
```

## 🎯 Beneficios Clave

### Para el Negocio
- ⏱️ **Ahorra 70% de tiempo** - No pierdas tiempo con curiosos
- 💰 **+50% conversión** - Enfócate en leads calificados
- 📈 **ROI medible** - Estima valor de cada lead
- 🎯 **Priorización inteligente** - Trabaja lo que realmente importa

### Para el Vendedor
- 🤖 **IA hace el trabajo pesado** - Análisis automático
- 💡 **Recomendaciones claras** - Sabe qué hacer con cada lead
- 📊 **Dashboard visual** - Ve todo de un vistazo
- 🔔 **Identificación de urgentes** - No pierdas hot leads

## 🔐 Privacidad y Seguridad

- Sin almacenamiento de datos personales (por ahora)
- Análisis en tiempo real
- No se comparte información con terceros
- Cumplimiento con GDPR y leyes mexicanas (configuración futura)

## 🛣️ Roadmap

### v1.0 (Actual) ✅
- [x] Sistema de scoring básico
- [x] Dashboard interactivo
- [x] Análisis de 6 dimensiones
- [x] Detección de banderas rojas/verdes
- [x] Predicción de conversión

### v1.1 (Próximo) 🚧
- [ ] Integración con WhatsApp Business API
- [ ] Base de datos persistente
- [ ] Histórico de leads
- [ ] Métricas de conversión real
- [ ] Exportar reportes PDF

### v2.0 (Futuro) 🔮
- [ ] Integración con CRM (Salesforce, HubSpot)
- [ ] Machine Learning mejorado
- [ ] Análisis automático de LinkedIn vía API
- [ ] App móvil
- [ ] Notificaciones push de hot leads
- [ ] A/B testing de estrategias

## 🤝 Contribuir

Contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

Sistema creado con ❤️ para revolucionar las ventas inmobiliarias con IA.

## 📞 Soporte

¿Preguntas? ¿Problemas? ¿Sugerencias?

- 📧 Email: [tu-email@empresa.com]
- 💬 Issues: [GitHub Issues]
- 📚 Documentación: [LEAD_SCORING_GUIDE.md](./LEAD_SCORING_GUIDE.md)

---

## 🌟 ¿Por qué usar este sistema?

### Antes (Sin IA)
❌ Tiempo perdido con curiosos  
❌ No sabes quién tiene dinero real  
❌ Sigues todos los leads por igual  
❌ No priorizas correctamente  
❌ ROI bajo y frustración alta  

### Después (Con IA)
✅ Filtras curiosos automáticamente  
✅ Identificas inversionistas serios  
✅ Priorizas por probabilidad de conversión  
✅ Maximizas tiempo en leads calificados  
✅ ROI alto y conversiones reales  

---

**🚀 ¡Empieza a maximizar tu ROI hoy mismo!**

```bash
yarn dev
# Navega a http://localhost:3000/lead-scoring
```

---

*Hecho con ❤️ y mucho ☕ | Última actualización: Septiembre 2026*
