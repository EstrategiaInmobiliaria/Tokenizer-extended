"""
Sabueso Digital v3 - Central de Alertas Palm Diamante
Detección → evidencia inmutable → WhatsApp → revisión humana (Jidoka) → réplica a LÆDS®

Instalación:
    pip install fastapi uvicorn requests python-multipart "pydantic>=2"

Variables de entorno obligatorias:
    WHATSAPP_TOKEN        Token permanente (System User) de Meta
    PHONE_NUMBER_ID       ID del número de WhatsApp Business
    GRAPH_API_VERSION     Versión vigente que muestra tu panel de Meta (ej. "vXX.0")
    DESTINATION_PHONES    Números destino separados por coma (tú y Diana)
    WEBHOOK_API_KEY       Secreto (24+ caracteres) que n8n envía en el header X-API-Key
    REVIEW_SECRET         Secreto (24+ caracteres) para firmar los enlaces de revisión
    REVIEW_PIN            PIN (6+ caracteres) que se pide para registrar un dictamen
    PUBLIC_BASE_URL       URL pública HTTPS de este servicio (ej. https://sabueso.palm-diamante.com)
    FALLBACK_IMAGE_URL    Imagen pública (logo) para el encabezado cuando no hay captura
                          (solo obligatoria en modo template)

Opcionales:
    WHATSAPP_MODE         "template" (producción, default) o "text" (pruebas en ventana de 24 h)
    TEMPLATE_NAME         Plantilla Utility aprobada (default "alerta_fraude_v3")
    TEMPLATE_LANG         Idioma de la plantilla (default "es_MX")
    ALLOWED_CAPTURE_HOSTS Dominios desde los que se aceptan capturas, separados por coma
    SHEET_WEBHOOK_URL     Webhook de n8n que replica eventos al Sheet Maestro LÆDS®
    SHEET_WEBHOOK_SECRET  Secreto que se envía a n8n en el header X-Sabueso-Secret
    DB_PATH               Archivo SQLite (default "sabueso_audit.db")

Ejecutar:
    python sabueso_alertas_v3.py
"""

import csv
import hashlib
import hmac
import html
import io
import json
import os
import re
import sqlite3
import sys
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import List, Literal, Optional
from urllib.parse import urlsplit, urlunsplit

import requests
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, Form, Header, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field, HttpUrl, field_validator


# ===========================================================================
# Configuración: el servicio no arranca si falta algo crítico
# ===========================================================================
def _env(nombre: str, requerido: bool = True, default: Optional[str] = None) -> str:
    valor = os.getenv(nombre, default)
    if requerido and not valor:
        sys.exit(f"❌ Falta la variable de entorno {nombre}. El servicio no puede arrancar.")
    return valor or ""


WHATSAPP_MODE = _env("WHATSAPP_MODE", requerido=False, default="template")
if WHATSAPP_MODE not in ("template", "text"):
    sys.exit("❌ WHATSAPP_MODE debe ser 'template' o 'text'.")

WHATSAPP_TOKEN = _env("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = _env("PHONE_NUMBER_ID")
GRAPH_API_VERSION = _env("GRAPH_API_VERSION")
DESTINATION_PHONES = [p.strip() for p in _env("DESTINATION_PHONES").split(",") if p.strip()]
WEBHOOK_API_KEY = _env("WEBHOOK_API_KEY")
REVIEW_SECRET = _env("REVIEW_SECRET")
REVIEW_PIN = _env("REVIEW_PIN")
PUBLIC_BASE_URL = _env("PUBLIC_BASE_URL").rstrip("/")
FALLBACK_IMAGE_URL = _env("FALLBACK_IMAGE_URL", requerido=(WHATSAPP_MODE == "template"))
TEMPLATE_NAME = _env("TEMPLATE_NAME", requerido=False, default="alerta_fraude_v3")
TEMPLATE_LANG = _env("TEMPLATE_LANG", requerido=False, default="es_MX")
ALLOWED_CAPTURE_HOSTS = {
    h.strip().lower() for h in _env("ALLOWED_CAPTURE_HOSTS", requerido=False).split(",") if h.strip()
}
SHEET_WEBHOOK_URL = _env("SHEET_WEBHOOK_URL", requerido=False)
SHEET_WEBHOOK_SECRET = _env("SHEET_WEBHOOK_SECRET", requerido=False)
DB_PATH = _env("DB_PATH", requerido=False, default="sabueso_audit.db")

for _nombre, _valor in (("WEBHOOK_API_KEY", WEBHOOK_API_KEY), ("REVIEW_SECRET", REVIEW_SECRET)):
    if len(_valor) < 24:
        sys.exit(f"❌ {_nombre} debe tener al menos 24 caracteres.")
if len(REVIEW_PIN) < 6:
    sys.exit("❌ REVIEW_PIN debe tener al menos 6 caracteres.")
if not PUBLIC_BASE_URL.startswith("https://"):
    sys.exit("❌ PUBLIC_BASE_URL debe ser HTTPS (Meta exige HTTPS en botones).")

GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}"
AUTH_META = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}


