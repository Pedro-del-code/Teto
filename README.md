# ★ Teto — Assistente Virtual Vocaloid

> Assistente de voz com avatar animado da Teto Kasane, voz neural com efeito vocaloid e IA via Groq.

---

## 🎵 Voz

| Camada | Tecnologia | Efeito |
|--------|-----------|--------|
| TTS Neural | Edge TTS `pt-BR-FranciscaNeural` | Voz jovem feminina |
| Pitch shift | pydub (+3 semitons) | Efeito vocaloid sintético |
| Velocidade | +10% | Mais animada |
| Tom | +5Hz | Levemente mais aguda |

Tudo **gratuito** — Edge TTS usa servidores da Microsoft sem API key.

---

## 🗂️ Estrutura do projeto

```
teto-assistente/
├── main.py                      ← Código principal
├── requirements.txt             ← Dependências Python
├── .env.example                 ← Modelo da chave de API
├── .gitignore
├── README.md
└── assets/
    ├── avatar/                  ← PNGs com fundo transparente (512×512)
    │   ├── boca_fechada.png     ← Silêncio / repouso
    │   ├── boca_meio.png        ← Fala suave
    │   ├── boca_aberta.png      ← Fala intensa
    │   ├── oculos.png           ← Pensando / processando
    │   └── braco_cruzado.png    ← Erro / não entendeu
    └── avatar_original/         ← JPGs originais (referência)
```

---

## ⚙️ Instalação

### 1. Requisitos do sistema

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3-pip python3-tk portaudio19-dev ffmpeg espeak -y
```

**macOS:**
```bash
brew install portaudio ffmpeg
```

**Windows:**
- Baixe o **ffmpeg**: https://ffmpeg.org/download.html → adicione ao PATH
- **PyAudio** no Windows:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```

---

### 2. Ambiente virtual

```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

---

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 4. Configurar a chave Groq

```bash
cp .env.example .env
```

Edite o `.env` e coloque sua chave gratuita de https://console.groq.com:

```
GROQ_API_KEY=gsk_SuaChaveAqui
```

---

### 5. Executar

```bash
python main.py
```

Clique em **▶ Iniciar** e fale com a Teto!

---

## 📱 Interface (Mobile-First)

A janela tem proporção de celular (**390×780 px**) para rodar bem em:
- Desktop/notebook com janela no canto
- Tablets com Python instalado
- Terminais com display (Raspberry Pi + touchscreen)

---

## 🔄 Fluxo completo

```
🎤 Microfone
    ↓
SpeechRecognition + Google STT (pt-BR, gratuito)
    ↓
Texto transcrito
    ↓
Groq API — llama-3.3-70b-versatile
    ↓
Resposta da Teto
    ↓
Edge TTS (pt-BR-FranciscaNeural) → MP3
    ↓
pydub pitch shift (+3 semitons → efeito vocaloid)
    ↓
🔊 Áudio + 🎭 Avatar animado
```

---

## 🎛️ Personalização (`main.py`)

| Constante | Padrão | O que muda |
|-----------|--------|-----------|
| `VOZ_EDGE` | `pt-BR-FranciscaNeural` | Voz do Edge TTS |
| `VOZ_VELOCIDADE` | `+10%` | Velocidade da fala |
| `VOZ_PITCH` | `+5Hz` | Tom da voz |
| `PITCH_SEMITONS` | `3` | Intensidade do efeito vocaloid |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modelo de IA |
| `SYSTEM_PROMPT` | *(personalidade da Teto)* | Comportamento da IA |

**Outras vozes Edge TTS disponíveis:**
```bash
edge-tts --list-voices | grep pt-BR
```

---

## ❓ Solução de problemas

| Problema | Solução |
|----------|---------|
| `GROQ_API_KEY não encontrada` | Renomeie `.env.example` para `.env` e cole a chave |
| `PyAudio` não instala | Use `pipwin install pyaudio` (Windows) ou `apt install portaudio19-dev` (Linux) |
| Sem som na resposta | Verifique se ffmpeg está instalado: `ffmpeg -version` |
| Avatar não aparece | Confirme que `assets/avatar/*.png` existe |
| Microfone não detectado | Verifique permissões de microfone no sistema operacional |

---

## 📄 Licença

MIT — uso livre para fins pessoais e educacionais.

---

*Teto Kasane é uma vocaloid/UTAU de uso livre. Este projeto não é afiliado oficialmente.*
