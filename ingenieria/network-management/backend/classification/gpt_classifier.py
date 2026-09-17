"""
Clasificador GPT-4o-mini - Clasifica contactos en Tier, Tema y Zona
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
import pandas as pd

load_dotenv()
console = Console()


@dataclass
class ContactClassification:
    """Clasificación de un contacto"""
    tier: str
    temas: List[str]
    zona: str
    reasoning: Optional[str] = None


class GPTClassifier:
    """Clasificador de contactos usando GPT-4o-mini"""
    
    TIER_DEFINITIONS = """
    **Tier 1 - Decisores C-Level**: 
    - CEOs, CFOs, CTOs de empresas inmobiliarias, ESG, desarrolladores
    - Directores de fondos de inversión inmobiliaria
    - Líderes de asociaciones industriales (CANADEVI, AMPI, etc.)
    
    **Tier 2 - Partners Estratégicos**:
    - Socios actuales de Agartha
    - Consultores de estrategia inmobiliaria
    - Especialistas en sustentabilidad/ESG
    - Gerentes de proyectos inmobiliarios
    
    **Tier 3 - Red General**:
    - Contactos profesionales sin rol directo en inmobiliario/ESG
    - Networking general para nurture
    - Proveedores indirectos
    """
    
    TEMA_OPTIONS = [
        "Inmobiliario",
        "ESG/Sustentabilidad", 
        "Inversión/Fondos",
        "Construcción",
        "Tecnología PropTech",
        "Consultoría Estratégica",
        "Legal/Regulatorio",
        "Arquitectura/Diseño",
        "Gobierno/Sector Público",
        "Academia/Investigación",
        "Otro"
    ]
    
    ZONA_OPTIONS = [
        "CDMX",
        "Monterrey",
        "Guadalajara", 
        "Querétaro",
        "Bajío (León, Aguascalientes, etc.)",
        "Península de Yucatán",
        "Internacional",
        "Desconocida"
    ]
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("GPT_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("GPT_MAX_TOKENS", "150"))
        self.temperature = float(os.getenv("GPT_TEMPERATURE", "0.3"))
        
        console.print(f"[cyan]GPT Classifier initialized with model: {self.model}[/cyan]")
    
    def _create_classification_prompt(self, contact: Dict) -> str:
        """Crea el prompt para clasificación"""
        
        contact_info = []
        if contact.get('full_name'):
            contact_info.append(f"Nombre: {contact['full_name']}")
        if contact.get('company'):
            contact_info.append(f"Empresa: {contact['company']}")
        if contact.get('title'):
            contact_info.append(f"Puesto: {contact['title']}")
        if contact.get('notes'):
            contact_info.append(f"Notas: {contact['notes'][:200]}")
        
        contact_text = "\n".join(contact_info) if contact_info else "Información limitada"
        
        prompt = f"""Eres un experto en clasificación de redes profesionales para Agartha, empresa de estrategia inmobiliaria y ESG en México.

Clasifica este contacto en:

1. **TIER** (elige UNO):
{self.TIER_DEFINITIONS}

2. **TEMAS** (elige 1-3 más relevantes):
{', '.join(self.TEMA_OPTIONS)}

3. **ZONA** (elige UNA):
{', '.join(self.ZONA_OPTIONS)}

**CONTACTO:**
{contact_text}

**RESPONDE EN JSON:**
{{
  "tier": "Tier 1|Tier 2|Tier 3",
  "temas": ["tema1", "tema2"],
  "zona": "zona",
  "reasoning": "breve justificación de 1 línea"
}}

JSON:"""
        
        return prompt
    
    def classify_contact(self, contact: Dict) -> ContactClassification:
        """Clasifica un contacto individual"""
        
        prompt = self._create_classification_prompt(contact)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en clasificación de contactos profesionales. Respondes SOLO con JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return ContactClassification(
                tier=result.get('tier', 'Tier 3'),
                temas=result.get('temas', ['Otro']),
                zona=result.get('zona', 'Desconocida'),
                reasoning=result.get('reasoning', '')
            )
            
        except Exception as e:
            console.print(f"[yellow]Warning: Classification failed for {contact.get('full_name', 'unknown')}: {e}[/yellow]")
            return ContactClassification(
                tier="Tier 3",
                temas=["Otro"],
                zona="Desconocida",
                reasoning="Clasificación automática falló"
            )
    
    def classify_batch(
        self,
        contacts: List[Dict],
        batch_size: int = 10,
        show_progress: bool = True
    ) -> List[ContactClassification]:
        """Clasifica múltiples contactos con rate limiting"""
        
        console.print(f"\n[cyan]Classifying {len(contacts)} contacts...[/cyan]")
        
        classifications = []
        
        iterator = track(contacts, description="Classifying") if show_progress else contacts
        
        for contact in iterator:
            classification = self.classify_contact(contact)
            classifications.append(classification)
        
        tier_counts = {}
        for c in classifications:
            tier_counts[c.tier] = tier_counts.get(c.tier, 0) + 1
        
        console.print("\n[green]✓ Classification complete[/green]")
        console.print("\n[cyan]Distribution:[/cyan]")
        for tier, count in sorted(tier_counts.items()):
            console.print(f"  • {tier}: {count} contacts")
        
        return classifications
    
    def add_classifications_to_df(
        self,
        df: pd.DataFrame,
        classifications: List[ContactClassification]
    ) -> pd.DataFrame:
        """Añade clasificaciones al DataFrame"""
        
        if len(df) != len(classifications):
            raise ValueError(f"Mismatch: {len(df)} contacts vs {len(classifications)} classifications")
        
        df = df.copy()
        df['tier'] = [c.tier for c in classifications]
        df['temas'] = [','.join(c.temas) for c in classifications]
        df['zona'] = [c.zona for c in classifications]
        df['classification_reasoning'] = [c.reasoning for c in classifications]
        
        return df


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python gpt_classifier.py <contacts_csv>[/red]")
        console.print("CSV should have columns: full_name, company, title, notes")
        sys.exit(1)
    
    df = pd.read_csv(sys.argv[1])
    
    classifier = GPTClassifier()
    contacts_dicts = df.to_dict('records')
    
    classifications = classifier.classify_batch(contacts_dicts)
    
    df_classified = classifier.add_classifications_to_df(df, classifications)
    
    output_path = sys.argv[1].replace('.csv', '_classified.csv')
    df_classified.to_csv(output_path, index=False)
    
    console.print(f"\n[green]✓ Saved to: {output_path}[/green]")
