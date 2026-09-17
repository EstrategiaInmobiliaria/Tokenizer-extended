"""
VCF Parser - Extrae contactos de archivos VCF (vCard) y los normaliza
"""
import vobject
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import re
from rich.console import Console
from rich.progress import track

console = Console()


@dataclass
class Contact:
    """Estructura de contacto normalizado"""
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phones: List[str] = None
    emails: List[str] = None
    addresses: List[str] = None
    notes: Optional[str] = None
    source: str = "vcf"
    
    def __post_init__(self):
        if self.phones is None:
            self.phones = []
        if self.emails is None:
            self.emails = []
        if self.addresses is None:
            self.addresses = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


class VCFParser:
    """Parser para archivos VCF con normalización de datos"""
    
    def __init__(self):
        self.contacts: List[Contact] = []
    
    def normalize_phone(self, phone: str) -> str:
        """Normaliza números telefónicos"""
        phone = re.sub(r'[^\d+]', '', phone)
        
        if phone.startswith('52') and len(phone) == 12:
            return f"+{phone}"
        elif phone.startswith('+52') and len(phone) == 13:
            return phone
        elif len(phone) == 10:
            return f"+52{phone}"
        
        return phone if phone else None
    
    def normalize_email(self, email: str) -> str:
        """Normaliza emails"""
        email = email.lower().strip()
        if '@' in email:
            return email
        return None
    
    def extract_contact(self, vcard) -> Optional[Contact]:
        """Extrae información de un vCard individual"""
        try:
            contact = Contact()
            
            if hasattr(vcard, 'fn'):
                contact.full_name = str(vcard.fn.value).strip()
            
            if hasattr(vcard, 'n'):
                name = vcard.n.value
                contact.last_name = name.family if name.family else None
                contact.first_name = name.given if name.given else None
            
            if hasattr(vcard, 'org'):
                orgs = vcard.org.value
                if isinstance(orgs, list) and orgs:
                    contact.company = orgs[0] if orgs[0] else None
                elif isinstance(orgs, str):
                    contact.company = orgs
            
            if hasattr(vcard, 'title'):
                contact.title = str(vcard.title.value).strip()
            
            if hasattr(vcard, 'tel_list'):
                for tel in vcard.tel_list:
                    normalized = self.normalize_phone(tel.value)
                    if normalized:
                        contact.phones.append(normalized)
            
            if hasattr(vcard, 'email_list'):
                for email in vcard.email_list:
                    normalized = self.normalize_email(email.value)
                    if normalized:
                        contact.emails.append(normalized)
            
            if hasattr(vcard, 'adr_list'):
                for adr in vcard.adr_list:
                    if adr.value:
                        addr_parts = [
                            str(p) for p in [
                                adr.value.street,
                                adr.value.city,
                                adr.value.region,
                                adr.value.code,
                                adr.value.country
                            ] if p
                        ]
                        if addr_parts:
                            contact.addresses.append(", ".join(addr_parts))
            
            if hasattr(vcard, 'note'):
                contact.notes = str(vcard.note.value).strip()
            
            if not contact.full_name and not contact.first_name and not contact.emails:
                return None
            
            return contact
            
        except Exception as e:
            console.print(f"[yellow]Warning: Error parsing contact: {e}[/yellow]")
            return None
    
    def parse_file(self, vcf_path: Path) -> List[Contact]:
        """Parsea un archivo VCF y retorna lista de contactos"""
        console.print(f"\n[cyan]Parsing VCF file:[/cyan] {vcf_path}")
        
        try:
            with open(vcf_path, 'r', encoding='utf-8') as f:
                vcf_content = f.read()
        except UnicodeDecodeError:
            with open(vcf_path, 'r', encoding='latin-1') as f:
                vcf_content = f.read()
        
        vcards = vobject.readComponents(vcf_content)
        
        contacts = []
        for vcard in track(list(vcards), description="Processing contacts"):
            contact = self.extract_contact(vcard)
            if contact:
                contacts.append(contact)
        
        self.contacts.extend(contacts)
        
        console.print(f"[green]✓ Extracted {len(contacts)} contacts[/green]")
        return contacts
    
    def parse_directory(self, directory: Path) -> List[Contact]:
        """Parsea todos los archivos VCF en un directorio"""
        vcf_files = list(directory.glob("*.vcf")) + list(directory.glob("*.vcard"))
        
        console.print(f"\n[cyan]Found {len(vcf_files)} VCF files[/cyan]")
        
        all_contacts = []
        for vcf_file in vcf_files:
            contacts = self.parse_file(vcf_file)
            all_contacts.extend(contacts)
        
        return all_contacts
    
    def to_dataframe(self):
        """Convierte contactos a pandas DataFrame"""
        import pandas as pd
        
        if not self.contacts:
            return pd.DataFrame()
        
        data = []
        for contact in self.contacts:
            base = contact.to_dict()
            base['phone_primary'] = base['phones'][0] if base['phones'] else None
            base['email_primary'] = base['emails'][0] if base['emails'] else None
            base['address_primary'] = base['addresses'][0] if base['addresses'] else None
            
            base['phones'] = '|'.join(base['phones']) if base['phones'] else None
            base['emails'] = '|'.join(base['emails']) if base['emails'] else None
            base['addresses'] = '|'.join(base['addresses']) if base['addresses'] else None
            
            data.append(base)
        
        return pd.DataFrame(data)


if __name__ == "__main__":
    parser = VCFParser()
    
    import sys
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.is_file():
            contacts = parser.parse_file(path)
        else:
            contacts = parser.parse_directory(path)
        
        df = parser.to_dataframe()
        console.print(f"\n[green]Total contacts parsed: {len(df)}[/green]")
        console.print(df.head())
    else:
        console.print("[red]Usage: python vcf_parser.py <vcf_file_or_directory>[/red]")
