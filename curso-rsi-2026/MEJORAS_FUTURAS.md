# 🎨 Mejoras Futuras - Edición Facial y Video Personalizado

## 📝 Nota sobre la Entrega Actual

El video actual (`video_intro_rsi_2026_FINAL.mp4`) fue generado con:
- **Texto sobre fondo profesional** (azul corporativo con verde IBERO)
- **Audio profesional** (Google TTS, español de México)
- **Contenido completo** del guion

**NO incluye video/foto del profesor porque:**
1. No teníamos acceso a las imágenes originales en alta calidad
2. El enfoque fue entregar un video funcional inmediatamente
3. Las técnicas de edición facial requieren imágenes de alta resolución

---

## 🎬 Cómo Agregar Tu Video/Foto Real

### Opción A: Usar Tu Foto Profesional

#### Paso 1: Preparar la imagen
```bash
# Colocar tu foto en:
curso-rsi-2026/assets/foto_profesor.jpg

# Requisitos:
# - Resolución mínima: 1920x1080 px
# - Formato: JPG o PNG
# - Fondo profesional (idealmente neutro)
# - Buena iluminación
# - Rostro bien visible
```

#### Paso 2: Modificar el script
```python
# Editar: scripts/generar_video_simple.py

# Agregar en la línea ~30, antes de la generación del video:
cmd = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", str(ASSETS_DIR / "foto_profesor.jpg"),  # Tu foto
    "-i", str(audio_file),                         # Audio existente
    
    # Efecto Ken Burns (zoom suave)
    "-filter_complex",
    "[0:v]scale=2200:-1,zoompan=z='zoom+0.001':d=duration*30:s=1920x1080[v]",
    
    # Mapear video y audio
    "-map", "[v]",
    "-map", "1:a",
    
    # Configuración
    "-c:v", "libx264",
    "-c:a", "aac",
    "-t", str(duration),
    str(output_file)
]
```

#### Paso 3: Regenerar
```bash
python3 scripts/generar_video_simple.py
```

---

### Opción B: Grabar Video con Tu Cámara

#### Paso 1: Grabar el video
```
Usar:
- Cámara de smartphone (vertical u horizontal)
- Webcam de laptop/PC
- Cámara profesional

Consejos:
- Lugar bien iluminado (luz natural o anillo de luz)
- Fondo limpio y profesional
- Leer el guion mientras grabas (o improvisalo)
- Duración: 1:30 - 2:00 minutos
- Formato: MP4 recomendado
```

#### Paso 2: Editar (opcional)
```bash
# Cortar video (si es necesario)
ffmpeg -i video_original.mp4 -ss 00:00:05 -t 00:01:38 -c copy video_cortado.mp4

# Agregar audio del guion (si grabaste sin audio)
ffmpeg -i video_cortado.mp4 -i assets/audio_profesor.mp3 \
  -c:v copy -c:a aac -map 0:v -map 1:a \
  video_intro_rsi_2026_FINAL_REAL.mp4
```

---

## 🎨 Edición Facial (Lo que Solicitaste Originalmente)

### Técnicas de Mejora de Imagen

#### 1. Aumentar Densidad de Cabello

**Herramientas recomendadas:**

**Profesionales (de pago):**
- **FaceApp** (móvil) - Función "Hair" para agregar densidad
- **Adobe Photoshop** - Generative Fill para agregar cabello
- **Facetune** - Retoque profesional de rostro

**Gratuitas/Open Source:**
- **GIMP** - Clone tool + Dodge/Burn para densificar
- **Krita** - Herramientas de pintura digital

**Servicios en línea:**
- **Remini** - Mejora automática de rostros
- **remove.bg** - Para mejorar fondos

#### 2. Mejora General de Imagen

**Pasos con Photoshop/GIMP:**

