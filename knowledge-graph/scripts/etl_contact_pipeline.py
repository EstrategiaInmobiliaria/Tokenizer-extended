"""
ETL Pipeline para Carga de 45K Contactos
Fuentes: vCard, LinkedIn, Twitter, WhatsApp
"""

import vobject
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import re
from datetime import datetime

# ============================================
# 1. VCARD PARSER
# ============================================

class VCardParser:
    """
    Parser para archivos .vcf (vCard)
    Fuente típica: Exportación de contactos de iPhone/Android
    """
    
    def parse_vcard_file(self, filepath: str) -> List[Dict]:
        """
        Parsea archivo vCard y retorna lista de contactos
        
        Args:
            filepath: Ruta al archivo .vcf
        
        Returns:
            Lista de diccionarios con datos de contacto
        """
        
        contacts = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            vcard_text = f.read()
        
        # Parsear cada vCard
        for vcard_str in vcard_text.split('BEGIN:VCARD')[1:]:
            vcard_str = 'BEGIN:VCARD' + vcard_str
            
            try:
                vcard = vobject.readOne(vcard_str)
                contact = self._extract_vcard_data(vcard)
                if contact:
                    contacts.append(contact)
            except Exception as e:
                print(f"Error parsing vCard: {e}")
                continue
        
        print(f"✅ Parseados {len(contacts)} contactos de vCard")
        return contacts
    
    def _extract_vcard_data(self, vcard) -> Dict:
        """Extrae campos relevantes de vCard"""
        
        contact = {
            'fuente': 'vCard',
            'unique_id': None,
            'nombre': None,
            'email': None,
            'telefono': None,
            'empresa': None,
            'puesto': None,
            'direccion': None,
            'notas': None
        }
        
        # Nombre completo
        if hasattr(vcard, 'fn'):
            contact['nombre'] = vcard.fn.value
        
        # Email (puede haber múltiples)
        if hasattr(vcard, 'email'):
            if isinstance(vcard.email, list):
                contact['email'] = vcard.email[0].value
            else:
                contact['email'] = vcard.email.value
        
        # Teléfono (puede haber múltiples)
        if hasattr(vcard, 'tel'):
            if isinstance(vcard.tel, list):
                contact['telefono'] = vcard.tel[0].value
            else:
                contact['telefono'] = vcard.tel.value
        
        # Organización
        if hasattr(vcard, 'org'):
            if isinstance(vcard.org.value, list):
                contact['empresa'] = vcard.org.value[0]
            else:
                contact['empresa'] = vcard.org.value
        
        # Título/Puesto
        if hasattr(vcard, 'title'):
            contact['puesto'] = vcard.title.value
        
        # Notas
        if hasattr(vcard, 'note'):
            contact['notas'] = vcard.note.value
        
        # Generar unique_id
        contact['unique_id'] = self._generate_id('vcard', contact['nombre'], contact['email'])
        
        return contact if contact['nombre'] else None
    
    def _generate_id(self, fuente: str, nombre: str, email: str) -> str:
        """Genera ID único combinando fuente + nombre + email"""
        key = f"{fuente}-{nombre or 'unknown'}-{email or 'none'}"
        return re.sub(r'[^\w-]', '', key).lower()


# ============================================
# 2. LINKEDIN PARSER
# ============================================

