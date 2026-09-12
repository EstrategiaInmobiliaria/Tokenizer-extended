#!/usr/bin/env python3
"""
Script para generar video introductorio profesional
Curso: Responsabilidad Social en la Industria - Otoño 2026
Profesor: Jaime Wilk Núñez
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuración de paths
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Crear directorios si no existen
ASSETS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuración del video
VIDEO_CONFIG = {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "duration": 75,  # 1:15 minutos
    "bitrate": "5000k",
    "audio_bitrate": "192k"
}

def check_dependencies():
    """Verifica que ffmpeg esté instalado"""
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      check=True)
        print("✓ FFmpeg está instalado")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Error: FFmpeg no está instalado")
        return False

def create_professional_background():
    """Crea un fondo profesional con colores de IBERO"""
    output_file = ASSETS_DIR / "background.png"
    
    # Colores institucionales IBERO: Verde (#6BA539) y blanco
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=#1a1a1a:s={VIDEO_CONFIG['width']}x{VIDEO_CONFIG['height']}:d=1",
        "-vframes", "1",
        str(output_file)
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"✓ Fondo creado: {output_file}")
    return output_file

def generate_text_overlays():
    """Genera los overlays de texto para cada sección"""
    overlays = {
        "titulo": {
            "text": "RESPONSABILIDAD SOCIAL\\nEN LA INDUSTRIA",
            "duration": 3,
            "position": "center"
        },
        "profesor": {
            "text": "Jaime Wilk Núñez\\nProfesor - Ingenería Industrial | MBA\\nUniversidad Iberoamericana",
            "duration": 5,
            "position": "bottom"
        },
        "pilares": {
            "text": "4 PILARES DEL CURSO:\\n\\n• Sostenibilidad\\n• Impacto Social\\n• Ética y Gobernanza\\n• Innovación y Competitividad",
            "duration": 8,
            "position": "right"
        }
    }
    return overlays

def create_audio_script():
    """Lee el guion y prepara el texto para audio"""
    guion_file = BASE_DIR / "guion.txt"
    
    if not guion_file.exists():
        print("✗ Error: No se encontró el archivo de guión")
        return None
    
    with open(guion_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo el texto hablado (sin las secciones marcadas con ===)
    lines = content.split('\n')
    speech_lines = [line.strip() for line in lines 
                   if line.strip() and not line.startswith('=') 
                   and not line.startswith('Curso:')
                   and not line.startswith('Profesor:')
                   and not line.startswith('Semestre:')
                   and not line.startswith('Universidad:')
                   and not line.startswith('SECCIÓN')]
    
    speech_text = ' '.join(speech_lines)
    
    print(f"✓ Guión procesado: {len(speech_text)} caracteres")
    return speech_text

def generate_placeholder_video():
    """Genera un video placeholder profesional mientras esperamos las imágenes reales"""
    output_file = OUTPUT_DIR / "video_intro_rsi_2026_placeholder.mp4"
    
    print("\n🎬 Generando video placeholder profesional...")
    
    # Crear video base con fondo y texto
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=#1a1a2e:s={VIDEO_CONFIG['width']}x{VIDEO_CONFIG['height']}:d={VIDEO_CONFIG['duration']}:r={VIDEO_CONFIG['fps']}",
        
        # Agregar texto principal
        "-vf", (
            "drawtext="
            f"text='RESPONSABILIDAD SOCIAL\\nEN LA INDUSTRIA':"
            "fontsize=72:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=h/4:"
            "enable='between(t,0,5)',"
            
            "drawtext="
            f"text='Jaime Wilk Núñez':"
            "fontsize=48:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=h/2:"
            "enable='between(t,5,75)',"
            
            "drawtext="
            f"text='Profesor - Ingeniería Industrial | MBA':"
            "fontsize=32:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=h/2+80:"
            "enable='between(t,5,75)',"
            
            "drawtext="
            f"text='Universidad Iberoamericana':"
            "fontsize=28:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=h/2+140:"
            "enable='between(t,5,75)',"
            
            "drawtext="
            f"text='Otoño 2026':"
            "fontsize=36:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=h*3/4:"
            "enable='between(t,5,75)'"
        ),
        
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", VIDEO_CONFIG['bitrate'],
        "-pix_fmt", "yuv420p",
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Video placeholder generado: {output_file}")
        print(f"  Tamaño: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generando video: {e}")
        print(f"  stderr: {e.stderr}")
        return None

def add_audio_instructions():
    """Muestra instrucciones para agregar audio profesional"""
    instructions = """
    
📢 SIGUIENTE PASO: AGREGAR AUDIO PROFESIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para agregar audio de calidad profesional, tienes 3 opciones:

OPCIÓN 1: Grabar tu propia voz (RECOMENDADO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Usar tu smartphone o micrófono USB
2. Grabar en un lugar silencioso
3. Leer el guion desde: curso-rsi-2026/guion.txt
4. Guardar como: curso-rsi-2026/assets/audio_profesor.mp3
5. Ejecutar: python3 scripts/combinar_audio_video.py

OPCIÓN 2: Usar servicio de Text-to-Speech profesional
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- ElevenLabs (muy natural): https://elevenlabs.io
- Google Cloud TTS: https://cloud.google.com/text-to-speech
- Amazon Polly: https://aws.amazon.com/polly/

OPCIÓN 3: Usar herramientas locales
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Coqui TTS (open source)
- pyttsx3 (básico, menos natural)

El guion completo está en: curso-rsi-2026/guion.txt
Duración estimada: 1:15 minutos
"""
    print(instructions)

def main():
    print("=" * 80)
    print("GENERADOR DE VIDEO INTRODUCTORIO")
    print("Responsabilidad Social en la Industria - Otoño 2026")
    print("Profesor: Jaime Wilk Núñez")
    print("=" * 80)
    print()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Procesar guion
    speech_text = create_audio_script()
    if not speech_text:
        sys.exit(1)
    
    # Generar video placeholder
    video_file = generate_placeholder_video()
    if not video_file:
        sys.exit(1)
    
    # Mostrar instrucciones para audio
    add_audio_instructions()
    
    print("\n✅ PROCESO COMPLETADO")
    print(f"\nVideo generado: {video_file}")
    print("\nSiguientes pasos:")
    print("1. Revisar el guion en: curso-rsi-2026/guion.txt")
    print("2. Grabar o generar el audio profesional")
    print("3. Colocar el audio en: curso-rsi-2026/assets/audio_profesor.mp3")
    print("4. Ejecutar: python3 scripts/combinar_audio_video.py")
    print()

if __name__ == "__main__":
    main()
