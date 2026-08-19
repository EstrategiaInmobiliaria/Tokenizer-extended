#!/usr/bin/env python3
"""
Pipeline principal - Procesa VCF, clasifica y carga a Supabase + Kùzu

USO:
    python main_pipeline.py --vcf /path/to/contacts.vcf
    python main_pipeline.py --linkedin /path/to/Connections.csv
    python main_pipeline.py --instagram /path/to/instagram_export/
"""
import argparse
from pathlib import Path
import sys
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))

from vcf_processor.vcf_parser import VCFParser
from vcf_processor.deduplicator import ContactDeduplicator
from vcf_processor.linkedin_processor import LinkedInProcessor
from vcf_processor.instagram_processor import InstagramProcessor
from classification.gpt_classifier import GPTClassifier
from database.supabase_client import SupabaseContactManager
from graph_engine.kuzu_graph import KuzuGraphEngine

load_dotenv()
console = Console()


def process_vcf_pipeline(vcf_path: Path, skip_classification: bool = False):
    """Pipeline completo para VCF"""
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]VCF PROCESSING PIPELINE[/bold cyan]")
    console.print("="*60 + "\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task1 = progress.add_task("Parsing VCF...", total=None)
        parser = VCFParser()
        
        if vcf_path.is_file():
            contacts = parser.parse_file(vcf_path)
        else:
            contacts = parser.parse_directory(vcf_path)
        
        df = parser.to_dataframe()
        progress.update(task1, completed=True)
        
        task2 = progress.add_task("Deduplicating contacts...", total=None)
        dedup = ContactDeduplicator()
        df_dedup = dedup.deduplicate(df, threshold=0.8)
        dedup.show_duplicates_preview(df_dedup, limit=3)
        
        df_merged = dedup.merge_duplicates(df_dedup)
        progress.update(task2, completed=True)
        
        if not skip_classification:
            task3 = progress.add_task("Classifying with GPT-4o-mini...", total=None)
            classifier = GPTClassifier()
            contacts_dicts = df_merged.to_dict('records')
            
            classifications = classifier.classify_batch(contacts_dicts, show_progress=False)
            df_classified = classifier.add_classifications_to_df(df_merged, classifications)
            progress.update(task3, completed=True)
        else:
            df_classified = df_merged
            df_classified['tier'] = 'Tier 3'
            df_classified['temas'] = 'Otro'
            df_classified['zona'] = 'Desconocida'
        
        task4 = progress.add_task("Uploading to Supabase...", total=None)
        supabase = SupabaseContactManager()
        uploaded = supabase.upload_contacts(df_classified)
        progress.update(task4, completed=True)
        
        task5 = progress.add_task("Building Kùzu graph...", total=None)
        df_with_ids = supabase.get_all_contacts()
        graph = KuzuGraphEngine()
        graph.load_contacts_from_df(df_with_ids)
        progress.update(task5, completed=True)
    
    console.print("\n[bold green]✓ VCF PIPELINE COMPLETE[/bold green]")
    console.print(f"  • Processed: {len(df)} contacts")
    console.print(f"  • After deduplication: {len(df_merged)} unique contacts")
    console.print(f"  • Uploaded to Supabase: {uploaded} contacts")
    
    return df_classified


def process_linkedin_pipeline(csv_path: Path, skip_classification: bool = False):
    """Pipeline para LinkedIn CSV"""
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]LINKEDIN PROCESSING PIPELINE[/bold cyan]")
    console.print("="*60 + "\n")
    
    processor = LinkedInProcessor()
    processor.load_csv(csv_path)
    
    processor.get_top_companies(limit=15)
    
    df_normalized = processor.normalize_to_contacts()
    
    if not skip_classification:
        classifier = GPTClassifier()
        contacts_dicts = df_normalized.to_dict('records')
        classifications = classifier.classify_batch(contacts_dicts)
        df_classified = classifier.add_classifications_to_df(df_normalized, classifications)
    else:
        df_classified = df_normalized
        df_classified['tier'] = 'Tier 3'
        df_classified['temas'] = 'Otro'
        df_classified['zona'] = 'Desconocida'
    
    supabase = SupabaseContactManager()
    uploaded = supabase.upload_contacts(df_classified)
    
    df_with_ids = supabase.get_all_contacts()
    graph = KuzuGraphEngine()
    graph.load_contacts_from_df(df_with_ids)
    
    console.print("\n[bold green]✓ LINKEDIN PIPELINE COMPLETE[/bold green]")
    console.print(f"  • Uploaded: {uploaded} contacts")
    
    return df_classified