class LinkedInParser:
    """
    Parser para datos de LinkedIn
    
    Fuentes:
    1. LinkedIn Data Export (GDPR request)
    2. LinkedIn API (con rate limits)
    3. Manual CSV export
    """
    
    def parse_linkedin_export(self, connections_file: str, 
                               profile_file: str = None) -> List[Dict]:
        """
        Parsea exportación GDPR de LinkedIn
        
        Archivos:
        - Connections.csv: Lista de conexiones
        - Profile.csv: Datos del perfil (opcional)
        
        Para obtener:
        LinkedIn → Settings & Privacy → Data Privacy → Get a copy of your data
        """
        
        contacts = []
        
        # Leer archivo de conexiones
        df = pd.read_csv(connections_file)
        
        for _, row in df.iterrows():
            contact = {
                'fuente': 'LinkedIn',
                'unique_id': self._generate_linkedin_id(row),
                'nombre': f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                'email': row.get('Email Address'),
                'empresa': row.get('Company'),
                'puesto': row.get('Position'),
                'linkedin_url': row.get('URL') or self._construct_linkedin_url(row),
                'fecha_conexion': row.get('Connected On'),
                'notas': None
            }
            
            contacts.append(contact)
        
        print(f"✅ Parseados {len(contacts)} contactos de LinkedIn")
        return contacts
    
    def _generate_linkedin_id(self, row: pd.Series) -> str:
        """Genera ID basado en URL de LinkedIn"""
        url = row.get('URL', '')
        if url:
            match = re.search(r'/in/([^/]+)', url)
            if match:
                return f"linkedin-{match.group(1)}"
        
        # Fallback: nombre + email
        return f"linkedin-{row.get('First Name', '').lower()}-{row.get('Last Name', '').lower()}"
    
    def _construct_linkedin_url(self, row: pd.Series) -> str:
        """Construye URL de LinkedIn si no está disponible"""
        first = row.get('First Name', '').lower()
        last = row.get('Last Name', '').lower()
        return f"https://linkedin.com/in/{first}-{last}"


# ============================================
# 3. TWITTER/X PARSER
# ============================================

