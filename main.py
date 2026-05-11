"""
╔══════════════════════════════════════════════════════════════╗
║  TETO — Backend FastAPI                                      ║
║  Recebe texto → consulta Groq → devolve resposta + áudio     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import tempfile
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import edge_tts
from groq import Groq
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY não encontrada nas variáveis de ambiente")

GROQ_MODEL     = "llama-3.3-70b-versatile"
VOZ_EDGE       = "pt-BR-FranciscaNeural"
VOZ_VELOCIDADE = "+10%"
VOZ_PITCH      = "+5Hz"

SYSTEM_PROMPT = """Você é a Teto Kasane, uma vocaloid animada, enérgica e um pouco dramática.
Fale em português do Brasil com entusiasmo. Seja divertida, prestativa e breve —
máximo 2 frases por resposta, a menos que peçam mais detalhes."""

# ─────────────────────────────────────────────
# INICIALIZAÇÃO
# ─────────────────────────────────────────────
groq_client = Groq(api_key=GROQ_API_KEY)

# Histórico por sessão simples (memória em RAM)
# Para múltiplos usuários simultâneos, use Redis ou banco de dados
historicos: dict[str, list] = {}

# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = FastAPI(title="Teto Assistente Virtual")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos (avatares)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


# ─────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────
class MensagemRequest(BaseModel):
    texto: str
    session_id: str = "default"


class MensagemResponse(BaseModel):
    resposta: str
    audio_url: str


# ─────────────────────────────────────────────
# ROTAS
# ─────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve o frontend principal."""
    return FileResponse("index.html")


@app.post("/chat", response_model=MensagemResponse)
async def chat(req: MensagemRequest):
    """
    Recebe texto do usuário → consulta Groq → gera áudio Edge TTS
    → retorna resposta em texto + URL do áudio.
    """
    # ── Recupera ou cria histórico da sessão ──
    if req.session_id not in historicos:
        historicos[req.session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    hist = historicos[req.session_id]
    hist.append({"role": "user", "content": req.texto})

    # Limita janela de contexto
    if len(hist) > 21:
        hist[1:] = hist[-20:]

    # ── Consulta Groq ──
    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=hist,
            temperature=0.85,
            max_tokens=256,
        )
        resposta = resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro Groq: {e}")

    hist.append({"role": "assistant", "content": resposta})

    # ── Gera áudio com Edge TTS ──
    try:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False, dir="static_audio", prefix="teto_"
        )
        tmp.close()
        tts = edge_tts.Communicate(
            resposta,
            voice=VOZ_EDGE,
            rate=VOZ_VELOCIDADE,
            pitch=VOZ_PITCH,
        )
        await tts.save(tmp.name)
        audio_url = f"/audio/{os.path.basename(tmp.name)}"
    except Exception as e:
        # Se TTS falhar, retorna só o texto sem áudio
        print(f"[TTS ERRO] {e}")
        audio_url = ""

    return MensagemResponse(resposta=resposta, audio_url=audio_url)


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve o arquivo de áudio gerado."""
    path = os.path.join("static_audio", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    return FileResponse(path, media_type="audio/mpeg")


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Limpa o histórico de uma sessão."""
    if session_id in historicos:
        del historicos[session_id]
    return {"ok": True}


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    os.makedirs("static_audio", exist_ok=True)
