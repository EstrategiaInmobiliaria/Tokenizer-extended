"""
Interfaz de línea de comandos.

    python -m master_blueprint.research_agent "tu pregunta" --out informe.md

Imprime el progreso en stderr y el informe en stdout, de modo que se puede
redirigir la salida a un archivo sin que se mezcle con las trazas.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .agent import AgentConfig, ResearchAgent
from .citations import CitationRegistry
from .models import SubQuestionKind
from .report import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research_agent",
        description=(
            "Agente de investigación web multi-paso: descompone la pregunta, busca "
            "en varias rondas, sintetiza las fuentes y cita cada afirmación."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            '  python -m master_blueprint.research_agent "secuenciación de productos en líneas de empaque"\n'
            '  python -m master_blueprint.research_agent "Last Planner System" --rounds 3 --out informe.md\n'
            '  python -m master_blueprint.research_agent "TSP con restricciones MTZ" --kinds metodo contraste\n'
        ),
    )
    parser.add_argument("question", help="Pregunta de investigación")
    parser.add_argument("--rounds", type=int, default=2, help="Rondas de búsqueda (def. 2)")
    parser.add_argument("--results", type=int, default=8, help="Resultados por consulta y proveedor (def. 8)")
    parser.add_argument(
        "--kinds",
        nargs="+",
        choices=[kind.value for kind in SubQuestionKind],
        help="Limita los tipos de sub-pregunta (def. los cinco)",
    )
    parser.add_argument("--lang", default="en", help="Idioma de Wikipedia (def. en)")
    parser.add_argument("--title", help="Título del informe")
    parser.add_argument("--out", type=Path, help="Archivo Markdown de salida")
    parser.add_argument("--json", dest="json_out", type=Path, help="Archivo JSON de salida (auditoría)")
    parser.add_argument("--cache-dir", help="Directorio de caché HTTP")
    parser.add_argument("--offline", action="store_true", help="Usa sólo la caché, sin red")
    parser.add_argument("--no-audit", action="store_true", help="Omite el registro de auditoría")
    parser.add_argument("--quiet", action="store_true", help="Silencia el progreso")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    kinds: Optional[List[SubQuestionKind]] = (
        [SubQuestionKind(value) for value in args.kinds] if args.kinds else None
    )

    config = AgentConfig(
        rounds=max(1, args.rounds),
        results_per_query=max(1, args.results),
        lang=args.lang,
        cache_dir=args.cache_dir,
        offline=args.offline,
        kinds=kinds,
    )

    def progress(message: str) -> None:
        if not args.quiet:
            print(message, file=sys.stderr, flush=True)

    try:
        agent = ResearchAgent(config=config)
        report = agent.research(args.question, on_progress=progress)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.", file=sys.stderr)
        return 130

    markdown = render_markdown(
        report,
        registry=CitationRegistry(),
        title=args.title,
        include_audit=not args.no_audit,
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        progress(f"Informe escrito en {args.out}")
    else:
        print(markdown)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(render_json(report), encoding="utf-8")
        progress(f"Auditoría JSON escrita en {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