class TwitterParser:
    """
    Parser para seguidores de Twitter/X
    
    Fuentes:
    1. Twitter API v2 (requiere API key)
    2. Exportación manual de seguidores
    """
    
    def parse_twitter_following(self, following_file: str) -> List[Dict]:
        """
        Parsea lista de cuentas que sigues en Twitter
        
        Formato esperado: JSON de Twitter API
        """
        
        contacts = []
        
        with open(following_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Formato: {"data": [{"id": "123", "name": "...", "username": "..."}]}
        users = data.get('data', [])
        
        for user in users:
            contact = {
                'fuente': 'Twitter',
                'unique_id': f"twitter-{user['username']}",
                'nombre': user.get('name'),
                'twitter_handle': f"@{user['username']}",
                'twitter_id': user['id'],
                'biografia': user.get('description'),
                'ubicacion': user.get('location'),
                'seguidores': user.get('public_metrics', {}).get('followers_count'),
                'verificado': user.get('verified', False)
            }
            
            contacts.append(contact)
        
        print(f"✅ Parseados {len(contacts)} contactos de Twitter")
        return contacts


# ============================================
# 4. WHATSAPP PARSER
# ============================================

class WhatsAppParser:
    """
    Parser para contactos de WhatsApp
    
    Fuentes:
    1. Exportación de chats (Settings → Chats → Export chat)
    2. WhatsApp Business API
    """
    
    def parse_whatsapp_contacts(self, contacts_file: str) -> List[Dict]:
        """
        Parsea lista de contactos de WhatsApp
        
        Formato esperado: CSV con columnas:
        - nombre
        - numero
        - ultimo_mensaje
        - fecha_ultimo_mensaje
        """
        
        contacts = []
        
        df = pd.read_csv(contacts_file)
        
        for _, row in df.iterrows():
            contact = {
                'fuente': 'WhatsApp',
                'unique_id': f"whatsapp-{self._normalize_phone(row['numero'])}",
                'nombre': row.get('nombre'),
                'whatsapp': row.get('numero'),
                'telefono': row.get('numero'),
                'ultimo_mensaje': row.get('ultimo_mensaje'),
                'fecha_ultimo_mensaje': row.get('fecha_ultimo_mensaje'),
                'frecuencia_mensajes': row.get('total_mensajes', 0)
            }
            
            contacts.append(contact)
        
        print(f"✅ Parseados {len(contacts)} contactos de WhatsApp")
        return contacts
    
    def _normalize_phone(self, phone: str) -> str:
        """Normaliza número de teléfono: +52 55 1234 5678 → 5512345678"""
        return re.sub(r'[^\d]', '', phone)[-10:]


# ============================================
# 5. ETL MASTER PIPELINE
# ============================================

class ContactETLPipeline:
    """
    Pipeline maestro para ingesta de 45K contactos desde todas las fuentes
    """
    
    def __init__(self, output_dir: str = '/workspace/knowledge-graph/data/contacts'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.vcard_parser = VCardParser()
        self.linkedin_parser = LinkedInParser()
        self.twitter_parser = TwitterParser()
        self.whatsapp_parser = WhatsAppParser()
    
    def run_full_pipeline(self, source_files: Dict[str, str]) -> pd.DataFrame:
        """
        Ejecuta pipeline completo de ETL
        
        Args:
            source_files: {
                'vcard': '/path/to/contacts.vcf',
                'linkedin': '/path/to/Connections.csv',
                'twitter': '/path/to/following.json',
                'whatsapp': '/path/to/whatsapp_contacts.csv'
            }
        
        Returns:
            DataFrame unificado con todos los contactos
        """
        
        all_contacts = []
        
        print("="*80)
        print("INICIANDO ETL PIPELINE")
        print("="*80 + "\n")
        
        # 1. vCard
        if source_files.get('vcard'):
            print("📇 Procesando vCard...")
            vcard_contacts = self.vcard_parser.parse_vcard_file(source_files['vcard'])
            all_contacts.extend(vcard_contacts)
            print()
        
        # 2. LinkedIn
        if source_files.get('linkedin'):
            print("💼 Procesando LinkedIn...")
            linkedin_contacts = self.linkedin_parser.parse_linkedin_export(source_files['linkedin'])
            all_contacts.extend(linkedin_contacts)
            print()
        
        # 3. Twitter
        if source_files.get('twitter'):
            print("🐦 Procesando Twitter...")
            twitter_contacts = self.twitter_parser.parse_twitter_following(source_files['twitter'])
            all_contacts.extend(twitter_contacts)
            print()
        
        # 4. WhatsApp
        if source_files.get('whatsapp'):
            print("💬 Procesando WhatsApp...")
            whatsapp_contacts = self.whatsapp_parser.parse_whatsapp_contacts(source_files['whatsapp'])
            all_contacts.extend(whatsapp_contacts)
            print()
        
        # Convertir a DataFrame
        df = pd.DataFrame(all_contacts)
        
        print("="*80)
        print(f"✅ PIPELINE COMPLETO: {len(df)} contactos de {len(source_files)} fuentes")
        print("="*80 + "\n")
        
        # Guardar datos crudos
        raw_output = self.output_dir / 'contacts_raw.csv'
        df.to_csv(raw_output, index=False)
        print(f"💾 Guardado: {raw_output}\n")
        
        # Estadísticas
        self._print_statistics(df)
        
        return df
    
    def _print_statistics(self, df: pd.DataFrame):
        """Imprime estadísticas del dataset"""
        
        print("📊 ESTADÍSTICAS:")
        print("-" * 80)
        print(f"Total contactos: {len(df)}")
        print(f"\nPor fuente:")
        print(df['fuente'].value_counts().to_string())
        
        print(f"\nContactos con email: {df['email'].notna().sum()} ({df['email'].notna().mean():.1%})")
        print(f"Contactos con teléfono: {df['telefono'].notna().sum()} ({df['telefono'].notna().mean():.1%})")
        print(f"Contactos con empresa: {df['empresa'].notna().sum()} ({df['empresa'].notna().mean():.1%})")
        print(f"Contactos con puesto: {df['puesto'].notna().sum()} ({df['puesto'].notna().mean():.1%})")
        
        print("\n" + "="*80 + "\n")


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    
    # Configurar rutas a archivos fuente
    source_files = {
        'vcard': '/workspace/knowledge-graph/data/sources/contacts.vcf',
        'linkedin': '/workspace/knowledge-graph/data/sources/Connections.csv',
        'twitter': '/workspace/knowledge-graph/data/sources/following.json',
        'whatsapp': '/workspace/knowledge-graph/data/sources/whatsapp_contacts.csv'
    }
    
    # Ejecutar pipeline
    pipeline = ContactETLPipeline()
    df_contacts = pipeline.run_full_pipeline(source_files)
    
    # Siguiente paso: Deduplicación
    print("📍 Siguiente paso:")
    print("   python scripts/deduplicate_contacts.py --input data/contacts/contacts_raw.csv")
