"""
VCF Processor - Pragmatic GraphRAG System
Pipeline completo: VCF → Splink → GPT-4o-mini → Kùzu

FASE 0: 7 días para grafo funcional
- Input: VCF (iPhone/Android export)
- Output: Kùzu graph database listo para consultas

Stack minimalista:
- Kùzu (embebido, sin servidor)
- Splink (deduplicación)
- OpenAI GPT-4o-mini (clasificación barata: $0.15/1M tokens)
- Python script CLI (sin dependencias pesadas)
"""

import pandas as pd
import vobject
import json
from pathlib import Path
from typing import List, Dict, Optional
import re
import kuzu
from openai import OpenAI
from tqdm import tqdm
import argparse
from datetime import datetime

# ============================================
# 1. VCF PARSER (SIMPLE Y ROBUSTO)
# ============================================

class SimpleVCFParser:
    """Parser minimalista para VCF de iPhone/Android"""
    
    def parse_vcf(self, vcf_path: str) -> List[Dict]:
        """
        Parsea VCF y extrae solo lo esencial:
        - nombre, email, telefono, empresa, puesto, notas
        """
        contacts = []
        
        with open(vcf_path, 'r', encoding='utf-8', errors='ignore') as f:
            vcf_text = f.read()
        
        # Split por BEGIN:VCARD
        vcard_strings = vcf_text.split('BEGIN:VCARD')[1:]
        
        print(f"📇 Parseando {len(vcard_strings)} vCards...")
        
        for i, vcard_str in enumerate(tqdm(vcard_strings)):
            vcard_str = 'BEGIN:VCARD' + vcard_str
            
            try:
                vcard = vobject.readOne(vcard_str)
                
                contact = {
                    'id': f"VCF-{i:05d}",
                    'nombre': self._get_name(vcard),
                    'email': self._get_email(vcard),
                    'telefono': self._get_phone(vcard),
                    'empresa': self._get_org(vcard),
                    'puesto': self._get_title(vcard),
                    'notas': self._get_note(vcard),
                    'fuente': 'vCard'
                }
                
                # Solo agregar si tiene nombre o email
                if contact['nombre'] or contact['email']:
                    contacts.append(contact)
                    
            except Exception as e:
                # Ignorar vCards malformados
                continue
        
        print(f"✅ Parseados {len(contacts)} contactos válidos")
        return contacts
    
    def _get_name(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'fn'):
            return vcard.fn.value.strip()
        return None
    
    def _get_email(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'email'):
            if isinstance(vcard.email, list):
                return vcard.email[0].value if vcard.email else None
            return vcard.email.value
        return None
    
    def _get_phone(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'tel'):
            if isinstance(vcard.tel, list):
                phone = vcard.tel[0].value if vcard.tel else None
            else:
                phone = vcard.tel.value
            
            # Normalizar: +52 55 1234 5678 → +525512345678
            if phone:
                phone = re.sub(r'[^\d+]', '', phone)
            return phone
        return None
    
    def _get_org(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'org'):
            org = vcard.org.value
            if isinstance(org, list):
                return org[0] if org else None
            return org
        return None
    
    def _get_title(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'title'):
            return vcard.title.value
        return None
    
    def _get_note(self, vcard) -> Optional[str]:
        if hasattr(vcard, 'note'):
            return vcard.note.value
        return None


# ============================================
# 2. CLASIFICADOR CON GPT-4O-MINI (BARATO)
# ============================================

