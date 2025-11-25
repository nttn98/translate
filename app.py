from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Groq API key and model from .env file
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Default to llama-3.3-70b-versatile

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    """Translate Vietnamese text to English using Groq API"""
    try:
        data = request.json
        text = data.get('text', '')

        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400

        # Call Groq API (OpenAI-compatible endpoint)
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}'
            },
            json={
                'model': GROQ_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional Vietnamese to English translator. Translate the text accurately and naturally. Only provide the translation, no explanations.'
                    },
                    {
                        'role': 'user',
                        'content': text
                    }
                ],
                'temperature': 0.3,  # Lower temperature for more consistent translations
                'max_tokens': 1000
            }
        )

        if response.status_code == 200:
            result = response.json()
            translation = result['choices'][0]['message']['content'].strip()
            return jsonify({'translation': translation})
        else:
            error_detail = response.json() if response.text else 'Unknown error'
            return jsonify({'error': 'Translation failed', 'details': error_detail}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

