import os
import re
import traceback
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

GROQ_KEY = (os.getenv("GROQ_API_KEY") or "").strip() or None
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


@app.route("/")
def index():
    return render_template("index.html")


def looks_like_vietnamese(text: str) -> bool:
    """
    Heuristic đơn giản để quyết định có nên gọi model dịch hay không.
    Nếu không giống tiếng Việt -> trả về "" luôn, KHÔNG gọi model.
    """
    t = (text or "").strip()
    if not t:
        return False

    # Có ít nhất 1 ký tự tiếng Việt có dấu
    viet_chars = re.findall(r"[À-Ỵà-ỵĂăÂâÊêÔôƠơƯưĐđ]", t)
    if len(viet_chars) >= 1:
        return True

    # Hoặc: nhiều chữ cái, ít số -> khả năng là text tự nhiên (VN không dấu)
    letters = re.findall(r"[A-Za-z]", t)
    digits = re.findall(r"\d", t)
    if len(letters) >= 4 and len(digits) <= len(letters):
        return True

    return False


def sanitize_model_output(out: str) -> str:
    """
    Chỉ làm nhẹ nhàng:
      - Bỏ khoảng trắng 2 đầu
      - Bỏ ngoặc kép bao quanh, nếu có
      - Bỏ prefix kiểu 'Translation:' nếu model lỡ nói nhiều
    KHÔNG tự ý drop output nữa, để đảm bảo model chỉ dịch và mình dùng nguyên bản dịch đó.
    """
    if not out:
        return ""

    translation = out.strip()

    # Bỏ ngoặc kép bao quanh, nếu có
    if (
        len(translation) >= 2
        and (
            (translation[0] == '"' and translation[-1] == '"')
            or (translation[0] == "“" and translation[-1] == "”")
        )
    ):
        translation = translation[1:-1].strip()

    lowered = translation.lower().lstrip()

    COMMON_PREFIXES = [
        "translation:",
        "english translation:",
        "english:",
        "here is the translation:",
        "here is the english translation:",
        "translated text:",
        "the translation is:",
    ]
    for p in COMMON_PREFIXES:
        if lowered.startswith(p):
            idx = lowered.find(p) + len(p)
            cut_pos = len(translation) - len(lowered) + idx
            translation = translation[cut_pos:].strip()
            break

    return translation


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(force=True)
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "no_text"}), 400

        # Không dịch nếu quá ít chữ cái (noise)
        letters = re.sub(r"[^A-Za-zÀ-Ỵà-ỵĂăÂâÊêÔôƠơƯưĐđ]", "", text)
        if len(letters) < 2:
            return jsonify({"translation": ""}), 200

        # Nếu không giống tiếng Việt -> không gọi model, trả rỗng
        if not looks_like_vietnamese(text):
            return jsonify({"translation": ""}), 200

        if GROQ_KEY:
            try:
                # MODEL CHỈ DỊCH VI → EN, KHÔNG LÀM GÌ KHÁC
                system_prompt = (
                    "You are a pure Vietnamese-to-English translation engine.\n"
                    "- Your ONLY task is to translate the user's Vietnamese text into natural, fluent English.\n"
                    "- Always output ONLY the English translation.\n"
                    "- Do NOT explain.\n"
                    "- Do NOT add any extra words like 'Here is the translation'.\n"
                    "- Do NOT ask questions.\n"
                    "- Do NOT repeat the Vietnamese text.\n"
                    "- Do NOT change the meaning, but you may adjust grammar and wording for natural English.\n"
                )

                payload = {
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 500,
                }

                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_KEY}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30,
                )

                if resp.status_code == 200:
                    j = resp.json()
                    raw_out = j["choices"][0]["message"]["content"]
                    cleaned = sanitize_model_output(raw_out)
                    return jsonify({"translation": cleaned}), 200

                print("Groq non-200:", resp.status_code, resp.text[:400])

            except Exception:
                print("Groq exception:", traceback.format_exc())

        # Không có GROQ_KEY hoặc lỗi -> trả rỗng (frontend sẽ ignore)
        return jsonify({"translation": ""}), 200

    except Exception:
        print("TRANSLATE unexpected:", traceback.format_exc())
        return jsonify({"translation": ""}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
