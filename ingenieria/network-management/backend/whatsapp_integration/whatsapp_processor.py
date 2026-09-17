"""
Procesador de WhatsApp - Transcripción y análisis de notas de voz
"""
import os
from pathlib import Path
from typing import Dict, Optional, List
import openai
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
import json

load_dotenv()
console = Console()


class WhatsAppProcessor:
    """
    Procesa mensajes de WhatsApp, especialmente notas de voz
    
    Integración con n8n:
    1. n8n recibe webhook de WhatsApp
    2. Descarga audio de nota de voz
    3. Llama a este procesador
    4. Guarda en Supabase + actualiza grafo Kùzu
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY required")
        
        self.client = OpenAI(api_key=api_key)
        console.print("[green]✓ WhatsApp processor initialized[/green]")
    
    def transcribe_audio(self, audio_path: Path) -> str:
        """
        Transcribe audio usando Whisper
        
        Args:
            audio_path: Ruta al archivo de audio (.ogg, .mp3, .m4a, etc.)
        
        Returns:
            Transcripción en texto
        """
        console.print(f"\n[cyan]Transcribing audio:[/cyan] {audio_path.name}")
        
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            
            text = transcript.text
            
            console.print(f"[green]✓ Transcribed {len(text)} characters[/green]")
            
            return text
            
        except Exception as e:
            console.print(f"[red]Transcription failed: {e}[/red]")
            raise
    
    def extract_meeting_info(self, transcript: str) -> Dict:
        """
        Extrae información estructurada de la transcripción
        
        Returns:
            Dict con: resumen, contactos mencionados, temas, próximos pasos
        """
        console.print("\n[cyan]Extracting meeting information...[/cyan]")
        
        prompt = f"""Eres un asistente experto en analizar reuniones de negocios.

Analiza esta transcripción de una reunión/conversación y extrae:

1. **Resumen**: Resumen ejecutivo de 2-3 líneas
2. **Contactos mencionados**: Nombres de personas mencionadas (con empresa si se menciona)
3. **Temas principales**: Lista de temas discutidos
4. **Próximos pasos**: Acciones o compromisos mencionados
5. **Sentimiento**: positivo/neutral/negativo

**TRANSCRIPCIÓN:**
{transcript}

**RESPONDE EN JSON:**
{{
  "resumen": "texto del resumen",
  "contactos": [
    {{"nombre": "Juan Pérez", "empresa": "Agartha", "rol": "decisor|partner|general"}},
    ...
  ],
  "temas": ["Inmobiliario", "ESG", ...],
  "proximos_pasos": ["Enviar propuesta", ...],
  "sentimiento": "positivo|neutral|negativo",
  "fecha_mencionada": "2024-03-15 o null",
  "ubicacion_mencionada": "Monterrey o null"
}}

