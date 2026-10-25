from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from groq import Groq

app = Flask(__name__)

# Load environment variables from .env
load_dotenv()

# Read the Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from the .env file")

# Initialize the Groq API client
client = Groq(api_key=api_key)

# Select a model supported by Groq (llama-3.3-70b-versatile was retired on 2026-08-16)
MODEL = "openai/gpt-oss-120b"


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Act like a helpful personal assistant."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.7,
            max_completion_tokens=512
        )

        answer = response.choices[0].message.content

        return jsonify({"response": answer}), 200

    except Exception:
        app.logger.exception("Error while processing the question")
        return jsonify({
            "error": "Unable to generate an answer. Please try again."
        }), 500


@app.route("/summarize", methods=["POST"])
def summarize():
    email_text = request.form.get("email", "").strip()

    if not email_text:
        return jsonify({"error": "Please enter email content."}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert email assistant. "
                        "Summarize emails in 2-3 sentences. "
                        "Preserve important dates, decisions, "
                        "action items, and deadlines."
                    )
                },
                {
                    "role": "user",
                    "content": email_text
                }
            ],
            temperature=0.3,
            max_completion_tokens=512
        )

        summary = response.choices[0].message.content

        return jsonify({"response": summary}), 200

    except Exception:
        app.logger.exception("Error while summarizing the email")
        return jsonify({
            "error": "Unable to summarize the email. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)