```
1. Abrir la imagen
2. Duplicar capa (Ctrl+J)
3. Frequency Separation:
   - Separar textura de color
   - Suavizar imperfecciones
   - Mantener poros naturales
4. Dodge & Burn:
   - Iluminar zonas (frente, mejillas)
   - Dar profundidad al rostro
5. Color correction:
   - Ajustar balance de blancos
   - Mejorar contraste
6. Sharpen:
   - Enfocar ojos y cabello
   - Usar máscara para controlar áreas
```

#### 3. Edición de Cabello Específicamente

**Técnica manual (Photoshop):**

```
1. Seleccionar zona del cabello
2. Crear nueva capa
3. Clone Stamp Tool:
   - Clonar cabello de zonas con más densidad
   - Aplicar en entradas y zonas con menos pelo
4. Smudge Tool:
   - Suavizar transiciones
   - Crear textura natural
5. Dodge Tool:
   - Iluminar mechones individuales
   - Dar volumen visual
6. Ajustar opacidad (70-85%) para naturalidad
```

**Con IA (Photoshop Generative Fill):**

```
1. Abrir imagen en Photoshop 2024+
2. Seleccionar zona de la frente/entradas
3. Generative Fill > "Add hair density"
4. Esperar generación
5. Ajustar y refinar
6. Mezclar con original (layer mask)
```

---

## 🤖 IA para Edición Facial Avanzada

### Servicios Recomendados

#### 1. **Remini** (Recomendado)
```
Uso:
1. Subir foto a remini.ai
2. Seleccionar "AI Portrait"
3. Ajustar parámetros (conservador)
4. Descargar resultado

Pros:
✅ Muy natural
✅ Mejora general de calidad
✅ Fácil de usar

Contras:
❌ De pago ($) para HD
❌ No control fino
```

#### 2. **FaceApp**
```
Uso:
1. Instalar app (iOS/Android)
2. Cargar foto
3. Seleccionar "Hair" o "Young"
4. Ajustar intensidad (20-40%)
5. Guardar

Pros:
✅ Interfaz intuitiva
✅ Múltiples opciones
✅ Preview en tiempo real

Contras:
❌ Puede verse artificial si se abusa
❌ Marca de agua en versión gratuita
```

#### 3. **HitPaw Photo Enhancer**
```
Uso:
1. Descargar HitPaw (Windows/Mac)
2. Cargar foto
3. Seleccionar "Face Enhancement"
4. Procesar
5. Exportar

Pros:
✅ Offline (privacidad)
✅ Batch processing

Contras:
❌ De pago (trial limitado)
```

---

## 🎬 Pipeline Completo Recomendado

### Para Video Profesional con Tu Imagen Real

```
1. FOTO BASE
   ├─ Tomar foto profesional
   ├─ Buena iluminación
   └─ Fondo neutro/corporativo

2. EDICIÓN FACIAL (OPCIONAL)
   ├─ Remini para mejora general
   ├─ FaceApp para densidad cabello (sutil: 20-30%)
   └─ Photoshop para ajustes finos

3. INTEGRACIÓN AL VIDEO
   ├─ Colocar foto editada en assets/
   ├─ Modificar script generar_video_simple.py
   └─ Agregar efecto Ken Burns (zoom suave)

4. AUDIO
   ├─ Usar audio actual (Google TTS)
   └─ O grabar tu propia voz

5. GENERAR VIDEO FINAL
   ├─ Ejecutar script modificado
   └─ Verificar resultado

6. AJUSTES FINALES
   ├─ Revisar sincronización
   ├─ Ajustar timing de texto
   └─ Exportar versión final
```

---

## 📱 App Móvil para Edición Rápida

### FaceApp (iOS/Android)

**Paso a paso para densificar cabello sutilmente:**

```
1. Abrir FaceApp
2. Cargar tu foto profesional
3. Ir a "Hair" (Pelo)
4. Seleccionar "Style" > "Density"
5. IMPORTANTE: Ajustar slider a 20-30% (NO 100%)
6. Si se ve artificial, reducir más
7. Guardar imagen
8. Repetir si es necesario con "Young" (10-15%)
9. Comparar con original
10. Usar la que se vea más natural
```