JSON:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en análisis de reuniones de negocios. Respondes SOLO con JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            console.print("[green]✓ Information extracted[/green]")
            
            return result
            
        except Exception as e:
            console.print(f"[yellow]Warning: Extraction failed: {e}[/yellow]")
            return {
                "resumen": transcript[:200],
                "contactos": [],
                "temas": [],
                "proximos_pasos": [],
                "sentimiento": "neutral",
                "fecha_mencionada": None,
                "ubicacion_mencionada": None
            }
    
    def create_embedding(self, text: str) -> List[float]:
        """Crea embedding del texto para búsqueda semántica"""
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            console.print(f"[yellow]Warning: Embedding failed: {e}[/yellow]")
            return None
    
    def process_voice_note(
        self,
        audio_path: Path,
        sender_phone: Optional[str] = None,
        save_transcript: bool = True
    ) -> Dict:
        """
        Pipeline completo: transcripción → análisis → embedding
        
        Returns:
            Dict completo listo para insertar en Supabase
        """
        console.print(f"\n[cyan]{'='*60}[/cyan]")
        console.print(f"[cyan]Processing voice note from: {sender_phone or 'unknown'}[/cyan]")
        console.print(f"[cyan]{'='*60}[/cyan]")
        
        transcript = self.transcribe_audio(audio_path)
        
        info = self.extract_meeting_info(transcript)
        
        embedding = self.create_embedding(transcript)
        
        result = {
            'transcript': transcript,
            'summary': info.get('resumen', ''),
            'sentiment': info.get('sentimiento', 'neutral'),
            'mentioned_contacts': info.get('contactos', []),
            'topics': info.get('temas', []),
            'next_steps': info.get('proximos_pasos', []),
            'mentioned_date': info.get('fecha_mencionada'),
            'mentioned_location': info.get('ubicacion_mencionada'),
            'embedding': embedding,
            'sender_phone': sender_phone,
            'audio_file': str(audio_path)
        }
        
        if save_transcript:
            transcript_path = audio_path.with_suffix('.json')
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            console.print(f"\n[green]✓ Saved transcript to: {transcript_path}[/green]")
        
        console.print("\n[cyan]Processing Summary:[/cyan]")
        console.print(f"  • Transcript length: {len(transcript)} chars")
        console.print(f"  • Sentiment: {result['sentiment']}")
        console.print(f"  • Mentioned contacts: {len(result['mentioned_contacts'])}")
        console.print(f"  • Topics: {', '.join(result['topics'][:3])}")
        
        return result
    
    def match_contact_by_phone(self, phone: str, contacts_df) -> Optional[Dict]:
        """
        Busca contacto en el DataFrame por teléfono
        
        Args:
            phone: Número de teléfono (puede incluir +52, etc.)
            contacts_df: DataFrame de contactos
        
        Returns:
            Dict con info del contacto o None
        """
        import re
        
        clean_phone = re.sub(r'[^\d]', '', phone)[-10:]
        
        matches = contacts_df[
            contacts_df['phone_primary'].notna() &
            contacts_df['phone_primary'].str.contains(clean_phone, na=False)
        ]
        
        if len(matches) > 0:
            return matches.iloc[0].to_dict()
        
        return None
    
    def process_text_message(
        self,
        message: str,
        sender_phone: Optional[str] = None
    ) -> Dict:
        """Procesa mensaje de texto simple"""
        
        console.print(f"\n[cyan]Processing text message from: {sender_phone or 'unknown'}[/cyan]")
        
        if len(message) < 50:
            return {
                'transcript': message,
                'summary': message,
                'sentiment': 'neutral',
                'mentioned_contacts': [],
                'topics': [],
                'next_steps': [],
                'embedding': self.create_embedding(message),
                'sender_phone': sender_phone
            }
        
        info = self.extract_meeting_info(message)
        embedding = self.create_embedding(message)
        
        return {
            'transcript': message,
            'summary': info.get('resumen', message[:100]),
            'sentiment': info.get('sentimiento', 'neutral'),
            'mentioned_contacts': info.get('contactos', []),
            'topics': info.get('temas', []),
            'next_steps': info.get('proximos_pasos', []),
            'mentioned_date': info.get('fecha_mencionada'),
            'mentioned_location': info.get('ubicacion_mencionada'),
            'embedding': embedding,
            'sender_phone': sender_phone
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python whatsapp_processor.py <audio_file> [phone][/red]")
        console.print("\nSupported formats: .ogg, .mp3, .m4a, .wav")
        sys.exit(1)
    
    audio_path = Path(sys.argv[1])
    sender_phone = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not audio_path.exists():
        console.print(f"[red]File not found: {audio_path}[/red]")
        sys.exit(1)
    
    processor = WhatsAppProcessor()
    result = processor.process_voice_note(audio_path, sender_phone)
    
    console.print("\n[green]✓ Processing complete[/green]")
    console.print(f"\n[cyan]Summary:[/cyan]\n{result['summary']}")
