#!/usr/bin/env python3
"""
Script para combinar el video con el audio profesional
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"

def check_audio_file():
    """Verifica que exista el archivo de audio"""
    audio_file = ASSETS_DIR / "audio_profesor.mp3"
    
    if not audio_file.exists():
        # Buscar otros formatos de audio
        alternatives = [
            ASSETS_DIR / "audio_profesor.wav",
            ASSETS_DIR / "audio_profesor.m4a",
            ASSETS_DIR / "audio.mp3",
            ASSETS_DIR / "audio.wav"
        ]
        
        for alt in alternatives:
            if alt.exists():
                return alt
        
        print("✗ Error: No se encontró el archivo de audio")
        print(f"  Esperado en: {audio_file}")
        print(f"  Alternativas: {', '.join([str(a) for a in alternatives])}")
        return None
    
    return audio_file

def get_audio_duration(audio_file):
    """Obtiene la duración del audio en segundos"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception as e:
        print(f"✗ Error obteniendo duración del audio: {e}")
        return None

def combine_video_audio(video_file, audio_file, output_file):
    """Combina el video con el audio"""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",  # Ajustar al más corto
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video con audio generado: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error combinando video y audio: {e}")
        return False

def main():
    print("=" * 80)
    print("COMBINADOR DE VIDEO Y AUDIO")
    print("=" * 80)
    print()
    
    # Buscar video
    video_files = list(OUTPUT_DIR.glob("video_intro_rsi_2026*.mp4"))
    if not video_files:
        print("✗ Error: No se encontró el video base")
        sys.exit(1)
    
    video_file = video_files[0]
    print(f"✓ Video encontrado: {video_file.name}")
    
    # Buscar audio
    audio_file = check_audio_file()
    if not audio_file:
        sys.exit(1)
    
    print(f"✓ Audio encontrado: {audio_file.name}")
    
    # Obtener duración del audio
    duration = get_audio_duration(audio_file)
    if duration:
        print(f"✓ Duración del audio: {duration:.1f} segundos ({duration/60:.1f} minutos)")
    
    # Combinar
    output_file = OUTPUT_DIR / "video_intro_rsi_2026_FINAL.mp4"
    print("\n🎬 Combinando video y audio...")
    
    if combine_video_audio(video_file, audio_file, output_file):
        print("\n✅ PROCESO COMPLETADO")
        print(f"\nVideo final: {output_file}")
        print(f"Tamaño: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        print("\n¡Listo para subir al curso de IBERO! 🎓")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
