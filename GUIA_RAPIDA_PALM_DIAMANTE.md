# Guía Rápida de Uso - Palm Diamante Calculator

## 🚀 Inicio Rápido

### 1. Levantar el servidor de desarrollo

```bash
cd /workspace
yarn install  # Si es primera vez
yarn dev
```

Abre tu navegador en: `http://localhost:3000/palm-diamante`

---

## 🎯 Flujo de Trabajo Recomendado

### Para Jaime Wilk (41k contactos)

1. **Graba los 3 videos de 15 segundos**
   - Usa los guiones exactos de la "Biblioteca de Marketing"
   - Sube a @palm.diamante en Instagram/TikTok
   - CTA: "Link en bio para calcular tu inversión"

2. **Configura el link en bio**
   - Apunta a: `tudominio.com/palm-diamante`
   - El usuario entra directo a la calculadora

3. **Leads que llegan:**
   - Usan la calculadora para ver su mensualidad
   - Completan el formulario de 3 preguntas
   - Si están calificados (3 SÍ) → **te llega notificación a WhatsApp**
   - Si NO calificados → entran a nurturing automático

### Para Diana Ondarza (Gestión de inventario)

1. **Actualizar inventario disponible**
   - Edita el archivo: `src/data/inventory.ts`
   - Cambia el `status` de unidades vendidas/apartadas

2. **Exportar para EasyBroker**
   - Entra a `/palm-diamante`
   - Click en "Exportar a Excel/CSV"
   - Sube el CSV a EasyBroker

3. **Marcar unidades apartadas**
   - Cuando un lead pague $25k
   - Busca la unidad por ID en `inventory.ts`
   - Cambia `status: "disponible"` a `status: "apartado"`

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Lead de Instagram que ve Video 1

**Flujo:**
1. Ve video de Jaime sobre "$25k aparta"
2. Click en link bio → calculadora
3. Selecciona "B1 Entry" (76m²)
4. Ve que necesita:
   - $25k aparta
   - $353k firma (solo $328k adicional)
   - $27k/mes por 24 meses
   - $4M con crédito hipotecario

5. Completa formulario:
   - ✅ Sí tiene $353k
   - ✅ Sí puede pagar $27k/mes
   - ✅ Sí quiere pre-aprobación (tiene RFC)

6. **LEAD CALIFICADO** → Recibe mensaje:
   > "✅ Lead calificado! Te contactaremos por WhatsApp."

7. Jaime recibe notificación y manda corrida financiera personalizada

### Ejemplo 2: Lead curioso que NO califica

**Flujo:**
1. Entra por Meta Ads
2. Ve calculadora de "Garden House" $9.8M
3. Completa formulario:
   - ❌ NO tiene $689k para firma
   - ❌ NO puede pagar $53k/mes
   - ❌ NO quiere crédito hipotecario

4. **LEAD NO CALIFICADO** → Recibe:
   > "📧 Gracias. Te enviaremos información a tu email para nurturing."

5. Entra a campaña de email educativo:
   - Email 1: "Cómo funciona el crédito hipotecario en preventa"
   - Email 2: "Comparativa Torre I vs II vs III"
   - Email 3: "Testimonios de inversionistas"

---

## 🔥 Casos de Éxito Esperados

### Torre III: El Volumen Real

**Perfil del inversionista ideal:**
- Tiene $353k-$441k para firma (B1 o A1)
- Puede pagar $27k-$34k mensuales
- Quiere **24 meses** de plazo (vs 5 o 9 de otras torres)
- Entiende que el 80% lo pone el banco

**Por qué funciona Torre III:**
- Mensualidad más baja que Torre I y II
- Más tiempo para organizar el crédito hipotecario
- 150 unidades = más opciones de piso/vista
- Entrega más lejana = más tiempo de plusvalía

### Garden House: El ROI King

**Perfil del inversionista ROI:**
- Tiene $689k para firma
- Puede pagar $53k/mes
- **Renta vacacional: $95k/mes en temporada**
- ROI anual: ~82% sobre inversión inicial

**Pitch de Jaime + Diana:**
> "Inviertes $689k hoy + $53k/mes por 24 meses. Rentas en $95k/mes 6 meses del año. Eso es $570k al año de ingreso sobre $689k inicial = 82% ROI. El banco pone el resto."

---

## 💻 Estructura Técnica

### Archivos Clave

```
src/
├── types/palm-diamante.ts          # Tipos TypeScript
├── utils/payment-calculator.ts     # Lógica de cálculos
├── data/inventory.ts               # Base de datos de unidades
├── components/
│   ├── PalmDiamanteCalculator.tsx  # Calculadora interactiva
│   ├── LeadQualificationForm.tsx   # Formulario 3 preguntas
│   ├── InventoryTable.tsx          # Tabla con filtros + export
│   └── VideoScriptsLibrary.tsx     # Scripts y templates
└── pages/
    ├── palm-diamante.tsx           # Página principal
    └── index.tsx                   # Home con banner
```

