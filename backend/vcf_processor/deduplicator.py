"""
Deduplicador usando Splink - Detecta y fusiona contactos duplicados
"""
import pandas as pd
import splink.duckdb.duckdb_comparison_library as cl
from splink.duckdb.duckdb_linker import DuckDBLinker
from typing import List, Dict
from rich.console import Console
from rich.table import Table

console = Console()


class ContactDeduplicator:
    """Deduplicador de contactos usando Splink con DuckDB"""
    
    def __init__(self):
        self.linker = None
        self.settings = self._get_splink_settings()
    
    def _get_splink_settings(self) -> Dict:
        """Configuración de Splink para matching de contactos"""
        return {
            "link_type": "dedupe_only",
            "comparisons": [
                cl.exact_match("email_primary", term_frequency_adjustments=True),
                cl.levenshtein_at_thresholds(
                    "full_name",
                    distance_threshold_or_thresholds=[1, 2],
                    term_frequency_adjustments=True
                ),
                cl.jaro_winkler_at_thresholds(
                    "full_name",
                    distance_threshold_or_thresholds=[0.9, 0.8],
                    term_frequency_adjustments=True
                ),
                cl.exact_match("phone_primary", term_frequency_adjustments=True),
                cl.jaro_winkler_at_thresholds(
                    "company",
                    distance_threshold_or_thresholds=[0.9],
                    term_frequency_adjustments=True
                ),
            ],
            "blocking_rules_to_generate_predictions": [
                "l.email_primary = r.email_primary",
                "l.phone_primary = r.phone_primary",
                "substr(l.full_name, 1, 3) = substr(r.full_name, 1, 3)",
                "l.company = r.company",
            ],
            "retain_matching_columns": True,
            "retain_intermediate_calculation_columns": False,
            "max_iterations": 10,
            "em_convergence": 0.01,
        }
    
    def deduplicate(self, df: pd.DataFrame, threshold: float = 0.8) -> pd.DataFrame:
        """
        Deduplica contactos usando probabilistic matching
        
        Args:
            df: DataFrame con contactos
            threshold: Umbral de probabilidad para considerar match (0-1)
        
        Returns:
            DataFrame deduplicado con cluster_id para agrupar duplicados
        """
        console.print("\n[cyan]Starting deduplication with Splink...[/cyan]")
        
        df = df.copy()
        df['unique_id'] = range(len(df))
        
        required_cols = ['full_name', 'email_primary', 'phone_primary', 'company']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        
        df['full_name'] = df['full_name'].fillna('').astype(str)
        df['email_primary'] = df['email_primary'].fillna('').astype(str)
        df['phone_primary'] = df['phone_primary'].fillna('').astype(str)
        df['company'] = df['company'].fillna('').astype(str)
        
        self.linker = DuckDBLinker(
            df,
            self.settings,
            input_table_aliases="contacts"
        )
        
        console.print("[yellow]Training Splink model...[/yellow]")
        
        try:
            self.linker.estimate_u_using_random_sampling(max_pairs=1e6)
            
            blocking_rules_for_training = [
                "l.email_primary = r.email_primary",
                "l.phone_primary = r.phone_primary",
            ]
            
            for rule in blocking_rules_for_training:
                try:
                    self.linker.estimate_parameters_using_expectation_maximisation(
                        rule,
                        estimate_without_term_frequencies=True
                    )
                except Exception as e:
                    console.print(f"[yellow]Skipping rule '{rule}': {e}[/yellow]")
        
        except Exception as e:
            console.print(f"[yellow]Training warning: {e}[/yellow]")
        
        console.print("[yellow]Finding duplicates...[/yellow]")
        predictions = self.linker.predict(threshold_match_probability=threshold)
        
        clusters = self.linker.cluster_pairwise_predictions_at_threshold(
            predictions,
            threshold_match_probability=threshold
        )
        
        clusters_df = clusters.as_pandas_dataframe()
        
        if clusters_df.empty:
            console.print("[green]No duplicates found - all contacts are unique[/green]")
            df['cluster_id'] = df['unique_id']
            return df
        
        cluster_map = dict(zip(
            clusters_df['unique_id'],
            clusters_df['cluster_id']
        ))
        
        df['cluster_id'] = df['unique_id'].map(cluster_map).fillna(df['unique_id']).astype(int)
        
        duplicate_clusters = df.groupby('cluster_id').size()
        num_duplicates = (duplicate_clusters > 1).sum()
        total_duplicate_records = duplicate_clusters[duplicate_clusters > 1].sum()
        
        console.print(f"\n[green]✓ Deduplication complete[/green]")
        console.print(f"  • Found {num_duplicates} groups of duplicates")
        console.print(f"  • Total duplicate records: {total_duplicate_records}")
        console.print(f"  • Unique contacts: {len(duplicate_clusters)}")
        
        return df
    
    def merge_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fusiona contactos duplicados en un solo registro por cluster
        
        Estrategia de fusión:
        - Toma el valor más completo (no nulo/vacío) de cada campo
        - Combina listas (emails, phones, addresses)
        """
        console.print("\n[cyan]Merging duplicate contacts...[/cyan]")
        
        def merge_group(group: pd.DataFrame) -> pd.Series:
            """Fusiona un grupo de contactos duplicados"""
            
            def get_best_value(series: pd.Series) -> str:
                non_null = series.dropna()
                if non_null.empty:
                    return None
                non_empty = non_null[non_null.astype(str).str.strip() != '']
                if non_empty.empty:
                    return non_null.iloc[0]
                return non_empty.iloc[0]
            
            def merge_list_field(series: pd.Series) -> str:
                all_values = []
                for val in series.dropna():
                    if isinstance(val, str) and val.strip():
                        all_values.extend(val.split('|'))
                unique_values = list(dict.fromkeys([v for v in all_values if v]))
                return '|'.join(unique_values) if unique_values else None
            
            merged = pd.Series({
                'full_name': get_best_value(group['full_name']),
                'first_name': get_best_value(group['first_name']),
                'last_name': get_best_value(group['last_name']),
                'company': get_best_value(group['company']),
                'title': get_best_value(group['title']),
                'phones': merge_list_field(group['phones']),
                'emails': merge_list_field(group['emails']),
                'addresses': merge_list_field(group['addresses']),
                'phone_primary': get_best_value(group['phone_primary']),
                'email_primary': get_best_value(group['email_primary']),
                'address_primary': get_best_value(group['address_primary']),
                'notes': get_best_value(group['notes']),
                'source': get_best_value(group['source']),
                'duplicate_count': len(group),
                'cluster_id': group['cluster_id'].iloc[0]
            })
            
            return merged
        
        merged_df = df.groupby('cluster_id').apply(merge_group).reset_index(drop=True)
        
        console.print(f"[green]✓ Merged {len(df)} records into {len(merged_df)} unique contacts[/green]")
        
        return merged_df
    
    def show_duplicates_preview(self, df: pd.DataFrame, limit: int = 5):
        """Muestra preview de duplicados encontrados"""
        
        duplicate_clusters = df[df.duplicated(subset=['cluster_id'], keep=False)]
        
        if duplicate_clusters.empty:
            console.print("[green]No duplicates to show[/green]")
            return
        
        console.print("\n[cyan]Preview of duplicate groups:[/cyan]\n")
        
        for cluster_id in duplicate_clusters['cluster_id'].unique()[:limit]:
            group = df[df['cluster_id'] == cluster_id]
            
            table = Table(title=f"Cluster {cluster_id} ({len(group)} contacts)")
            table.add_column("Name", style="cyan")
            table.add_column("Email", style="magenta")
            table.add_column("Phone", style="green")
            table.add_column("Company", style="yellow")
            
            for _, row in group.iterrows():
                table.add_row(
                    str(row.get('full_name', ''))[:30],
                    str(row.get('email_primary', ''))[:30],
                    str(row.get('phone_primary', ''))[:15],
                    str(row.get('company', ''))[:20]
                )
            
            console.print(table)
            console.print()


if __name__ == "__main__":
    console.print("[red]This module should be imported, not run directly[/red]")
    console.print("Use: from deduplicator import ContactDeduplicator")
