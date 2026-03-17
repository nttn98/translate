# My Translator (Flask Edition)

Realtime Vietnamese to English translator with speech input and pluggable TTS providers, inspired by the project style of phuc-nt/my-translator.

## Setup

1. Create virtual environment:

```bash
python -m venv venv
```

2. Activate virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your own Groq key in `.env`:

```
GROQ_API_KEY=your_own_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get your free Groq API key at: https://console.groq.com/keys

5. Run:

```bash
python app.py
```

6. Open browser: `http://localhost:5000`

## Features

- Realtime translate while typing (chunk based for low latency)
- Vietnamese microphone input (Web Speech API)
- English narration with 2 providers:
  - Web Speech (browser/local)
  - Edge TTS (server-side neural voice)
- Adjustable speech speed (0.5x - 2x)
- Auto-speak mode
- Continuous mode
- Tabbed settings UI

## Optional: Edge TTS setup

Edge TTS is included in requirements. If you only want browser TTS, keep using provider "Web Speech" in app settings.

## Recommended Groq models

### **llama-3.3-70b-versatile** (Default - Best quality)

- Speed: 280 tokens/sec
- Price: $0.59/1M input, $0.79/1M output
- Best for accurate translations

### **llama-3.1-8b-instant** (Fastest)

- Speed: 560 tokens/sec (FASTEST!)
- Price: $0.05/1M input, $0.08/1M output
- Best for quick translations

To change model, edit `GROQ_MODEL` in `.env` file.

## Tech Stack

- **Backend:** Flask 3.0
- **API:** Groq (OpenAI-compatible)
- **Frontend:** Vanilla JavaScript + tabbed settings UI
- **Speech:** Web Speech API + Edge TTS
