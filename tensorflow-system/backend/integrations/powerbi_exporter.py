"""
Exportación automática TensorFlow → Power BI

Arquitectura desacoplada (recomendada):
  TensorFlow → DataFrame estructurado → Repositorio central (SQL)
                                      → Power BI (Import / DirectQuery)

Alternativa streaming:
  TensorFlow → Push Dataset API de Power BI (tiempo real)

No ejecuta Python dentro de Power Query (evita Personal Gateway).
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# ---------------------------------------------------------------------------
# 1. Estructurar predicciones en DataFrame
# ---------------------------------------------------------------------------

class PredictionRowBuilder:
    """
    Empaqueta salidas del modelo en filas planas para Power BI.

    Campos obligatorios para tendencias e históricos:
    - id_registro (UUID o ID de negocio)
    - categoria / modelo
    - probabilidad / métricas numéricas
    - fecha_prediccion (ISO UTC)
    """

    CATEGORY_SCHEMAS = {
        "real_estate": {
            "probabilidad": "probabilidad_venta_12m",
            "metricas": ["precio_estimado", "dias_estimados"],
            "recomendacion_key": "recomendacion",
        },
        "social_media": {
            "probabilidad": "probabilidad_viral",
            "metricas": ["engagement_score", "alcance_estimado"],
            "recomendacion_key": "recomendacion",
        },
        "personal_tco": {
            "probabilidad": None,
            "metricas": [
                "tco_total_3_anos",
                "costo_operacion_3_anos",
                "valor_residual_3_anos",
                "costo_mensual_promedio",
            ],
            "recomendacion_key": "recomendacion",
        },
        "personal_tennis": {
            "probabilidad": "probabilidad_victoria",
            "metricas": ["tension_kg", "mejora_vs_promedio"],
            "recomendacion_key": "pelota",
        },
    }

    @staticmethod
    def utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def build_row(
        cls,
        *,
        category: str,
        model: str,
        prediction: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None,
        id_registro: Optional[str] = None,
        id_negocio: Optional[str] = None,
        confidence_score: Optional[float] = None,
        batch_id: Optional[str] = None,
        fecha_prediccion: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Construye una fila plana lista para SQL / Push Dataset."""
        schema = cls.CATEGORY_SCHEMAS.get(category, {})
        prob_key = schema.get("probabilidad")
        probabilidad = None
        if prob_key and prob_key in prediction:
            probabilidad = float(prediction[prob_key])
        elif confidence_score is not None:
            probabilidad = float(confidence_score)

        metricas = schema.get("metricas", [])
        recomendacion_key = schema.get("recomendacion_key", "recomendacion")

        row: Dict[str, Any] = {
            "id_registro": id_registro or str(uuid.uuid4()),
            "id_negocio": id_negocio or "",
            "categoria": category,
            "modelo": model,
            "probabilidad": probabilidad,
            "confianza": float(confidence_score) if confidence_score is not None else probabilidad,
            "recomendacion": str(prediction.get(recomendacion_key, "")),
            "fecha_prediccion": fecha_prediccion or cls.utc_now_iso(),
            "batch_id": batch_id or "",
            "input_json": json.dumps(input_data or {}, ensure_ascii=False),
            "prediction_json": json.dumps(prediction, ensure_ascii=False),
        }

        for metric in metricas:
            value = prediction.get(metric)
            if isinstance(value, (int, float)):
                row[metric] = float(value)
            elif value is not None:
                row[metric] = value
            else:
                row[metric] = None

        # Campos de input frecuentes aplanados (útiles en Power BI)
        if input_data:
            for key in (
                "ubicacion",
                "precio_m2",
                "cap_rate",
                "tipo_contenido",
                "tema_categoria",
                "hora",
                "dia_semana",
            ):
                if key in input_data:
                    row[f"input_{key}"] = input_data[key]

        return row

    @classmethod
    def to_dataframe(cls, rows: Sequence[Dict[str, Any]]) -> pd.DataFrame:
        """Convierte filas a DataFrame tipado para Power BI / SQL."""
        if not rows:
            return pd.DataFrame(
                columns=[
                    "id_registro",
                    "id_negocio",
                    "categoria",
                    "modelo",
                    "probabilidad",
                    "confianza",
                    "recomendacion",
                    "fecha_prediccion",
                    "batch_id",
                ]
            )

        df = pd.DataFrame(list(rows))
        if "fecha_prediccion" in df.columns:
            df["fecha_prediccion"] = pd.to_datetime(df["fecha_prediccion"], utc=True)
        for col in ("probabilidad", "confianza"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df


# ---------------------------------------------------------------------------
# 2. Repositorio central (SQLAlchemy)
# ---------------------------------------------------------------------------

class DatabaseExporter:
    """
    Persiste predicciones en un repositorio central.

    Soporta:
    - SQLite (default local, sin infra)
    - PostgreSQL / MySQL / SQL Server vía DATABASE_URL
    """

    DEFAULT_TABLE = "predicciones_tensorflow"

    def __init__(self, database_url: Optional[str] = None):
        default_sqlite = Path(__file__).resolve().parent.parent / "data" / "powerbi" / "predicciones.db"
        default_sqlite.parent.mkdir(parents=True, exist_ok=True)

        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            f"sqlite:///{default_sqlite}",
        )
        self.engine: Engine = create_engine(self.database_url, future=True)
        self.table_name = os.getenv("POWERBI_SQL_TABLE", self.DEFAULT_TABLE)

    def append(self, df: pd.DataFrame, table_name: Optional[str] = None) -> int:
        """Inserta filas con if_exists='append'. Retorna número de filas."""
        if df.empty:
            return 0

        table = table_name or self.table_name
        # SQLite / Postgres: append histórico
        df.to_sql(
            table,
            self.engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        return len(df)

    def replace(self, df: pd.DataFrame, table_name: Optional[str] = None) -> int:
        """Reemplaza tabla completa (útil para snapshots diarios)."""
        if df.empty:
            return 0
        table = table_name or self.table_name
        df.to_sql(table, self.engine, if_exists="replace", index=False)
        return len(df)

    def upsert_by_id(self, df: pd.DataFrame, table_name: Optional[str] = None) -> int:
        """
        Upsert simple por id_registro.
        - SQLite: delete + append
        - Postgres: ON CONFLICT (si hay PK; fallback delete+append)
        """
        if df.empty:
            return 0

        table = table_name or self.table_name
        ids = df["id_registro"].astype(str).tolist()

        with self.engine.begin() as conn:
            # Crear tabla si no existe
            df.head(0).to_sql(table, conn, if_exists="append", index=False)

            if ids:
                # Borrar IDs existentes y reinsertar
                placeholders = ", ".join([f":id{i}" for i in range(len(ids))])
                params = {f"id{i}": v for i, v in enumerate(ids)}
                conn.execute(
                    text(f"DELETE FROM {table} WHERE id_registro IN ({placeholders})"),
                    params,
                )

        df.to_sql(table, self.engine, if_exists="append", index=False)
        return len(df)

    def fetch_recent(self, limit: int = 100, table_name: Optional[str] = None) -> pd.DataFrame:
        table = table_name or self.table_name
        try:
            return pd.read_sql(
                text(f"SELECT * FROM {table} ORDER BY fecha_prediccion DESC LIMIT :lim"),
                self.engine,
                params={"lim": limit},
            )
        except Exception:
            return pd.DataFrame()

    def count_rows(self, table_name: Optional[str] = None) -> int:
        table = table_name or self.table_name
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                return int(result.scalar() or 0)
        except Exception:
            return 0


# ---------------------------------------------------------------------------
# 3. Push Dataset (streaming / tiempo real)
# ---------------------------------------------------------------------------

class PowerBIPushClient:
    """
    Envía predicciones a un Push / Streaming Dataset de Power BI.

    Setup en Power BI Service:
      Área de trabajo → Nuevo → Conjunto de datos de streaming → API
      Campos sugeridos:
        - id_registro (Text)
        - categoria (Text)
        - modelo (Text)
        - probabilidad (Number)
        - confianza (Number)
        - recomendacion (Text)
        - fecha_prediccion (DateTime)
        - id_negocio (Text)
        - batch_id (Text)
    """

    def __init__(self, push_url: Optional[str] = None, api_key: Optional[str] = None):
        self.push_url = push_url or os.getenv("POWERBI_PUSH_URL", "")
        self.api_key = api_key or os.getenv("POWERBI_API_KEY", "")

    @property
    def enabled(self) -> bool:
        return bool(self.push_url)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def push_rows(self, rows: Sequence[Dict[str, Any]], timeout: int = 30) -> Dict[str, Any]:
        """POST rows al Push Dataset. Power BI espera un array JSON."""
        if not self.enabled:
            return {"status": "skipped", "reason": "POWERBI_PUSH_URL no configurada"}

        # Payload tipado para streaming datasets
        payload = []
        for row in rows:
            item = {
                "id_registro": str(row.get("id_registro", "")),
                "id_negocio": str(row.get("id_negocio", "")),
                "categoria": str(row.get("categoria", "")),
                "modelo": str(row.get("modelo", "")),
                "probabilidad": float(row["probabilidad"]) if row.get("probabilidad") is not None else 0.0,
                "confianza": float(row["confianza"]) if row.get("confianza") is not None else 0.0,
                "recomendacion": str(row.get("recomendacion", "")),
                "fecha_prediccion": self._to_iso(row.get("fecha_prediccion")),
                "batch_id": str(row.get("batch_id", "")),
            }
            payload.append(item)

        response = requests.post(
            self.push_url,
            data=json.dumps(payload),
            headers=self._headers(),
            timeout=timeout,
        )

        return {
            "status": "ok" if response.ok else "error",
            "status_code": response.status_code,
            "rows_sent": len(payload),
            "response_text": response.text[:500],
        }

    def push_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"status": "skipped", "reason": "DataFrame vacío"}
        rows = df.to_dict(orient="records")
        return self.push_rows(rows)

    @staticmethod
    def _to_iso(value: Any) -> str:
        if value is None:
            return datetime.now(timezone.utc).isoformat()
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)


