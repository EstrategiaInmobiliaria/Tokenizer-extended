# Video Introductorio - Responsabilidad Social en la Industria

**Profesor:** Jaime Wilk Núñez  
**Curso:** Responsabilidad Social en la Industria  
**Semestre:** Otoño 2026  
**Universidad:** Universidad Iberoamericana (IBERO)

---

## 📋 Contenido del Video

### Duración: 1:15 minutos

**Secciones:**
1. **Bienvenida** (0:00-0:15): Presentación personal y credenciales
2. **Propósito** (0:15-0:35): Objetivo del curso y enfoque práctico
3. **4 Pilares** (0:35-0:55): Sostenibilidad, Impacto Social, Ética y Gobernanza, Innovación
4. **Rompehielos** (0:55-1:15): Invitación a que los alumnos se presenten

---

## 🚀 Guía de Uso Rápida

### Opción 1: Video con Audio Pregrabado (RECOMENDADO)

```bash
# 1. Grabar tu voz leyendo el guion (guion.txt)
#    - Usar smartphone o micrófono USB
#    - Lugar silencioso
#    - Guardar como: assets/audio_profesor.mp3

# 2. Generar video base
python3 scripts/generar_video.py

# 3. Combinar video + audio
python3 scripts/combinar_audio_video.py

# 4. Video final estará en: output/video_intro_rsi_2026_FINAL.mp4
```

### Opción 2: Usar Servicio Text-to-Speech Profesional

**Servicios recomendados:**
- **ElevenLabs** (mejor calidad, voz muy natural): https://elevenlabs.io
- **Google Cloud TTS** (buena calidad): https://cloud.google.com/text-to-speech
- **Amazon Polly** (opción AWS): https://aws.amazon.com/polly/

**Pasos:**
1. Copiar el texto del `guion.txt`
2. Generar audio en el servicio elegido
3. Descargar como `audio_profesor.mp3` en carpeta `assets/`
4. Ejecutar los scripts como en Opción 1

---

## 📁 Estructura del Proyecto

```
curso-rsi-2026/
├── assets/               # Imágenes y audios
│   ├── foto_profesor.jpg       # Tu foto profesional
│   ├── audio_profesor.mp3      # Audio del guion
│   └── background.png          # Fondo generado
├── output/               # Videos generados
│   ├── video_intro_rsi_2026_placeholder.mp4
│   └── video_intro_rsi_2026_FINAL.mp4
├── scripts/              # Scripts Python
│   ├── generar_video.py
│   └── combinar_audio_video.py
├── guion.txt            # Guion completo del video
└── README.md            # Este archivo
```

---

## 🎨 Personalización

### Cambiar el fondo

Edita en `scripts/generar_video.py`:
```python
# Línea ~45: Cambiar color de fondo
"color=c=#1a1a2e:s={width}x{height}"  # Color actual: azul oscuro
# Opciones:
# - Verde IBERO: #6BA539
# - Blanco: #FFFFFF
# - Negro: #000000
```

### Ajustar duración

Edita en `guion.txt` el contenido y en `generar_video.py`:
```python
VIDEO_CONFIG = {
    "duration": 75,  # Cambiar según duración del audio
}
```

### Agregar logo de IBERO

1. Colocar logo en: `assets/logo_ibero.png`
2. El script lo agregará automáticamente en la esquina superior derecha

---

## 🎯 Especificaciones Técnicas

- **Resolución:** 1920x1080 (Full HD)
- **FPS:** 30
- **Bitrate Video:** 5000k
- **Audio:** AAC 192kbps
- **Formato:** MP4 (H.264)
- **Duración:** 75 segundos (1:15)

---

## 📝 Tips para Grabar Audio Profesional

### Equipo
- **Micrófono:** USB de solapa o smartphone moderno
- **Lugar:** Silencioso, sin eco (closet con ropa funciona bien)
- **Posición:** 15-20cm de distancia del micrófono

### Técnica
1. **Leer el guion 2-3 veces** antes de grabar (para naturalidad)
2. **Tono:** Cercano, profesional, entusiasta (no monótono)
3. **Ritmo:** Pausas naturales, no apresurado
4. **Errores:** No importan, se pueden editar después

### Apps recomendadas
- **iOS:** Voice Memos, GarageBand
- **Android:** Smart Recorder, Easy Voice Recorder
- **PC/Mac:** Audacity (gratis), Adobe Audition

---

## 🔧 Solución de Problemas

### Error: "FFmpeg no encontrado"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# MacOS
brew install ffmpeg
```

### Audio no sincroniza con video
```bash
# Verificar duración del audio
ffprobe -i assets/audio_profesor.mp3 -show_entries format=duration

# Ajustar duración del video en generar_video.py
```

### Video muy pesado
```bash
# Reducir bitrate en generar_video.py
"bitrate": "3000k",  # En lugar de 5000k
```

---

## 📧 Contacto

**Profesor:** Jaime Wilk Núñez  
**Email:** jwilk@global-t-bird.edu / 5561000600  
**Universidad:** Universidad Iberoamericana

---

## 📄 Licencia

Este material es propiedad de la Universidad Iberoamericana y el profesor Jaime Wilk Núñez.
Uso exclusivo para el curso de Responsabilidad Social en la Industria - Otoño 2026.

---

**Última actualización:** Agosto 2026
