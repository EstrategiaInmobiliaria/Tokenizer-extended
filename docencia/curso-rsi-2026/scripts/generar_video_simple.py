#!/usr/bin/env python3
"""
Genera un video profesional simple que funcione correctamente con FFmpeg
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"

def get_audio_duration():
    """Obtiene la duración del audio"""
    audio_file = ASSETS_DIR / "audio_profesor.mp3"
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def create_video_with_audio():
    """Crea el video directamente con el audio"""
    audio_file = ASSETS_DIR / "audio_profesor.mp3"
    output_file = OUTPUT_DIR / "video_intro_rsi_2026_FINAL.mp4"
    
    duration = get_audio_duration()
    if not duration:
        return None
    
    print(f"✓ Duración del audio: {duration:.1f} segundos ({duration/60:.2f} minutos)")
    print()
    print("🎬 Generando video profesional...")
    
    # Crear video con fondo y texto que sincroniza con el audio
    cmd = [
        "ffmpeg", "-y",
        
        # Input de color de fondo
        "-f", "lavfi", "-i", f"color=c=#1a1a2e:s=1920x1080:r=30",
        
        # Input de audio
        "-i", str(audio_file),
        
        # Filtro de video con textos
        "-filter_complex",
        (
            # Texto principal - Título del curso (primeros 5 segundos)
            "[0:v]drawtext="
            "text='RESPONSABILIDAD SOCIAL EN LA INDUSTRIA':"
            "fontsize=60:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=h/3:"
            "enable='between(t,0,5)',"
            
            # Subtítulo
            "drawtext="
            "text='Otoño 2026 | Universidad Iberoamericana':"
            "fontsize=32:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=h/3+120:"
            "enable='between(t,0,5)',"
            
            # Nombre del profesor (del segundo 5 en adelante)
            "drawtext="
            "text='Prof. Jaime Wilk Núñez':"
            "fontsize=52:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=200:"
            "enable='gte(t,5)',"
            
            # Credenciales
            "drawtext="
            "text='Ingeniero Industrial | MBA':"
            "fontsize=28:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=300:"
            "enable='gte(t,5)',"
            
            # 4 Pilares (aparecen del segundo 20 al 50)
            "drawtext="
            "text='4 PILARES DEL CURSO':"
            "fontsize=44:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=450:"
            "enable='between(t,20,50)',"
            
            "drawtext="
            "text='Sostenibilidad | Impacto Social | Ética | Innovación':"
            "fontsize=26:"
            "fontcolor=#cccccc:"
            "x=(w-text_w)/2:"
            "y=530:"
            "enable='between(t,20,50)',"
            
            # Rompehielos (últimos 30 segundos)
            "drawtext="
            "text='¡Hora de conocernos!':"
            "fontsize=48:"
            "fontcolor=#6BA539:"
            "x=(w-text_w)/2:"
            "y=h/2-80:"
            f"enable='gte(t,{duration-30})',"
            
            "drawtext="
            "text='Por favor preséntense brevemente':"
            "fontsize=32:"
            "fontcolor=white:"
            "x=(w-text_w)/2:"
            "y=h/2+20:"
            f"enable='gte(t,{duration-30})'[v]"
        ),
        
        # Mapear video y audio
        "-map", "[v]",
        "-map", "1:a",
        
        # Configuración de output
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", "4000k",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video generado exitosamente")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generando video")
        print(f"  FFmpeg stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None

def main():
    print("=" * 80)
    print("GENERADOR DE VIDEO FINAL")
    print("Responsabilidad Social en la Industria - Otoño 2026")
    print("=" * 80)
    print()
    
    output_file = create_video_with_audio()
    
    if not output_file:
        sys.exit(1)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    duration = get_audio_duration()
    
    print()
    print("=" * 80)
    print("✅ VIDEO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print()
    print(f"📹 Archivo: {output_file.name}")
    print(f"📊 Tamaño: {file_size:.2f} MB")
    print(f"⏱️  Duración: {duration:.1f} segundos ({duration/60:.2f} minutos)")
    print(f"📐 Resolución: 1920x1080 Full HD")
    print(f"🎵 Audio: AAC 192kbps estéreo")
    print()
    print("✨ Listo para usar en:")
    print("   ✓ Plataforma IBERO")
    print("   ✓ WhatsApp/Teams")
    print("   ✓ Primera clase presencial")
    print()
    print(f"📂 Ruta: {output_file.absolute()}")
    print()

if __name__ == "__main__":
    main()