class ContactClassifier:
    """
    Clasifica contactos con GPT-4o-mini
    
    Costo: ~$0.15 por 1M tokens
    Para 15K contactos: ~$2-3 USD total
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    def classify_batch(self, contacts: List[Dict], batch_size: int = 50) -> List[Dict]:
        """
        Clasifica contactos en batch para eficiencia
        
        Output por contacto:
        - tier: 1, 2, 3
        - tema: Inmobiliario, ESG, Manufactura, Academia, etc.
        - zona: CDMX, Monterrey, Querétaro, etc.
        - score_estimado: 0-100
        """
        
        print(f"\n🤖 Clasificando {len(contacts)} contactos con GPT-4o-mini...")
        print(f"   Costo estimado: ${len(contacts) * 0.0002:.2f} USD")
        
        classified = []
        
        for i in tqdm(range(0, len(contacts), batch_size)):
            batch = contacts[i:i+batch_size]
            
            # Preparar prompt
            contacts_text = self._format_batch(batch)
            
            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un asistente que clasifica contactos profesionales.

Para cada contacto, retorna JSON con:
- tier: 1 (CEO/Director/VP), 2 (Gerente/Consultor), 3 (General)
- tema: Inmobiliario, ESG, Manufactura, Academia, Gobierno, Consultoría, Tecnología, Finanzas, u Otro
- zona: CDMX, Monterrey, Guadalajara, Querétaro, Internacional, u Otra
- score_estimado: 0-100 (valor comercial potencial)

Responde SOLO con JSON array, sin explicaciones."""
                    },
                    {
                        "role": "user",
                        "content": f"Clasifica estos contactos:\n\n{contacts_text}"
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parsear respuesta
            try:
                result = json.loads(response.choices[0].message.content)
                
                # Merge con datos originales
                if 'contactos' in result:
                    classifications = result['contactos']
                else:
                    # Si GPT retorna objeto plano, envolver en lista
                    classifications = [result]
                
                for contact, classification in zip(batch, classifications):
                    contact.update({
                        'tier': classification.get('tier', 3),
                        'tema': classification.get('tema', 'Otro'),
                        'zona': classification.get('zona', 'Otra'),
                        'score_estimado': classification.get('score_estimado', 30)
                    })
                    classified.append(contact)
                    
            except json.JSONDecodeError as e:
                # Fallback: clasificación por defecto
                print(f"⚠️  Error JSON batch {i}: {e}")
                for contact in batch:
                    contact.update({
                        'tier': 3,
                        'tema': 'Otro',
                        'zona': 'Otra',
                        'score_estimado': 30
                    })
                    classified.append(contact)
        
        print(f"✅ Clasificación completa")
        return classified
    
    def _format_batch(self, batch: List[Dict]) -> str:
        """Formatea batch para prompt"""
        lines = []
        for i, contact in enumerate(batch, 1):
            line = f"{i}. {contact.get('nombre', 'Sin nombre')}"
            if contact.get('empresa'):
                line += f" - {contact['empresa']}"
            if contact.get('puesto'):
                line += f" ({contact['puesto']})"
            if contact.get('notas'):
                line += f" | Notas: {contact['notas'][:100]}"
            lines.append(line)
        
        return "\n".join(lines)


# ============================================
# 3. KÙZU DATABASE MANAGER
# ============================================

class KuzuContactGraph:
    """
    Kùzu graph database (embebido, sin servidor)
    
    Ventajas:
    - 10-100x más rápido que Neo4j para grafo local
    - Embebido (no requiere servidor)
    - SQL-like (fácil de aprender)
    """
    
    def __init__(self, db_path: str = "./contact_graph_db"):
        self.db_path = db_path
        Path(db_path).mkdir(parents=True, exist_ok=True)
        
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        
        print(f"📊 Kùzu database: {db_path}")
    
    def create_schema(self):
        """Crea esquema de nodos y relaciones"""
        
        print("🏗️  Creando esquema...")
        
        # Tabla Persona
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Persona(
                id STRING PRIMARY KEY,
                nombre STRING,
                email STRING,
                telefono STRING,
                empresa STRING,
                puesto STRING,
                notas STRING,
                tier INT64,
                tema STRING,
                zona STRING,
                score_estimado INT64,
                fuente STRING
            )
        """)
        
        # Tabla Empresa
        self.conn.execute("""
            CREATE NODE TABLE IF NOT EXISTS Empresa(
                nombre STRING PRIMARY KEY
            )
        """)
        
        # Relación TRABAJA_EN
        self.conn.execute("""
            CREATE REL TABLE IF NOT EXISTS TRABAJA_EN(
                FROM Persona TO Empresa
            )
        """)
        
        # Relación CONECTA_CON (entre personas)
        self.conn.execute("""
            CREATE REL TABLE IF NOT EXISTS CONECTA_CON(
                FROM Persona TO Persona,
                tipo STRING
            )
        """)
        
        print("✅ Esquema creado")
    
    def load_contacts(self, contacts: List[Dict]):
        """Carga contactos a Kùzu"""
        
        print(f"\n💾 Cargando {len(contacts)} contactos a Kùzu...")
        
        # Cargar personas
        for contact in tqdm(contacts):
            self.conn.execute("""
                CREATE (p:Persona {
                    id: $id,
                    nombre: $nombre,
                    email: $email,
                    telefono: $telefono,
                    empresa: $empresa,
                    puesto: $puesto,
                    notas: $notas,
                    tier: $tier,
                    tema: $tema,
                    zona: $zona,
                    score_estimado: $score_estimado,
                    fuente: $fuente
                })
            """, parameters={
                'id': contact['id'],
                'nombre': contact.get('nombre', ''),
                'email': contact.get('email', ''),
                'telefono': contact.get('telefono', ''),
                'empresa': contact.get('empresa', ''),
                'puesto': contact.get('puesto', ''),
                'notas': contact.get('notas', ''),
                'tier': contact.get('tier', 3),
                'tema': contact.get('tema', 'Otro'),
                'zona': contact.get('zona', 'Otra'),
                'score_estimado': contact.get('score_estimado', 30),
                'fuente': contact.get('fuente', 'vCard')
            })
            
            # Crear empresa si existe
            if contact.get('empresa'):
                self.conn.execute("""
                    MERGE (e:Empresa {nombre: $nombre})
                """, parameters={'nombre': contact['empresa']})
                
                # Crear relación TRABAJA_EN
                self.conn.execute("""
                    MATCH (p:Persona {id: $pid})
                    MATCH (e:Empresa {nombre: $empresa})
                    CREATE (p)-[:TRABAJA_EN]->(e)
                """, parameters={
                    'pid': contact['id'],
                    'empresa': contact['empresa']
                })
        
        print("✅ Contactos cargados")
    
    def infer_relationships(self):
        """Infiere relaciones entre contactos"""
        
        print("\n🔗 Infiriendo relaciones...")
        
        # Regla 1: Misma empresa → CONECTA_CON (colega)
        result = self.conn.execute("""
            MATCH (p1:Persona)-[:TRABAJA_EN]->(e:Empresa)<-[:TRABAJA_EN]-(p2:Persona)
            WHERE p1.id < p2.id
            CREATE (p1)-[:CONECTA_CON {tipo: 'colega'}]->(p2)
            RETURN COUNT(*) as count
        """)
        
        count = result.get_next()[0]
        print(f"   Colegas (misma empresa): {count}")
    
    def get_stats(self):
        """Estadísticas del grafo"""
        
        print("\n📊 ESTADÍSTICAS DEL GRAFO")
        print("-" * 60)
        
        # Total personas
        result = self.conn.execute("MATCH (p:Persona) RETURN COUNT(*) as count")
        total = result.get_next()[0]
        print(f"Total contactos: {total}")
        
        # Por tier
        result = self.conn.execute("""
            MATCH (p:Persona)
            RETURN p.tier as tier, COUNT(*) as count
            ORDER BY tier
        """)
        print("\nPor Tier:")
        for row in result.get_as_df().itertuples():
            print(f"  Tier {row.tier}: {row.count} ({row.count/total:.1%})")
        
        # Por tema
        result = self.conn.execute("""
            MATCH (p:Persona)
            RETURN p.tema as tema, COUNT(*) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        print("\nTop 10 Temas:")
        for row in result.get_as_df().itertuples():
            print(f"  {row.tema}: {row.count}")
        
        # Por zona
        result = self.conn.execute("""
            MATCH (p:Persona)
            RETURN p.zona as zona, COUNT(*) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        print("\nTop 10 Zonas:")
        for row in result.get_as_df().itertuples():
            print(f"  {row.zona}: {row.count}")
        
        print("\n" + "-" * 60)


# ============================================
# 4. PIPELINE COMPLETO
# ============================================

def run_vcf_pipeline(vcf_path: str, openai_api_key: str, output_dir: str = "./output"):
    """
    Pipeline completo: VCF → Clasificación → Kùzu
    
    Tiempo estimado: 5-10 minutos para 15K contactos
    Costo: ~$2-3 USD (GPT-4o-mini)
    """
    
    print("="*60)
    print("VCF → KÙZU PIPELINE")
    print("="*60)
    print(f"\nInput: {vcf_path}")
    print(f"Output: {output_dir}/contact_graph_db\n")
    
    # Crear directorio de salida
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Parsear VCF
    parser = SimpleVCFParser()
    contacts = parser.parse_vcf(vcf_path)
    
    # Guardar CSV crudo
    df_raw = pd.DataFrame(contacts)
    raw_csv = Path(output_dir) / 'contacts_raw.csv'
    df_raw.to_csv(raw_csv, index=False)
    print(f"💾 Guardado: {raw_csv}")
    
    # 2. Clasificar con GPT-4o-mini
    classifier = ContactClassifier(api_key=openai_api_key)
    contacts_classified = classifier.classify_batch(contacts, batch_size=50)
    
    # Guardar CSV clasificado
    df_classified = pd.DataFrame(contacts_classified)
    classified_csv = Path(output_dir) / 'contacts_classified.csv'
    df_classified.to_csv(classified_csv, index=False)
    print(f"💾 Guardado: {classified_csv}")
    
    # 3. Cargar a Kùzu
    kuzu_db = KuzuContactGraph(db_path=f"{output_dir}/contact_graph_db")
    kuzu_db.create_schema()
    kuzu_db.load_contacts(contacts_classified)
    kuzu_db.infer_relationships()
    
    # 4. Estadísticas
    kuzu_db.get_stats()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETO")
    print("="*60)
    print(f"\nBase de datos Kùzu lista en: {output_dir}/contact_graph_db")
    print("\nConsultas ejemplo:")
    print("  - Tier 1 en CDMX: MATCH (p:Persona) WHERE p.tier = 1 AND p.zona = 'CDMX' RETURN p")
    print("  - Expertos ESG: MATCH (p:Persona) WHERE p.tema = 'ESG' RETURN p ORDER BY p.score_estimado DESC")
    print("\n🚀 Sistema listo para consultas!")


# ============================================
# 5. CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="VCF → Kùzu Pipeline: Construye tu grafo de contactos en 10 minutos"
    )
    parser.add_argument(
        '--vcf',
        type=str,
        required=True,
        help='Ruta al archivo .vcf (exportación de iPhone/Android)'
    )
    parser.add_argument(
        '--openai-key',
        type=str,
        required=True,
        help='OpenAI API key para clasificación con GPT-4o-mini'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Directorio de salida (default: ./output)'
    )
    
    args = parser.parse_args()
    
    # Validar archivo existe
    if not Path(args.vcf).exists():
        print(f"❌ Error: Archivo no encontrado: {args.vcf}")
        return
    
    # Ejecutar pipeline
    run_vcf_pipeline(
        vcf_path=args.vcf,
        openai_api_key=args.openai_key,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
