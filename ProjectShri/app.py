from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure API key is set
api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
if not api_key:
    raise ValueError("GOOGLE_AI_STUDIO_KEY is not set. Check your .env file.")

# Configure Google AI Studio API
genai.configure(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Secure secret key

# Dummy credentials for login (replace with a database in a real application)
USER_CREDENTIALS = {'admin': 'password123'}

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/chatbot", methods=["POST"])
def chatbot():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user_input = request.json.get("message")

    if not user_input:
        return jsonify({"error": "No message received"}), 400

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_input)

        if response.text:
            bot_reply = response.text
        else:
            bot_reply = "Sorry, I couldn't generate a response."
    except Exception as e:
        app.logger.error(f"Error in chatbot: {str(e)}")
        bot_reply = "Sorry, an error occurred while processing your request."

    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)