# ---------------------------------------------------------------------------
# 4. Pipeline unificado
# ---------------------------------------------------------------------------

class PowerBIExportPipeline:
    """
    Orquesta: predicciones → DataFrame → SQL (+ opcional Push Dataset).

    Modes:
    - repository: solo SQL (recomendado históricos / Import / DirectQuery)
    - streaming: solo Push Dataset
    - hybrid: SQL + Push Dataset
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        push_url: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        self.db = DatabaseExporter(database_url)
        self.push = PowerBIPushClient(push_url)
        self.mode = (mode or os.getenv("POWERBI_EXPORT_MODE", "hybrid")).lower()
        self.builder = PredictionRowBuilder()

    def export_predictions(
        self,
        rows: Sequence[Dict[str, Any]],
        *,
        write_mode: str = "append",
    ) -> Dict[str, Any]:
        """
        Exporta filas ya estructuradas.

        write_mode: append | replace | upsert
        """
        df = self.builder.to_dataframe(rows)
        result: Dict[str, Any] = {
            "timestamp": PredictionRowBuilder.utc_now_iso(),
            "mode": self.mode,
            "rows": len(df),
            "database": None,
            "push": None,
        }

        if self.mode in ("repository", "hybrid", "sql"):
            if write_mode == "replace":
                n = self.db.replace(df)
            elif write_mode == "upsert":
                n = self.db.upsert_by_id(df)
            else:
                n = self.db.append(df)
            result["database"] = {
                "status": "ok",
                "rows_written": n,
                "table": self.db.table_name,
                "database_url_scheme": self.db.database_url.split("://", 1)[0],
                "total_rows": self.db.count_rows(),
            }

        if self.mode in ("streaming", "hybrid", "push"):
            result["push"] = self.push.push_dataframe(df)

        return result

    def export_from_model_output(
        self,
        *,
        category: str,
        model: str,
        prediction: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None,
        id_negocio: Optional[str] = None,
        confidence_score: Optional[float] = None,
        batch_id: Optional[str] = None,
        also_push: bool = True,
    ) -> Dict[str, Any]:
        """Atajo: una predicción de modelo → export inmediato."""
        row = self.builder.build_row(
            category=category,
            model=model,
            prediction=prediction,
            input_data=input_data,
            id_negocio=id_negocio,
            confidence_score=confidence_score,
            batch_id=batch_id,
        )

        # Temporalmente forzar push si se pide
        original_mode = self.mode
        if also_push and self.push.enabled and self.mode == "repository":
            self.mode = "hybrid"
        try:
            return self.export_predictions([row], write_mode="append")
        finally:
            self.mode = original_mode

    def export_batch_file(
        self,
        jsonl_path: Union[str, Path],
        *,
        write_mode: str = "append",
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lee predictions.jsonl del impact tracker y exporta a Power BI."""
        path = Path(jsonl_path)
        if not path.exists():
            return {"status": "error", "reason": f"Archivo no encontrado: {path}"}

        rows: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if limit is not None and i >= limit:
                    break
                record = json.loads(line)
                category = record.get("category", "unknown")
                # Mapear categorías del tracker a schemas del exporter
                category_map = {
                    "real_estate": "real_estate",
                    "social_media": "social_media",
                    "personal": "personal_tco",
                }
                mapped = category_map.get(category, category)
                rows.append(
                    self.builder.build_row(
                        category=mapped,
                        model=record.get("model", ""),
                        prediction=record.get("prediction", {}),
                        input_data=record.get("input_data", {}),
                        id_registro=record.get("id"),
                        confidence_score=record.get("confidence_score"),
                        fecha_prediccion=record.get("timestamp"),
                        batch_id=f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                    )
                )

        return self.export_predictions(rows, write_mode=write_mode)


