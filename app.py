from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ============================================================
# PUT YOUR GEMINI API KEY HERE
# Keep the actual key only on your computer.
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    print("\n========================================")
    print("POST /ask RECEIVED")
    print("========================================")

    try:
        # Get information from the website
        data = request.get_json()

        print("Website data:", data)

        if not data:
            return jsonify({
                "response": "No information was received."
            }), 400

        help_type = data.get("helpType", "brainstorm")
        student_input = data.get("studentInput", "").strip()

        # Make sure the student actually entered something
        if not student_input:
            return jsonify({
                "response": "Please enter a question or idea first."
            })

        # Check API key
        if (
                not GEMINI_API_KEY
                or GEMINI_API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE"
        ):
            print("ERROR: Gemini API key is missing.")

            return jsonify({
                "response": "Gemini API key is missing from app.py."
            }), 500

        # ============================================================
        # Instructions for each study assistant mode
        # ============================================================
        instructions = {

            "brainstorm": """
You are an AI Study Assistant.

Help a college student brainstorm ideas without doing the assignment
for them.

Give several possible directions, questions, examples, or starting
points.

Do not write a complete essay or assignment for the student.

Encourage the student to develop their own ideas.
""",

            "explain": """
You are an AI Study Assistant.

Explain the student's question clearly and simply.

Break difficult ideas into smaller parts.

Use examples when helpful.

The goal is to help the student understand the material.
""",

            "writing": """
You are an AI Study Assistant.

Help the student improve their own writing.

Give suggestions about grammar, clarity, organization, word choice,
and sentence structure.

Explain why the suggestions would improve the writing.

Do not write an entire assignment for the student.
""",

            "study": """
You are an AI Study Assistant.

Help the student study.

Create practice questions, explain concepts, make study guides,
provide examples, and identify topics the student should review.

Do not simply complete an assignment for the student.
"""
        }

        # Select the correct instructions
        instruction = instructions.get(
            help_type,
            instructions["brainstorm"]
        )

        # ============================================================
        # Build the prompt sent to Gemini
        # ============================================================
        prompt = f"""
{instruction}

Student's request:

{student_input}

Respond directly to the student.

Keep your response clear, helpful, and appropriate for a college
student.

Help the student learn and think for themselves.
"""

        # ============================================================
        # Gemini API
        # ============================================================
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-3.5-flash-lite:generateContent"
        )

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

        print("\nSENDING REQUEST TO GEMINI...")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("Gemini status code:", response.status_code)

        # ============================================================
        # If Gemini gives an error
        # ============================================================
        if response.status_code != 200:

            print("\n========== GEMINI ERROR ==========")
            print("Status Code:", response.status_code)
            print("Response:")
            print(response.text)
            print("==================================\n")

            return jsonify({
                "response": (
                        "Gemini API Error "
                        + str(response.status_code)
                        + ". Check IntelliJ terminal for details."
                )
            }), 500

        # ============================================================
        # Convert Gemini response to JSON
        # ============================================================
        result = response.json()

        print("Gemini responded successfully.")

        # ============================================================
        # Get the actual AI text
        # ============================================================
        try:
            ai_response = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

        except (KeyError, IndexError, TypeError):

            print("\n========== UNEXPECTED RESPONSE ==========")
            print(result)
            print("==========================================\n")

            return jsonify({
                "response": "Gemini returned an unexpected response."
            }), 500

        # Send response back to website
        return jsonify({
            "response": ai_response
        })

    # ================================================================
    # Timeout error
    # ================================================================
    except requests.exceptions.Timeout:

        print("\n========== TIMEOUT ==========")
        print("Gemini took too long to respond.")
        print("=============================\n")

        return jsonify({
            "response": "The AI request timed out. Please try again."
        }), 500

    # ================================================================
    # Connection/request error
    # ================================================================
    except requests.exceptions.RequestException as e:

        print("\n========== REQUEST ERROR ==========")
        print(e)
        print("===================================\n")

        return jsonify({
            "response": "Could not connect to Gemini."
        }), 500

    # ================================================================
    # Any other Python error
    # ================================================================
    except Exception as e:

        print("\n========== PYTHON ERROR ==========")
        print(e)
        print("==================================\n")

        return jsonify({
            "response": "Something went wrong. Check IntelliJ."
        }), 500


# ============================================================
# Start Flask
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)