def ahora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def codigo_publico(evidencia_id: int) -> str:
    return f"PD-{evidencia_id:05d}"


# ===========================================================================
# Validación de entrada (Poka-Yoke)
# ===========================================================================
def normalizar_telefono(tel: str) -> str:
    """Convierte cualquier formato mexicano a 10 dígitos."""
    digitos = re.sub(r"\D", "", tel)
    if len(digitos) == 13 and digitos.startswith("521"):
        digitos = digitos[3:]
    elif len(digitos) == 12 and digitos.startswith("52"):
        digitos = digitos[2:]
    if len(digitos) != 10:
        raise ValueError(f"Teléfono inválido: {tel}")
    return digitos


def normalizar_url(url: str) -> str:
    """Misma página aunque cambie mayúsculas del dominio, la diagonal final o el #fragmento."""
    partes = urlsplit(url)
    ruta = partes.path.rstrip("/") or "/"
    return urlunsplit((partes.scheme.lower(), partes.netloc.lower(), ruta, partes.query, ""))


class AlertaCoyote(BaseModel):
    nivel_riesgo: Literal["BAJO", "MEDIO", "ALTO"]
    motivo: str = Field(min_length=3, max_length=300)
    url_sospechosa: HttpUrl
    telefonos_no_autorizados: List[str] = Field(min_length=1, max_length=20)
    timestamp: datetime
    screenshot_url: Optional[HttpUrl] = None
    html_sha256: Optional[str] = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")

    @field_validator("telefonos_no_autorizados")
    @classmethod
    def _normalizar(cls, v: List[str]) -> List[str]:
        return sorted({normalizar_telefono(t) for t in v})


# ===========================================================================
# Base de datos: evidencia append-only con cadena de hashes
# ===========================================================================
GENESIS = "0" * 64
CAMPOS_CADENA = (
    "huella", "nivel_riesgo", "motivo", "url", "telefonos",
    "detectado_en", "recibido_en", "captura_url", "html_sha256",
)


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaccion():
    """BEGIN IMMEDIATE bloquea escrituras concurrentes: elimina la condición de carrera."""
    conn = conectar()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


