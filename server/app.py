import os
import requests
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
import time

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("Error: Hugging Face API key is missing!")

HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

# Initialize Firebase
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "babble-8e814-firebase-adminsdk-fbsvc-052260f205.json"))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# AI Model Selection
PRIMARY_MODEL = "meta-llama/Llama-2-7b-chat-hf"  # More reliable than GPT-2
BACKUP_MODEL = "meta-llama/Llama-2-13b-chat-hf"  # Stronger backup model


def create_default_lesson(speech_issue):
    """Creates a structured fallback lesson plan."""
    return f"""
Speech Therapy Lesson Plan: {speech_issue}

Goals
- Improve pronunciation of '{speech_issue}'.
- Increase confidence in speaking.
- Develop effective communication skills.

Warm-up (10 minutes)
1. Take deep breaths to relax vocal cords.
2. Perform gentle mouth and tongue stretches.
3. Say simple vowel sounds clearly.

Core Practice (20 minutes)
1. Sound Awareness - Listen to recordings and identify correct pronunciation.
2. Mimicry - Repeat the sounds while looking in the mirror.
3. Word Building - Practice difficult words in isolation.
4. Sentence Flow - Move to short sentences and paragraphs.

Confidence Exercises (10 minutes)
- Read aloud in a slow, controlled voice.
- Record and compare your speech over time.
- Engage in guided conversation with a friend.

Daily Routine - 
Morning: Sound drills
Afternoon: Word repetition
Evening: Conversation practice

Practicing daily for at least 20 minutes leads to noticeable improvement!
"""


def request_ai_response(prompt, model):
    """Requests AI-generated text using Llama-2 with structured outputs."""
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,  # Increase tokens for a detailed lesson
                "temperature": 0.7,
                "top_p": 0.9,
                "stop_sequences": ["\n\n"]  # Helps prevent incomplete responses
            }
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        print(f"API Attempt {attempt + 1} (Model: {model}): Status Code {response.status_code}")

        if response.status_code == 200:
            try:
                response_json = response.json()
                print("Full AI Response:", response_json)

                if isinstance(response_json, list) and len(response_json) > 0:
                    lesson_text = response_json[0].get("generated_text", "").strip()

                    # 🚨 Filter out invalid responses 🚨
                    if lesson_text in ["User", "---", "I hope this helps!"] or len(lesson_text.split()) < 50:
                        print("⚠️ AI Response Invalid (too short or contains placeholders):", lesson_text)
                        return None  # Retry with another model

                    return lesson_text  # Valid response

            except Exception as e:
                print("Error processing AI response:", str(e))

        time.sleep(2 ** attempt)  # Exponential backoff

    return None  # If all retries fail, return None instead of crashing


@app.route("/generate_lesson", methods=["POST"])
def generate_lesson():
    """Generates a concise lesson plan using AI or default fallback."""
    try:
        data = request.json
        user_id = data.get("user_id", "").strip()
        speech_issue = data.get("speech_issue", "").strip()

        if not user_id or not speech_issue:
            return jsonify({"error": "Missing required fields"}), 400

        # Request AI-generated lesson
        prompt = f"Generate a structured speech therapy lesson plan for improving '{speech_issue}' pronunciation."
        lesson_text = request_ai_response(prompt, PRIMARY_MODEL)

        # If primary model fails, try backup model
        if not lesson_text:
            print("⚠️ Primary AI model failed. Trying backup model...")
            lesson_text = request_ai_response(prompt, BACKUP_MODEL)

        # If AI still fails, use a default lesson template
        if not lesson_text:
            print("⚠️ AI failed completely. Using default lesson format.")
            lesson_text = create_default_lesson(speech_issue)

        # Store in Firebase
        try:
            db.collection("lessons").document(user_id).set({
                "lesson": lesson_text,
                "speech_issue": speech_issue,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print(f"Firebase error: {str(e)}")

        # Generate PDF
        pdf_filename = f"lesson_{user_id}.pdf"
        pdf_path = os.path.join("pdfs", pdf_filename)
        os.makedirs("pdfs", exist_ok=True)

        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            margin = 40
            y_position = height - 50

            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin, y_position, f"Speech Therapy Lesson Plan: {speech_issue}")
            y_position -= 30

            c.setFont("Helvetica", 12)
            for line in lesson_text.split("\n"):
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
                c.drawString(margin, y_position, line)
                y_position -= 18

            c.save()
        except Exception as e:
            print(f"PDF generation error: {str(e)}")

        return jsonify({
            "lesson": lesson_text,
            "pdf_url": f"/download_lesson/{user_id}"
        })

    except Exception as e:
        print(f"Error in generate_lesson: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/download_lesson/<user_id>", methods=["GET"])
def download_lesson(user_id):
    """Downloads the generated PDF."""
    try:
        pdf_path = os.path.join("pdfs", f"lesson_{user_id}.pdf")
        if not os.path.exists(pdf_path):
            return jsonify({"error": "Lesson PDF not found"}), 404
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print(f"Error downloading lesson: {str(e)}")
        return jsonify({"error": "Error downloading PDF"}), 500


if __name__ == "__main__":
    app.run(debug=True)