def process_instagram_pipeline(export_path: Path):
    """Pipeline para Instagram export"""
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]INSTAGRAM PROCESSING PIPELINE[/bold cyan]")
    console.print("="*60 + "\n")
    
    processor = InstagramProcessor()
    processor.load_json_export(export_path)
    
    processor.show_stats()
    
    df_normalized = processor.normalize_to_contacts()
    
    df_normalized['tier'] = 'Tier 3'
    df_normalized.loc[df_normalized.get('is_mutual_follow', False), 'tier'] = 'Tier 2'
    df_normalized['temas'] = 'Redes Sociales'
    df_normalized['zona'] = 'Desconocida'
    
    supabase = SupabaseContactManager()
    uploaded = supabase.upload_contacts(df_normalized)
    
    df_with_ids = supabase.get_all_contacts()
    graph = KuzuGraphEngine()
    graph.load_contacts_from_df(df_with_ids)
    
    console.print("\n[bold green]✓ INSTAGRAM PIPELINE COMPLETE[/bold green]")
    console.print(f"  • Uploaded: {uploaded} contacts")
    
    return df_normalized


def analyze_network():
    """Análisis de red completo"""
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]NETWORK ANALYSIS[/bold cyan]")
    console.print("="*60 + "\n")
    
    supabase = SupabaseContactManager()
    df_contacts = supabase.get_all_contacts()
    
    console.print(f"[cyan]Total contacts in database: {len(df_contacts)}[/cyan]\n")
    
    tier_dist = df_contacts['tier'].value_counts()
    console.print("[cyan]Distribution by Tier:[/cyan]")
    for tier, count in tier_dist.items():
        console.print(f"  • {tier}: {count}")
    
    zona_dist = df_contacts['zona'].value_counts().head(10)
    console.print("\n[cyan]Top Zones:[/cyan]")
    for zona, count in zona_dist.items():
        console.print(f"  • {zona}: {count}")
    
    graph = KuzuGraphEngine()
    graph.load_contacts_from_df(df_contacts)
    
    console.print("\n[cyan]Detecting communities...[/cyan]")
    communities = graph.detect_communities()
    
    central = graph.get_central_contacts(limit=10)
    console.print("\n[cyan]Most connected contacts:[/cyan]")
    console.print(central.to_string(index=False))
    
    inactive = supabase.get_inactive_contacts(days=180)
    console.print(f"\n[yellow]Inactive contacts (6+ months): {len(inactive)}[/yellow]")


def main():
    parser = argparse.ArgumentParser(
        description="Network Management System - Contact Processing Pipeline"
    )
    
    parser.add_argument(
        '--vcf',
        type=Path,
        help='Path to VCF file or directory'
    )
    
    parser.add_argument(
        '--linkedin',
        type=Path,
        help='Path to LinkedIn Connections.csv'
    )
    
    parser.add_argument(
        '--instagram',
        type=Path,
        help='Path to Instagram export directory'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run network analysis'
    )
    
    parser.add_argument(
        '--skip-classification',
        action='store_true',
        help='Skip GPT classification (faster, less accurate)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.vcf:
            if not args.vcf.exists():
                console.print(f"[red]Error: VCF path not found: {args.vcf}[/red]")
                sys.exit(1)
            process_vcf_pipeline(args.vcf, args.skip_classification)
        
        elif args.linkedin:
            if not args.linkedin.exists():
                console.print(f"[red]Error: LinkedIn CSV not found: {args.linkedin}[/red]")
                sys.exit(1)
            process_linkedin_pipeline(args.linkedin, args.skip_classification)
        
        elif args.instagram:
            if not args.instagram.exists():
                console.print(f"[red]Error: Instagram export not found: {args.instagram}[/red]")
                sys.exit(1)
            process_instagram_pipeline(args.instagram)
        
        elif args.analyze:
            analyze_network()
        
        else:
            parser.print_help()
            console.print("\n[yellow]Examples:[/yellow]")
            console.print("  python main_pipeline.py --vcf /path/to/contacts.vcf")
            console.print("  python main_pipeline.py --linkedin /path/to/Connections.csv")
            console.print("  python main_pipeline.py --instagram /path/to/instagram_export/")
            console.print("  python main_pipeline.py --analyze")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
