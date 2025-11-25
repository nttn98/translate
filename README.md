# Vietnamese to English Translator

Flask web application for translating Vietnamese to English with voice input and text-to-speech using **Groq API** (super fast!).

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

4. Configure API key in `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get your free Groq API key at: https://console.groq.com/keys

5. Run:

```bash
python app.py
```

6. Open browser: `http://localhost:5000`

## ✨ Features

- ✅ Auto-translate after typing
- ✅ Voice input (Vietnamese)
- ✅ Text-to-speech (English)
- ✅ Adjustable speech speed (0.5x - 2x)
- ✅ Auto-speak mode
- ✅ Continuous mode
- ✅ **SUPER FAST** translation with Groq (280-560 tokens/sec)

## 🤖 Recommended Models

### **llama-3.3-70b-versatile** (Default - Best quality)

- Speed: 280 tokens/sec
- Price: $0.59/1M input, $0.79/1M output
- Best for accurate translations

### **llama-3.1-8b-instant** (Fastest)

- Speed: 560 tokens/sec (FASTEST!)
- Price: $0.05/1M input, $0.08/1M output
- Best for quick translations

### **qwen/qwen3-32b** (Good for Vietnamese)

- Speed: 400 tokens/sec
- Price: $0.29/1M input, $0.59/1M output
- Qwen models are optimized for Asian languages

To change model, edit `GROQ_MODEL` in `.env` file.

## 🛠️ Tech Stack

- **Backend:** Flask 3.0
- **API:** Groq (OpenAI-compatible)
- **Frontend:** Vanilla JavaScript
- **Speech:** Web Speech API
