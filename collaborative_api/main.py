import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import errors as genai_errors
from pydantic import BaseModel, Field

# Carga GEMINI_API_KEY y ANTHROPIC_API_KEY desde .env (si existe)
load_dotenv()

# claude-3-5-sonnet-20241022 fue retirado el 28-oct-2025; Anthropic recomienda
# claude-sonnet-4-6 como reemplazo. Ambos modelos se pueden sobrescribir por env.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "2048"))

app = FastAPI(
    title="Gemini & Claude Collaborative API",
    description=(
        "API que coordina las fortalezas analíticas de Gemini con las "
        "capacidades de generación y código de Claude."
    ),
    version="1.0",
)

# Clientes asíncronos para no bloquear el event loop de FastAPI.
gemini_client = genai.Client()
claude_client = anthropic.AsyncAnthropic()


class CollaborationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Requerimiento del usuario")


class CollaborationResponse(BaseModel):
    status: str
    step_1_gemini_analysis: str
    step_2_claude_execution: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "gemini_model": GEMINI_MODEL, "claude_model": CLAUDE_MODEL}


@app.post("/api/collaborate", response_model=CollaborationResponse)
async def collaborate(request: CollaborationRequest) -> CollaborationResponse:
    # PASO 1: Gemini analiza el requerimiento y produce un plan estructurado
    try:
        gemini_response = await gemini_client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=(
                "Actúa como analista y arquitecto. Analiza el siguiente requerimiento "
                "y genera un plan estructurado, pasos lógicos o especificaciones "
                f"claras:\n\n{request.prompt}"
            ),
        )
    except genai_errors.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Error de Gemini: {exc.message}") from exc

    gemini_plan = gemini_response.text
    if not gemini_plan:
        raise HTTPException(status_code=502, detail="Gemini no devolvió contenido de texto.")

    # PASO 2: Claude ejecuta la solución final a partir del plan de Gemini.
    # Se incluye también el requerimiento original para que Claude no pierda contexto.
    try:
        claude_message = await claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Basándote estrictamente en el siguiente plan analítico "
                        "proporcionado por Gemini, desarrolla la solución final "
                        "completa, limpia y optimizada.\n\n"
                        f"REQUERIMIENTO ORIGINAL:\n{request.prompt}\n\n"
                        f"PLAN DE GEMINI:\n{gemini_plan}"
                    ),
                }
            ],
        )
    except anthropic.APIStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Error de Claude: {exc.message}") from exc
    except anthropic.APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="No se pudo conectar con Claude.") from exc

    claude_output = "".join(
        block.text for block in claude_message.content if block.type == "text"
    )
    if not claude_output:
        raise HTTPException(status_code=502, detail="Claude no devolvió contenido de texto.")

    return CollaborationResponse(
        status="success",
        step_1_gemini_analysis=gemini_plan,
        step_2_claude_execution=claude_output,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
