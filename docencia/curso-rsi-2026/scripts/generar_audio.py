#!/usr/bin/env python3
"""
Script para generar audio profesional del guion usando Google TTS
"""

import os
import sys
from pathlib import Path
from gtts import gTTS

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"

# Crear directorios si no existen
ASSETS_DIR.mkdir(exist_ok=True)

def load_guion():
    """Carga y procesa el guion"""
    guion_file = BASE_DIR / "guion.txt"
    
    if not guion_file.exists():
        print("✗ Error: No se encontró el archivo de guión")
        return None
    
    with open(guion_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer solo el texto hablado
    lines = content.split('\n')
    speech_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Filtrar líneas de formato
        if (line.startswith('=') or 
            line.startswith('Curso:') or 
            line.startswith('Profesor:') or
            line.startswith('Semestre:') or
            line.startswith('Universidad:') or
            line.startswith('GUIÓN') or
            line.startswith('SECCIÓN') or
            line.startswith('=====')):
            continue
        speech_lines.append(line)
    
    # Unir el texto con pausas naturales
    speech_text = ' '.join(speech_lines)
    
    # Reemplazar caracteres especiales para mejor pronunciación
    speech_text = speech_text.replace('MBA', 'eme-be-a')
    speech_text = speech_text.replace('GE', 'yi-í')
    speech_text = speech_text.replace('RSC', 'erre ese ce')
    speech_text = speech_text.replace('IBERO', 'ibero')
    
    return speech_text

def generate_audio(text, output_file, lang='es', slow=False):
    """Genera el archivo de audio usando Google TTS"""
    try:
        # Configurar gTTS para español de México
        tts = gTTS(text=text, lang=lang, slow=slow, tld='com.mx')
        tts.save(str(output_file))
        return True
    except Exception as e:
        print(f"✗ Error generando audio: {e}")
        return False

def optimize_audio(input_file, output_file):
    """Optimiza el audio para mejor calidad"""
    import subprocess
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        # Normalizar volumen
        "-filter:a", "loudnorm=I=-16:TP=-1.5:LRA=11",
        # Configuración de calidad
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "44100",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"  Advertencia: No se pudo optimizar el audio: {e}")
        return False

def main():
    print("=" * 80)
    print("GENERADOR DE AUDIO PROFESIONAL")
    print("Responsabilidad Social en la Industria - Otoño 2026")
    print("=" * 80)
    print()
    
    # Cargar guion
    print("📝 Procesando guion...")
    speech_text = load_guion()
    
    if not speech_text:
        sys.exit(1)
    
    print(f"✓ Texto procesado: {len(speech_text)} caracteres")
    print(f"  Palabras: {len(speech_text.split())}")
    print(f"  Duración estimada: {len(speech_text.split()) / 150 * 60:.1f} segundos")
    print()
    
    # Generar audio
    print("🎙️  Generando audio con Google TTS (Español de México)...")
    temp_file = ASSETS_DIR / "audio_temp.mp3"
    output_file = ASSETS_DIR / "audio_profesor.mp3"
    
    if not generate_audio(speech_text, temp_file, lang='es', slow=False):
        sys.exit(1)
    
    print("✓ Audio base generado")
    
    # Optimizar audio
    print("🔧 Optimizando calidad de audio...")
    if optimize_audio(temp_file, output_file):
        print("✓ Audio optimizado")
        # Eliminar archivo temporal
        temp_file.unlink()
    else:
        # Si falla la optimización, usar el archivo base
        temp_file.rename(output_file)
        print("⚠️  Usando audio sin optimización")
    
    file_size = output_file.stat().st_size / 1024
    print()
    print("✅ AUDIO GENERADO EXITOSAMENTE")
    print(f"\nArchivo: {output_file}")
    print(f"Tamaño: {file_size:.1f} KB")
    print()
    print("Siguiente paso:")
    print("  python3 scripts/combinar_audio_video.py")
    print()

if __name__ == "__main__":
    main()