@contextmanager
def lectura():
    conn = conectar()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with lectura() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS evidencias (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                huella        TEXT UNIQUE NOT NULL,
                nivel_riesgo  TEXT NOT NULL,
                motivo        TEXT NOT NULL,
                url           TEXT NOT NULL,
                telefonos     TEXT NOT NULL,
                detectado_en  TEXT NOT NULL,
                recibido_en   TEXT NOT NULL,
                captura_url   TEXT,
                html_sha256   TEXT,
                hash_anterior TEXT NOT NULL,
                hash_registro TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS detecciones (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                evidencia_id INTEGER NOT NULL REFERENCES evidencias(id),
                detectado_en TEXT NOT NULL,
                recibido_en  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS revisiones (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                evidencia_id INTEGER UNIQUE NOT NULL REFERENCES evidencias(id),
                decision     TEXT NOT NULL CHECK (decision IN ('CONFIRMADO', 'DESCARTADO')),
                canal        TEXT,
                revisor      TEXT NOT NULL,
                notas        TEXT,
                revisado_en  TEXT NOT NULL,
                CHECK (decision = 'DESCARTADO' OR (canal IS NOT NULL AND canal <> ''))
            );

            CREATE TABLE IF NOT EXISTS envios (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                evidencia_id INTEGER NOT NULL REFERENCES evidencias(id),
                tipo         TEXT NOT NULL,
                estado       TEXT NOT NULL,
                detalle      TEXT,
                creado_en    TEXT NOT NULL
            );
            """
        )
        # Evidencia, detecciones y dictámenes no se pueden editar ni borrar
        for tabla in ("evidencias", "detecciones", "revisiones"):
            for accion in ("UPDATE", "DELETE"):
                conn.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {tabla}_no_{accion.lower()} "
                    f"BEFORE {accion} ON {tabla} "
                    f"BEGIN SELECT RAISE(ABORT, 'Registro de auditoría inmutable: {tabla}'); END;"
                )


def hash_de(datos: dict, anterior: str) -> str:
    contenido = json.dumps({k: datos[k] for k in CAMPOS_CADENA}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((anterior + contenido).encode()).hexdigest()


def calcular_huella(alerta: AlertaCoyote) -> str:
    base = normalizar_url(str(alerta.url_sospechosa)) + "|" + ",".join(alerta.telefonos_no_autorizados)
    return hashlib.sha256(base.encode()).hexdigest()


def registrar(alerta: AlertaCoyote) -> tuple[int, bool]:
    """Devuelve (evidencia_id, es_nueva). Las repeticiones solo suman una detección."""
    huella = calcular_huella(alerta)
    ahora = ahora_iso()
    detectado = alerta.timestamp.isoformat(timespec="seconds")

    with transaccion() as conn:
        existente = conn.execute("SELECT id FROM evidencias WHERE huella = ?", (huella,)).fetchone()
        if existente:
            conn.execute(
                "INSERT INTO detecciones (evidencia_id, detectado_en, recibido_en) VALUES (?, ?, ?)",
                (existente["id"], detectado, ahora),
            )
            return existente["id"], False

        ultimo = conn.execute("SELECT hash_registro FROM evidencias ORDER BY id DESC LIMIT 1").fetchone()
        anterior = ultimo["hash_registro"] if ultimo else GENESIS

        datos = {
            "huella": huella,
            "nivel_riesgo": alerta.nivel_riesgo,
            "motivo": alerta.motivo,
            "url": str(alerta.url_sospechosa),
            "telefonos": ",".join(alerta.telefonos_no_autorizados),
            "detectado_en": detectado,
            "recibido_en": ahora,
            "captura_url": str(alerta.screenshot_url) if alerta.screenshot_url else None,
            "html_sha256": alerta.html_sha256.lower() if alerta.html_sha256 else None,
        }
        datos["hash_anterior"] = anterior
        datos["hash_registro"] = hash_de(datos, anterior)

        columnas = ", ".join(datos.keys())
        marcas = ", ".join("?" for _ in datos)
        cur = conn.execute(f"INSERT INTO evidencias ({columnas}) VALUES ({marcas})", tuple(datos.values()))
        conn.execute(
            "INSERT INTO detecciones (evidencia_id, detectado_en, recibido_en) VALUES (?, ?, ?)",
            (cur.lastrowid, detectado, ahora),
        )
        return cur.lastrowid, True


CONSULTA_EVIDENCIAS = """
    SELECT e.*,
           COUNT(d.id)                    AS veces_detectada,
           MAX(d.recibido_en)             AS ultima_deteccion,
           COALESCE(r.decision, 'PENDIENTE') AS estado,
           r.canal, r.revisor, r.notas, r.revisado_en
    FROM evidencias e
    LEFT JOIN detecciones d ON d.evidencia_id = e.id
    LEFT JOIN revisiones r  ON r.evidencia_id = e.id
    {where}
    GROUP BY e.id
    ORDER BY e.id
"""


def obtener_evidencia(evidencia_id: int) -> Optional[dict]:
    with lectura() as conn:
        fila = conn.execute(CONSULTA_EVIDENCIAS.format(where="WHERE e.id = ?"), (evidencia_id,)).fetchone()
    return dict(fila) if fila else None


def listar_canales() -> List[str]:
    with lectura() as conn:
        filas = conn.execute(
            "SELECT DISTINCT canal FROM revisiones WHERE canal IS NOT NULL ORDER BY canal"
        ).fetchall()
    return [f["canal"] for f in filas]


def registrar_envio(evidencia_id: int, tipo: str, estado: str, detalle: str) -> None:
    with transaccion() as conn:
        conn.execute(
            "INSERT INTO envios (evidencia_id, tipo, estado, detalle, creado_en) VALUES (?, ?, ?, ?, ?)",
            (evidencia_id, tipo, estado, detalle[:2000], ahora_iso()),
        )


# ===========================================================================
# Enlaces de revisión firmados (el botón de WhatsApp no puede mandar headers)
# ===========================================================================
def token_revision(evidencia_id: int) -> str:
    firma = hmac.new(REVIEW_SECRET.encode(), f"revision:{evidencia_id}".encode(), hashlib.sha256)
    return firma.hexdigest()[:32]


def clave_revision(evidencia_id: int) -> str:
    return f"{evidencia_id}-{token_revision(evidencia_id)}"


def resolver_clave(clave: str) -> int:
    m = re.fullmatch(r"(\d+)-([a-f0-9]{32})", clave)
    if not m or not hmac.compare_digest(m.group(2), token_revision(int(m.group(1)))):
        raise HTTPException(status_code=404, detail="No encontrado")
    return int(m.group(1))


# ===========================================================================
# WhatsApp (Meta Cloud API)
# ===========================================================================
MAX_IMAGEN = 5 * 1024 * 1024  # límite de Meta para imágenes


def host_permitido(url: Optional[str]) -> bool:
    if not url:
        return False
    partes = urlsplit(url)
    return partes.scheme == "https" and (partes.hostname or "").lower() in ALLOWED_CAPTURE_HOSTS


def subir_captura(captura_url: Optional[str]) -> Optional[str]:
    """Descarga la captura (solo de dominios permitidos), valida que sea imagen real y la sube a Meta."""
    if not captura_url:
        return None
    if not host_permitido(captura_url):
        log(f"⚠️ Captura ignorada, dominio no permitido: {captura_url}")
        return None

    try:
        with requests.get(captura_url, timeout=15, stream=True, allow_redirects=False) as r:
            r.raise_for_status()
            contenido = b""
            for bloque in r.iter_content(64 * 1024):
                contenido += bloque
                if len(contenido) > MAX_IMAGEN:
                    log("⚠️ Captura mayor a 5 MB, se usará la imagen de respaldo.")
                    return None
    except requests.RequestException as e:
        log(f"⚠️ No se pudo descargar la captura: {type(e).__name__}: {e}")
        return None

    # El tipo se decide por el contenido real, no por lo que diga el servidor
    if contenido.startswith(b"\xff\xd8\xff"):
        tipo, ext = "image/jpeg", "jpg"
    elif contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        tipo, ext = "image/png", "png"
    else:
        log("⚠️ La captura no es JPEG ni PNG válido.")
        return None

    try:
        up = requests.post(
            f"{GRAPH_BASE}/media",
            headers=AUTH_META,
            files={"file": (f"evidencia.{ext}", contenido, tipo)},
            data={"messaging_product": "whatsapp", "type": tipo},
            timeout=20,
        )
    except requests.RequestException as e:
        log(f"⚠️ Error de red subiendo captura a Meta: {e}")
        return None

    if not up.ok:
        log(f"⚠️ Meta rechazó la captura: HTTP {up.status_code} {up.text[:300]}")
        return None
    return up.json().get("id")


def construir_payload(destino: str, ev: dict, media_id: Optional[str]) -> dict:
    codigo = codigo_publico(ev["id"])
    telefonos = ev["telefonos"].replace(",", ", ")
    hora = datetime.fromisoformat(ev["detectado_en"]).strftime("%d/%m/%Y %H:%M")
    clave = clave_revision(ev["id"])

    if WHATSAPP_MODE == "text":
        cuerpo = (
            f"🚨 *ALERTA {ev['nivel_riesgo']} - PALM DIAMANTE* 🚨\n\n"
            f"ID evidencia: {codigo}\n"
            f"Teléfonos detectados: {telefonos}\n"
            f"Hora: {hora}\n\n"
            f"Revisar: {PUBLIC_BASE_URL}/revisar/{clave}"
        )
        return {
            "messaging_product": "whatsapp",
            "to": destino,
            "type": "text",
            "text": {"body": cuerpo, "preview_url": False},
        }

    # El encabezado IMAGE es obligatorio si la plantilla lo tiene: siempre hay respaldo
    imagen = {"id": media_id} if media_id else {"link": FALLBACK_IMAGE_URL}
    return {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {"code": TEMPLATE_LANG},
            "components": [
                {"type": "header", "parameters": [{"type": "image", "image": imagen}]},
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": ev["nivel_riesgo"]},   # {{1}}
                        {"type": "text", "text": codigo},               # {{2}}
                        {"type": "text", "text": telefonos[:100]},      # {{3}}
                        {"type": "text", "text": hora},                 # {{4}}
                    ],
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [{"type": "text", "text": clave}],
                },
            ],
        },
    }


def enviar_whatsapp(evidencia_id: int) -> None:
    ev = obtener_evidencia(evidencia_id)
    if not ev:
        return

    media_id = subir_captura(ev["captura_url"]) if WHATSAPP_MODE == "template" else None
    headers = {**AUTH_META, "Content-Type": "application/json"}
    resultados = []

    for destino in DESTINATION_PHONES:
        try:
            r = requests.post(
                f"{GRAPH_BASE}/messages",
                headers=headers,
                json=construir_payload(destino, ev, media_id),
                timeout=10,
            )
            resultados.append(f"{destino}: ok" if r.ok else f"{destino}: HTTP {r.status_code} {r.text[:300]}")
        except requests.RequestException as e:
            resultados.append(f"{destino}: {type(e).__name__}: {e}")

    estado = "enviado" if all(x.endswith(": ok") for x in resultados) else "error"
    detalle = " | ".join(resultados)
    registrar_envio(evidencia_id, "whatsapp", estado, detalle)
    log(f"{'✅' if estado == 'enviado' else '❌'} {codigo_publico(evidencia_id)} WhatsApp: {detalle}")


# ===========================================================================
# Réplica al Sheet Maestro LÆDS® (vía n8n). La penalización solo viaja confirmada.
# ===========================================================================
def sincronizar_sheet(evento: str, evidencia_id: int) -> None:
    if not SHEET_WEBHOOK_URL:
        return
    ev = obtener_evidencia(evidencia_id)
    if not ev:
        return

    codigo = codigo_publico(evidencia_id)
    payload = {
        "id_evento": f"{codigo}-{evento}",  # n8n debe ignorar id_evento repetidos
        "evento": evento,
        "codigo": codigo,
        "nivel_riesgo": ev["nivel_riesgo"],
        "motivo": ev["motivo"],
        "url": ev["url"],
        "telefonos": ev["telefonos"],
        "detectado_en": ev["detectado_en"],
        "veces_detectada": ev["veces_detectada"],
        "estado": ev["estado"],
        "canal": ev["canal"],
        "revisor": ev["revisor"],
        "revisado_en": ev["revisado_en"],
        "aplicar_penalizacion": ev["estado"] == "CONFIRMADO",
    }
    headers = {"X-Sabueso-Secret": SHEET_WEBHOOK_SECRET} if SHEET_WEBHOOK_SECRET else {}

    try:
        r = requests.post(SHEET_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        estado = "enviado" if r.ok else "error"
        detalle = f"HTTP {r.status_code} {r.text[:300]}"
    except requests.RequestException as e:
        estado, detalle = "error", f"{type(e).__name__}: {e}"

    registrar_envio(evidencia_id, f"sheet:{evento}", estado, detalle)
    log(f"{'✅' if estado == 'enviado' else '❌'} {codigo} Sheet ({evento}): {detalle}")


# ===========================================================================
# Página de revisión (Jidoka: la consecuencia requiere firma humana)
# ===========================================================================
_fallos_pin: dict[int, list[float]] = {}


def pin_bloqueado(evidencia_id: int) -> bool:
    ahora = time.time()
    recientes = [t for t in _fallos_pin.get(evidencia_id, []) if ahora - t < 900]
    _fallos_pin[evidencia_id] = recientes
    return len(recientes) >= 5


ESTILOS = """
:root { --fondo:#f6f5f2; --tarjeta:#fff; --texto:#1c1c1c; --suave:#6b6b6b; --borde:#e2e0da;
        --rojo:#b3261e; --verde:#1e6b3a; --acento:#8a6d1f; }
@media (prefers-color-scheme: dark) {
  :root { --fondo:#141414; --tarjeta:#1f1f1f; --texto:#eee; --suave:#a0a0a0; --borde:#333;
          --rojo:#ff8a80; --verde:#81c995; --acento:#e0c16a; } }
* { box-sizing:border-box; }
body { margin:0; padding:16px; background:var(--fondo); color:var(--texto);
       font:16px/1.5 -apple-system, system-ui, "Segoe UI", Roboto, sans-serif; }
main { max-width:640px; margin:0 auto; }
h1 { font-size:1.3rem; margin:0 0 4px; } h2 { font-size:1.05rem; margin:0 0 12px; }
.card { background:var(--tarjeta); border:1px solid var(--borde); border-radius:12px; padding:16px; margin:12px 0; }
.nota { color:var(--suave); font-size:.9rem; }
.badge { display:inline-block; padding:2px 10px; border-radius:99px; font-size:.85rem; font-weight:600;
         border:1px solid currentColor; color:var(--acento); }
.badge.CONFIRMADO { color:var(--rojo); } .badge.DESCARTADO { color:var(--verde); }
dl { display:grid; grid-template-columns:max-content 1fr; gap:6px 12px; margin:0; }
dt { color:var(--suave); } dd { margin:0; overflow-wrap:anywhere; }
code { overflow-wrap:anywhere; }
img { max-width:100%; border-radius:8px; border:1px solid var(--borde); }
label { display:block; margin:12px 0 4px; font-weight:600; }
.opciones label { font-weight:400; margin:6px 0; }
input[type=text], input[type=password], textarea { width:100%; padding:10px; font:inherit; color:inherit;
       background:var(--fondo); border:1px solid var(--borde); border-radius:8px; }
button { margin-top:16px; width:100%; padding:12px; font:inherit; font-weight:600; border:0;
         border-radius:8px; background:var(--texto); color:var(--fondo); cursor:pointer; }
.aviso { padding:12px; border-radius:8px; margin:12px 0; border:1px solid currentColor; }
.aviso.ok { color:var(--verde); } .aviso.error { color:var(--rojo); }
"""


def pagina_revision(ev: dict, clave: str, aviso: str = "", es_error: bool = False) -> str:
    e = html.escape
    codigo = codigo_publico(ev["id"])

    if ev["captura_url"] and host_permitido(ev["captura_url"]):
        captura = f'<img src="{e(ev["captura_url"])}" alt="Captura de la página sospechosa">'
    elif ev["captura_url"]:
        captura = f'<p class="nota">Captura en dominio no permitido: <code>{e(ev["captura_url"])}</code></p>'
    else:
        captura = '<p class="nota">Sin captura adjunta.</p>'

    clase_aviso = "error" if es_error else "ok"
    bloque_aviso = f'<div class="aviso {clase_aviso}">{e(aviso)}</div>' if aviso else ""

    if ev["estado"] != "PENDIENTE":
        canal = f" · Canal: {e(ev['canal'])}" if ev["canal"] else ""
        notas = f"<p>{e(ev['notas'])}</p>" if ev["notas"] else ""
        dictamen = (
            '<div class="card"><h2>Dictamen registrado</h2>'
            f'<p><span class="badge {e(ev["estado"])}">{e(ev["estado"])}</span>{canal}</p>'
            f'<p class="nota">Por {e(ev["revisor"])} el {e(ev["revisado_en"])}</p>{notas}</div>'
        )
    else:
        opciones_canal = "".join(f'<option value="{e(c)}">' for c in listar_canales())
        dictamen = f"""
        <form method="post" class="card">
          <h2>Dictamen</h2>
          <div class="opciones">
            <label><input type="radio" name="decision" value="CONFIRMADO" required> Confirmar fraude</label>
            <label><input type="radio" name="decision" value="DESCARTADO"> Descartar (falso positivo)</label>
          </div>
          <label for="canal">Canal responsable (obligatorio si confirmas)</label>
          <input type="text" id="canal" name="canal" list="canales" maxlength="100" placeholder="Ej. PixelSiete">
          <datalist id="canales">{opciones_canal}</datalist>
          <label for="revisor">Tu nombre</label>
          <input type="text" id="revisor" name="revisor" required maxlength="80">
          <label for="notas">Notas</label>
          <textarea id="notas" name="notas" maxlength="1000" rows="3"></textarea>
          <label for="pin">PIN de revisión</label>
          <input type="password" id="pin" name="pin" required autocomplete="off">
          <button type="submit">Registrar dictamen</button>
          <p class="nota">El dictamen es definitivo y queda en el registro de auditoría.
          Solo un dictamen CONFIRMADO envía la penalización a LÆDS®.</p>
        </form>"""

    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<title>{codigo} · Revisión de evidencia</title>
<style>{ESTILOS}</style>
</head><body><main>
  <h1>{codigo}</h1>
  <span class="badge {e(ev["estado"])}">{e(ev["estado"])}</span>
  {bloque_aviso}
  <div class="card">
    <h2>Evidencia</h2>
    <dl>
      <dt>Riesgo</dt><dd>{e(ev["nivel_riesgo"])}</dd>
      <dt>Motivo</dt><dd>{e(ev["motivo"])}</dd>
      <dt>URL</dt><dd><code>{e(ev["url"])}</code></dd>
      <dt>Teléfonos</dt><dd>{e(ev["telefonos"].replace(",", ", "))}</dd>
      <dt>Detectado</dt><dd>{e(ev["detectado_en"])}</dd>
      <dt>Veces visto</dt><dd>{ev["veces_detectada"]} (última: {e(ev["ultima_deteccion"] or "")})</dd>
      <dt>Hash HTML</dt><dd><code>{e(ev["html_sha256"] or "—")}</code></dd>
      <dt>Hash registro</dt><dd><code>{e(ev["hash_registro"])}</code></dd>
    </dl>
  </div>
  <div class="card"><h2>Captura</h2>{captura}</div>
  {dictamen}
</main></body></html>"""


# ===========================================================================
# API
# ===========================================================================
def verificar_api_key(x_api_key: str = Header(default="")) -> None:
    if not hmac.compare_digest(x_api_key.encode(), WEBHOOK_API_KEY.encode()):
        raise HTTPException(status_code=401, detail="API key inválida")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    log(f"Sabueso v3 iniciado. Modo: {WHATSAPP_MODE}. Destinos: {len(DESTINATION_PHONES)}. "
        f"Réplica Sheet: {'sí' if SHEET_WEBHOOK_URL else 'no'}")
    yield


app = FastAPI(title="Sabueso Digital v3 - Palm Diamante", lifespan=lifespan, docs_url=None, redoc_url=None)


@app.get("/salud")
def salud():
    return {"status": "ok"}


@app.post("/webhook/alertas-fraude", dependencies=[Depends(verificar_api_key)])
def recibir_alerta(alerta: AlertaCoyote, background_tasks: BackgroundTasks):
    evidencia_id, es_nueva = registrar(alerta)
    codigo = codigo_publico(evidencia_id)

    if es_nueva:
        log(f"🆕 {codigo}: {alerta.url_sospechosa}")
        background_tasks.add_task(enviar_whatsapp, evidencia_id)
        background_tasks.add_task(sincronizar_sheet, "nueva_alerta", evidencia_id)
    else:
        log(f"🔁 {codigo} detectada otra vez; se sumó la detección sin notificar.")

    return {"status": "success", "codigo": codigo, "nueva": es_nueva}


@app.get("/revisar/{clave}", response_class=HTMLResponse)
def ver_revision(clave: str):
    evidencia_id = resolver_clave(clave)
    ev = obtener_evidencia(evidencia_id)
    if not ev:
        raise HTTPException(status_code=404, detail="No encontrado")
    return HTMLResponse(pagina_revision(ev, clave))


@app.post("/revisar/{clave}", response_class=HTMLResponse)
def registrar_dictamen(
    clave: str,
    background_tasks: BackgroundTasks,
    decision: str = Form(...),
    revisor: str = Form(...),
    pin: str = Form(...),
    canal: str = Form(""),
    notas: str = Form(""),
):
    evidencia_id = resolver_clave(clave)
    ev = obtener_evidencia(evidencia_id)
    if not ev:
        raise HTTPException(status_code=404, detail="No encontrado")

    def rechazar(mensaje: str, status: int = 400) -> HTMLResponse:
        return HTMLResponse(pagina_revision(ev, clave, mensaje, es_error=True), status_code=status)

    if pin_bloqueado(evidencia_id):
        return rechazar("Demasiados intentos con PIN incorrecto. Espera 15 minutos.", 429)
    if not hmac.compare_digest(pin.encode(), REVIEW_PIN.encode()):
        _fallos_pin.setdefault(evidencia_id, []).append(time.time())
        return rechazar("PIN incorrecto.", 403)

    decision = decision.strip().upper()
    canal = canal.strip()[:100]
    revisor = revisor.strip()[:80]
    notas = notas.strip()[:1000]

    if decision not in ("CONFIRMADO", "DESCARTADO"):
        return rechazar("Decisión inválida.")
    if not revisor:
        return rechazar("Escribe tu nombre.")
    if decision == "CONFIRMADO" and not canal:
        return rechazar("Para confirmar, indica el canal responsable.")

    try:
        with transaccion() as conn:
            conn.execute(
                "INSERT INTO revisiones (evidencia_id, decision, canal, revisor, notas, revisado_en) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (evidencia_id, decision, canal or None, revisor, notas or None, ahora_iso()),
            )
    except sqlite3.IntegrityError:
        ev = obtener_evidencia(evidencia_id)
        return rechazar("Esta alerta ya tiene un dictamen registrado.", 409)

    _fallos_pin.pop(evidencia_id, None)
    log(f"🧾 {codigo_publico(evidencia_id)} {decision} por {revisor}" + (f" · canal {canal}" if canal else ""))
    background_tasks.add_task(sincronizar_sheet, "revision", evidencia_id)

    ev = obtener_evidencia(evidencia_id)
    return HTMLResponse(pagina_revision(ev, clave, "Dictamen registrado."))


@app.post("/alertas/{evidencia_id}/reenviar", dependencies=[Depends(verificar_api_key)])
def reenviar(evidencia_id: int, background_tasks: BackgroundTasks, tipo: Literal["whatsapp", "sheet"] = "whatsapp"):
    ev = obtener_evidencia(evidencia_id)
    if not ev:
        raise HTTPException(status_code=404, detail="No encontrado")
    if tipo == "whatsapp":
        background_tasks.add_task(enviar_whatsapp, evidencia_id)
    else:
        evento = "revision" if ev["estado"] != "PENDIENTE" else "nueva_alerta"
        background_tasks.add_task(sincronizar_sheet, evento, evidencia_id)
    return {"status": "success", "codigo": codigo_publico(evidencia_id), "reintento": tipo}


def _celda_segura(valor) -> str:
    """Evita inyección de fórmulas al abrir el CSV en Excel o Sheets."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@", "\t", "\r") else texto


@app.get("/alertas/export.csv", dependencies=[Depends(verificar_api_key)])
def exportar_csv():
    with lectura() as conn:
        filas = conn.execute(CONSULTA_EVIDENCIAS.format(where="")).fetchall()

    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.writer(buffer)
    columnas = [
        "codigo", "estado", "canal", "nivel_riesgo", "motivo", "url", "telefonos",
        "detectado_en", "veces_detectada", "ultima_deteccion", "revisor", "revisado_en",
        "notas", "captura_url", "html_sha256", "hash_registro",
    ]
    writer.writerow(columnas)
    for f in filas:
        d = dict(f)
        d["codigo"] = codigo_publico(d["id"])
        writer.writerow([_celda_segura(d.get(c)) for c in columnas])

    nombre = f"sabueso_palm_diamante_{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@app.get("/alertas/verificar-cadena", dependencies=[Depends(verificar_api_key)])
def verificar_cadena():
    """Recalcula la cadena de hashes. Guarda 'ultimo_hash' fuera del servidor para compararlo después."""
    with lectura() as conn:
        filas = conn.execute("SELECT * FROM evidencias ORDER BY id").fetchall()

    anterior = GENESIS
    for f in filas:
        d = dict(f)
        if d["hash_anterior"] != anterior or hash_de(d, anterior) != d["hash_registro"]:
            return {"integra": False, "falla_en": codigo_publico(d["id"])}
        anterior = d["hash_registro"]

    return {"integra": True, "registros": len(filas), "ultimo_hash": anterior}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