**Configuración recomendada:**
- Hair Density: 25%
- Young filter: 10% (opcional)
- Skin smoother: 15% (opcional)
- Eye enhancer: 0% (mantener natural)

---

## 🎨 Edición con GIMP (Gratuito)

### Tutorial: Densificar Cabello Manualmente

```bash
# Instalar GIMP
sudo apt install gimp  # Linux
# O descargar desde gimp.org (Windows/Mac)

# Pasos:
1. Abrir imagen en GIMP
2. Duplicar capa (Capa > Duplicar capa)
3. Seleccionar "Clone Tool" (Herramienta clonar)
4. Configurar:
   - Brush: Soft
   - Opacity: 40-60%
   - Size: Ajustar según zona
5. Alt+Click en zona con cabello denso (fuente)
6. Pintar en entradas/zonas con menos pelo
7. Cambiar fuente frecuentemente (naturalidad)
8. Usar Smudge tool para suavizar
9. Ajustar opacidad de capa si es necesario
10. Guardar como JPG
```

---

## 🚀 Implementación Rápida

### Si tienes prisa (30 minutos):

```
1. Toma una selfie profesional con tu smartphone
   - Luz natural frente a ventana
   - Fondo limpio
   - Camisa formal

2. Edita con FaceApp (5 min)
   - Hair: 25%
   - Guardar

3. Sube a curso-rsi-2026/assets/foto_profesor.jpg

4. Ejecuta:
   cd curso-rsi-2026
   # Modificar script (ver ejemplo arriba)
   python3 scripts/generar_video_simple.py

5. Listo! Tu video personalizado está en output/
```

---

## 📚 Recursos Adicionales

### Tutoriales Recomendados

**YouTube:**
- "Natural Hair Thickening in Photoshop" - Phlearn
- "Frequency Separation for Portraits" - Adorama
- "Professional Headshot Retouching" - Unmesh Dinda

**Cursos:**
- Udemy: "Portrait Retouching Masterclass"
- Skillshare: "Natural Photo Editing"

### Herramientas Mencionadas

| Herramienta | Precio | Plataforma | Mejor Para |
|-------------|--------|------------|------------|
| Remini | $5/mes | Web, móvil | Mejora automática |
| FaceApp | Gratis/Pro | iOS, Android | Edición facial |
| Photoshop | $10/mes | PC, Mac | Control total |
| GIMP | Gratis | Linux, Win, Mac | Alternativa PS |
| HitPaw | $30 one-time | PC, Mac | Batch processing |

---

## ✅ Checklist de Edición Facial Sutil

Antes de usar la imagen editada, verifica que:

- [ ] La edición se ve **natural** (no artificial)
- [ ] El cabello agregado coincide con tu color/textura real
- [ ] No hay líneas o bordes evidentes
- [ ] La iluminación es consistente
- [ ] Tu identidad es claramente reconocible
- [ ] No se ve "de plástico" o sobre-procesado
- [ ] Alguien más confirma que se ve natural

**Regla de oro:** Menos es más. Mejor quedarse corto que exagerar.

---

## 📧 Soporte

Si necesitas ayuda con la edición facial o personalización del video:

1. Consultar tutoriales en YouTube (buscar por herramienta específica)
2. Revisar documentación de cada herramienta
3. Experimentar con copias de la imagen (no el original)

---

**Nota Final:** El video actual está completamente funcional y profesional. La edición facial es completamente **opcional** y solo recomendada si tienes tiempo y experiencia con herramientas de edición.

---

*Documento creado: 10 de Agosto, 2026*  
*Para: Profesor Jaime Wilk Núñez*  
*Curso: Responsabilidad Social en la Industria - IBERO*