### Agregar Nuevas Unidades

Edita `src/data/inventory.ts`:

```typescript
{
  id: "IIIA-B1-110",              // ID único
  torre: "III-A",                 // Torre I-A, I-B, II-A, II-B, III-A, III-B
  model: "B1",                    // B1, A1, A2, Roof Garden, Garden House, Penthouse
  metrosCuadrados: 76.04,
  precioTotal: 5043733,
  status: "disponible",           // disponible, vendido, reservado, apartado
  nivel: 5,                       // Número de piso
  numeroUnidad: "510",            // Número de unidad
}
```

### Cambiar Precios Base

Edita `src/data/inventory.ts` en `MODEL_PRICING`:

```typescript
export const MODEL_PRICING = {
  B1: {
    metrosCuadrados: 76.04,
    precioBase: 5043733,          // Cambia aquí
    descripcion: "Entrada - Ideal para primer inversionista",
  },
  // ...
}
```

---

## 📊 Dashboard de Métricas (Próximamente)

### Métricas que rastrear manualmente (por ahora):

1. **Leads por fuente:**
   - Instagram: ___
   - TikTok: ___
   - Meta Ads: ___
   - Referidos: ___
   - Base de datos 41k: ___

2. **Tasa de calificación:**
   - Total leads: ___
   - Completaron formulario: ___
   - Calificados (3 SÍ): ___
   - No calificados: ___

3. **Conversión por torre:**
   - Torre I: ___
   - Torre II: ___
   - Torre III: ___

4. **Conversión a aparta ($25k):**
   - Leads calificados: ___
   - Agendaron llamada: ___
   - Pagaron $25k: ___

---

## 🎬 Video Tutoriales (Grabar)

### Para el Equipo

1. **Tutorial 1: Cómo usar la calculadora** (3 min)
   - Mostrar cómo seleccionar modelo
   - Explicar cada línea del desglose
   - Destacar inversión inicial vs precio total

2. **Tutorial 2: Calificar un lead** (2 min)
   - Explicar las 3 preguntas
   - Qué hacer si dice SÍ (WhatsApp)
   - Qué hacer si dice NO (nurturing)

3. **Tutorial 3: Exportar inventario** (1 min)
   - Click en "Exportar CSV"
   - Importar en EasyBroker

### Para los Leads (Contenido educativo)

1. **¿Cómo funciona la estructura de $25k aparta?** (5 min)
2. **Torre I vs Torre II vs Torre III: ¿Cuál elegir?** (4 min)
3. **Crédito hipotecario en preventa: Todo lo que necesitas saber** (6 min)
4. **ROI de renta vacacional en Diamante** (5 min)

---

## 🚧 Troubleshooting

### Problema: La calculadora no muestra mensualidades

**Solución:** Verifica que `TORRE_FINANCING_MONTHS` en `src/types/palm-diamante.ts` tenga los meses correctos:

```typescript
export const TORRE_FINANCING_MONTHS: Record<TorreType, number> = {
  "I-A": 5,
  "I-B": 5,
  "II-A": 9,
  "II-B": 9,
  "III-A": 24,
  "III-B": 24,
};
```

### Problema: El CSV no descarga

**Solución:** Asegúrate de tener unidades en `SAMPLE_UNITS` en `src/data/inventory.ts`

### Problema: El formulario no envía

**Solución:** Por ahora solo muestra un `alert()`. Necesitas conectar con tu backend/CRM. Ver sección "Próximos Pasos" en README principal.

---

## ✅ Checklist Pre-Lanzamiento

- [ ] Grabar 3 videos de 15 seg
- [ ] Subir videos a @palm.diamante
- [ ] Configurar link en bio → `/palm-diamante`
- [ ] Probar calculadora en todos los modelos
- [ ] Probar formulario con ambos flujos (SÍ y NO)
- [ ] Exportar CSV de prueba
- [ ] Configurar notificaciones de WhatsApp para leads calificados
- [ ] Crear campaña de email nurturing (3-5 emails)
- [ ] Preparar template de corrida financiera personalizada
- [ ] Coordinar con Diana para actualizar inventario semanal

---

## 📞 Soporte

**Dudas técnicas:** [Tu contacto aquí]
**Dudas de inventario:** Diana Ondarza
**Dudas de estrategia:** Jaime Wilk

---

**¡Éxito con Palm Diamante! 🏢🚀**
