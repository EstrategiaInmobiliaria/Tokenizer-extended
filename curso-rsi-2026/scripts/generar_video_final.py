#!/usr/bin/env python3
"""
Script para generar el video final con duración exacta del audio
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
    
    if not audio_file.exists():
        print("✗ Error: No se encontró el archivo de audio")
        return None
    
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
        print(f"✗ Error: {e}")
        return None

def create_professional_video(duration):
    """Crea un video profesional con animaciones y transiciones"""
    output_file = OUTPUT_DIR / "video_base.mp4"
    
    width = 1920
    height = 1080
    
    # Filtros de video con texto animado
    video_filter = (
        # Fondo degradado profesional
        f"color=c=#1a1a2e:s={width}x{height}:d={duration}:r=30,"
        
        # Título principal (0-5 segundos) - Fade in/out
        "drawtext="
        "text='RESPONSABILIDAD SOCIAL\\nEN LA INDUSTRIA':"
        "fontsize=72:"
        "fontcolor=white:"
        "x=(w-text_w)/2:"
        "y=h/3:"
        "alpha='if(lt(t,1),t/1,if(lt(t,4),1,(5-t)/1))',"
        
        # Subtítulo del curso (0-5 segundos)
        "drawtext="
        "text='Otoño 2026 | Universidad Iberoamericana':"
        "fontsize=32:"
        "fontcolor=#6BA539:"
        "x=(w-text_w)/2:"
        "y=h/3+180:"
        "alpha='if(lt(t,1),t/1,if(lt(t,4),1,(5-t)/1))',"
        
        # Nombre del profesor (aparece en 5s, permanece)
        "drawtext="
        "text='Jaime Wilk Núñez':"
        "fontsize=56:"
        "fontcolor=#6BA539:"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "x=(w-text_w)/2:"
        "y=h/2-60:"
        "alpha='if(lt(t,5),0,if(lt(t,6),(t-5)/1,1))',"
        
        # Credenciales del profesor
        "drawtext="
        "text='Ingeniero Industrial | MBA en Negocios Internacionales':"
        "fontsize=28:"
        "fontcolor=white:"
        "x=(w-text_w)/2:"
        "y=h/2+40:"
        "alpha='if(lt(t,5),0,if(lt(t,6),(t-5)/1,1))',"
        
        # Experiencia
        "drawtext="
        "text='+ 20 años de experiencia en empresas multinacionales':"
        "fontsize=24:"
        "fontcolor=#cccccc:"
        "x=(w-text_w)/2:"
        "y=h/2+100:"
        "alpha='if(lt(t,6),0,if(lt(t,7),(t-6)/1,1))',"
        
        # Pilares del curso (aparecen en 15s)
        "drawtext="
        "text='4 PILARES DEL CURSO':"
        "fontsize=48:"
        "fontcolor=#6BA539:"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "x=(w-text_w)/2:"
        "y=200:"
        "alpha='if(lt(t,15),0,if(lt(t,16),(t-15)/1,if(lt(t,35),1,0)))',"
        
        # Pilar 1: Sostenibilidad
        "drawtext="
        "text='🌱 SOSTENIBILIDAD':"
        "fontsize=38:"
        "fontcolor=white:"
        "x=200:"
        "y=400:"
        "alpha='if(lt(t,16),0,if(lt(t,17),(t-16)/1,if(lt(t,35),1,0)))',"
        
        "drawtext="
        "text='Economía circular y estrategias ambientales':"
        "fontsize=24:"
        "fontcolor=#cccccc:"
        "x=200:"
        "y=460:"
        "alpha='if(lt(t,16),0,if(lt(t,17),(t-16)/1,if(lt(t,35),1,0)))',"
        
        # Pilar 2: Impacto Social
        "drawtext="
        "text='👥 IMPACTO SOCIAL':"
        "fontsize=38:"
        "fontcolor=white:"
        "x=200:"
        "y=560:"
        "alpha='if(lt(t,18),0,if(lt(t,19),(t-18)/1,if(lt(t,35),1,0)))',"
        
        "drawtext="
        "text='Desarrollo de comunidades y equidad':"
        "fontsize=24:"
        "fontcolor=#cccccc:"
        "x=200:"
        "y=620:"
        "alpha='if(lt(t,18),0,if(lt(t,19),(t-18)/1,if(lt(t,35),1,0)))',"
        
        # Pilar 3: Ética y Gobernanza
        "drawtext="
        "text='⚖️ ÉTICA Y GOBERNANZA':"
        "fontsize=38:"
        "fontcolor=white:"
        "x=200:"
        "y=720:"
        "alpha='if(lt(t,20),0,if(lt(t,21),(t-20)/1,if(lt(t,35),1,0)))',"
        
        "drawtext="
        "text='Transparencia y códigos de conducta':"
        "fontsize=24:"
        "fontcolor=#cccccc:"
        "x=200:"
        "y=780:"
        "alpha='if(lt(t,20),0,if(lt(t,21),(t-20)/1,if(lt(t,35),1,0)))',"
        
        # Pilar 4: Innovación
        "drawtext="
        "text='💡 INNOVACIÓN Y COMPETITIVIDAD':"
        "fontsize=38:"
        "fontcolor=white:"
        "x=200:"
        "y=880:"
        "alpha='if(lt(t,22),0,if(lt(t,23),(t-22)/1,if(lt(t,35),1,0)))',"
        
        "drawtext="
        "text='Casos reales de la industria':"
        "fontsize=24:"
        "fontcolor=#cccccc:"
        "x=200:"
        "y=940:"
        "alpha='if(lt(t,22),0,if(lt(t,23),(t-22)/1,if(lt(t,35),1,0)))',"
        
        # Rompehielos (aparece al final, 55s+)
        "drawtext="
        f"text='¡Es hora de conocernos!':"
        "fontsize=52:"
        "fontcolor=#6BA539:"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "x=(w-text_w)/2:"
        "y=h/2-100:"
        f"alpha='if(lt(t,55),0,if(lt(t,56),(t-55)/1,1))',"
        
        "drawtext="
        "text='Preséntense brevemente:':"
        "fontsize=36:"
        "fontcolor=white:"
        "x=(w-text_w)/2:"
        "y=h/2+20:"
        "alpha='if(lt(t,56),0,if(lt(t,57),(t-56)/1,1))',"
        
        "drawtext="
        "text='• ¿Qué esperan aprender?':"
        "fontsize=28:"
        "fontcolor=#cccccc:"
        "x=400:"
        "y=h/2+120:"
        "alpha='if(lt(t,57),0,if(lt(t,58),(t-57)/1,1))',"
        
        "drawtext="
        "text='• ¿En qué semestre van?':"
        "fontsize=28:"
        "fontcolor=#cccccc:"
        "x=400:"
        "y=h/2+180:"
        "alpha='if(lt(t,58),0,if(lt(t,59),(t-58)/1,1))',"
        
        "drawtext="
        "text='• ¿Quiénes son ustedes?':"
        "fontsize=28:"
        "fontcolor=#cccccc:"
        "x=400:"
        "y=h/2+240:"
        "alpha='if(lt(t,59),0,if(lt(t,60),(t-59)/1,1))'"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=#1a1a2e:s={width}x{height}:d={duration}:r=30",
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-b:v", "5000k",
        "-pix_fmt", "yuv420p",
        str(output_file)
    ]
    
    try:
        print("🎬 Generando video profesional con animaciones...")
        result = subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video generado: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"  stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return None

def combine_video_audio(video_file, audio_file, output_file):
    """Combina video y audio"""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_file)
    ]
    
    try:
        print("🔊 Combinando video y audio...")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video final generado: {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 80)
    print("GENERADOR DE VIDEO FINAL PROFESIONAL")
    print("Responsabilidad Social en la Industria - Otoño 2026")
    print("=" * 80)
    print()
    
    # Obtener duración del audio
    print("📊 Analizando audio...")
    duration = get_audio_duration()
    
    if not duration:
        sys.exit(1)
    
    print(f"✓ Duración del audio: {duration:.1f} segundos ({duration/60:.2f} minutos)")
    print()
    
    # Generar video
    video_file = create_professional_video(duration)
    if not video_file:
        sys.exit(1)
    
    print()
    
    # Combinar video y audio
    audio_file = ASSETS_DIR / "audio_profesor.mp3"
    output_file = OUTPUT_DIR / "video_intro_rsi_2026_FINAL.mp4"
    
    if not combine_video_audio(video_file, audio_file, output_file):
        sys.exit(1)
    
    # Mostrar información final
    file_size = output_file.stat().st_size / 1024 / 1024
    
    print()
    print("=" * 80)
    print("✅ VIDEO FINAL COMPLETADO")
    print("=" * 80)
    print(f"\n📹 Archivo: {output_file.name}")
    print(f"📊 Tamaño: {file_size:.2f} MB")
    print(f"⏱️  Duración: {duration:.1f} segundos ({duration/60:.2f} minutos)")
    print(f"📐 Resolución: 1920x1080 (Full HD)")
    print(f"🎵 Audio: AAC 192kbps")
    print()
    print("✨ El video está listo para:")
    print("   • Subir a la plataforma de IBERO")
    print("   • Compartir en WhatsApp/Teams con los alumnos")
    print("   • Usar como introducción en la primera clase")
    print()
    print("📂 Ruta completa:")
    print(f"   {output_file.absolute()}")
    print()

if __name__ == "__main__":
    main()
