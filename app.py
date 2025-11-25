# app.py
import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# Groq translation config (your existing)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

# Optional OpenAI (Whisper) key for server-side STT
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Upload folder for audio fallback
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not configured on server'}), 500

        payload = {
            'model': GROQ_MODEL,
            'messages': [
                {'role': 'system', 'content': 'You are a professional Vietnamese to English translator. Translate the text accurately and naturally. Only provide the translation, no explanations.'},
                {'role': 'user', 'content': text}
            ],
            'temperature': 0.3,
            'max_tokens': 1000
        }
        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}'
            },
            json=payload,
            timeout=30
        )
        if resp.status_code != 200:
            try:
                detail = resp.json()
            except:
                detail = resp.text
            return jsonify({'error': 'Translation provider error', 'details': detail}), 500
        j = resp.json()
        try:
            translation = j['choices'][0]['message']['content'].strip()
        except Exception:
            translation = str(j)
        return jsonify({'translation': translation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stt', methods=['POST'])
def stt():
    """
    Receive uploaded audio (field 'file').
    If OPENAI_API_KEY present -> call OpenAI Whisper transcription endpoint.
    Otherwise save file to static/uploads and return file path.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        f = request.files['file']
        if f.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        filename = secure_filename(f.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(save_path)

        if OPENAI_API_KEY:
            try:
                files = {
                    'file': (filename, open(save_path, 'rb')),
                    'model': (None, 'whisper-1')
                }
                headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
                resp = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files, timeout=120)
                if resp.status_code != 200:
                    try:
                        err = resp.json()
                    except:
                        err = resp.text
                    return jsonify({'error': 'STT provider error', 'details': err}), 500
                j = resp.json()
                transcription = j.get('text') or j.get('transcription') or ''
                return jsonify({'transcription': transcription})
            except Exception as e:
                return jsonify({'error': 'STT request failed', 'details': str(e)}), 500
        else:
            public_path = f"/static/uploads/{filename}"
            return jsonify({'message': 'File saved (no STT configured)', 'file': public_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