def get_default_pipeline() -> PowerBIExportPipeline:
    return PowerBIExportPipeline()


if __name__ == "__main__":
    # Demo local
    pipeline = PowerBIExportPipeline(mode="repository")

    demo_rows = [
        PredictionRowBuilder.build_row(
            category="real_estate",
            model="real_estate_opportunity",
            prediction={
                "probabilidad_venta_12m": 0.873,
                "precio_estimado": 14200000,
                "dias_estimados": 156,
                "recomendacion": "ALTA PRIORIDAD",
            },
            input_data={"ubicacion": "Querétaro", "precio_m2": 45000, "cap_rate": 7.2},
            id_negocio="DEV-QRO-001",
            confidence_score=0.873,
            batch_id="demo_batch",
        ),
        PredictionRowBuilder.build_row(
            category="social_media",
            model="social_content_optimizer",
            prediction={
                "probabilidad_viral": 0.62,
                "engagement_score": 78.5,
                "alcance_estimado": 4200,
                "recomendacion": "PUBLICAR",
            },
            input_data={"tipo_contenido": "Reel", "tema_categoria": "Cap Rate", "hora": 9},
            id_negocio="POST-WEEK-01",
            confidence_score=0.62,
            batch_id="demo_batch",
        ),
    ]

    result = pipeline.export_predictions(demo_rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nTotal filas en DB: {pipeline.db.count_rows()}")
    print(pipeline.db.fetch_recent(5).to_string(index=False))
