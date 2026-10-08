import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.5-flash-lite:generateContent"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "response": "No information was received."
            }), 400

        help_type = data.get("helpType", "brainstorm")
        student_input = data.get("studentInput", "").strip()

        if not student_input:
            return jsonify({
                "response": "Please enter a question or idea first."
            })

        if not GEMINI_API_KEY:
            return jsonify({
                "response": "Gemini API key is not configured."
            }), 500

        instructions = {
            "brainstorm": """
You are an AI Study Assistant helping a college student brainstorm.

Give several possible directions, questions, examples, or starting
points.

Do not write a complete assignment for the student.

Help the student develop their own ideas.
""",

            "explain": """
You are an AI Study Assistant.

Explain the student's question clearly and simply.

Break difficult ideas into smaller parts.

Use examples when helpful.

The goal is to help the student understand the material.
""",

            "writing": """
You are an AI Study Assistant helping a college student improve
their own writing.

Give suggestions about grammar, clarity, organization, word choice,
and sentence structure.

Explain why your suggestions improve the writing.

Do not write an entire assignment for the student.
""",

            "study": """
You are an AI Study Assistant helping a college student study.

Create practice questions, explain concepts, make study guides,
provide examples, and identify topics the student should review.

Do not simply complete an assignment for the student.
"""
        }

        instruction = instructions.get(
            help_type,
            instructions["brainstorm"]
        )

        prompt = f"""
{instruction}

Student's request:

{student_input}

Respond directly to the student.

Keep your response clear, helpful, and appropriate for a college
student.

Help the student learn and think for themselves.
"""

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        print("Sending request to Gemini...")

        response = requests.post(
            GEMINI_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        print("Gemini status:", response.status_code)

        if response.status_code != 200:
            print("Gemini error:")
            print(response.text)

            return jsonify({
                "response": (
                        "Gemini API Error "
                        + str(response.status_code)
                        + ". Check the terminal for details."
                )
            }), 500

        result = response.json()

        try:
            ai_response = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

        except (KeyError, IndexError, TypeError):
            print("Unexpected Gemini response:")
            print(result)

            return jsonify({
                "response": "Gemini returned an unexpected response."
            }), 500

        return jsonify({
            "response": ai_response
        })

    except requests.exceptions.Timeout:
        print("Gemini request timed out.")

        return jsonify({
            "response": "The AI request timed out. Please try again."
        }), 500

    except requests.exceptions.RequestException as e:
        print("Request error:", e)

        return jsonify({
            "response": "Could not connect to Gemini."
        }), 500

    except Exception as e:
        print("Python error:", e)

        return jsonify({
            "response": "Something went wrong. Check the terminal."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)