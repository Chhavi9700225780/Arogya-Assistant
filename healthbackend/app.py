import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

from healthbackend.services.user_profile_store import save_profile, get_profile
from healthbackend.services.orchestrator import orchestrate
from healthbackend.services.history_store import get_history
from healthbackend.utils.exceptions import AuthError, InputError, AgentError
from healthbackend.services.user_auth_store import check_credentials
from healthbackend.config.settings import GOOGLE_API_KEY, MODEL_NAME
from healthbackend.services.user_auth_store import check_credentials, create_user
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# -------------------------
# Error Handlers
# -------------------------
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify({"error": str(e)}), 401


@app.errorhandler(InputError)
def input_error(e):
    return jsonify({"error": str(e)}), 400


# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if not check_credentials(username, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"status": "ok", "user_id": username})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    ok = create_user(username, password)
    if not ok:
        return jsonify({"error": "Username already exists"}), 409

    return jsonify({"status": "ok", "user_id": username})


# -------------------------
# Health Assist API
# -------------------------
@app.route("/health-assist", methods=["POST"])
def health_assist():
    data = request.get_json()

    if not data or "symptoms" not in data:
        raise InputError("Symptoms required")

    result = asyncio.run(
        orchestrate(
            data["symptoms"],
            data.get("medical_report"),
            data.get("user_id", "guest"),
        )
    )
    return jsonify(result)


# -------------------------
# Recommendation API
# -------------------------
@app.route("/recommendations", methods=["POST"])
def recommendations_only():
    data = request.get_json() or {}

    symptoms = data.get("symptoms")
    medical_report = data.get("medical_report", "")
    user_id = data.get("user_id", "guest")

    if not symptoms:
        raise InputError("Symptoms required")

    result = asyncio.run(
        orchestrate(
            symptoms,
            medical_report,
            user_id,
        )
    )

    return jsonify(
        {
            "query": symptoms,
            "recommendations": result.get("recommendations", []),
        }
    )


# -------------------------
# Follow-up API
# -------------------------
@app.route("/follow-up", methods=["POST"])
def follow_up():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    question = data.get("question", "").strip()

    if not user_id or not question:
        return jsonify({"error": "user_id and question are required"}), 400

    history = get_history(user_id) or []
    if not history:
        return jsonify({"error": "No previous wellness session found for this user"}), 400

    last = history[-1]

    context_text = (
        f"Previous wellness plan summary:\n{last.get('synthesized_guidance', '')}\n\n"
        f"Key recommendations:\n" + "\n".join(last.get("recommendations", []))
    )

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
        convert_system_message_to_human=True,
    )

    messages = [
        SystemMessage(
            content=(
                "You are a cautious wellness assistant answering follow-up questions "
                "about an existing wellness plan. Use the provided summary and "
                "recommendations as context. You may clarify, reorder, or restate "
                "information, but do NOT diagnose, do NOT prescribe medicines, and "
                "always remind the user to follow their doctor's advice."
            )
        ),
        HumanMessage(content=context_text),
        HumanMessage(content=f"User follow-up question: {question}"),
    ]

    result = llm.invoke(messages)
    return jsonify({"answer": result.content})


# -------------------------
# User Profile API
# -------------------------
@app.route("/profile/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    return jsonify({"user_id": user_id, "profile": get_profile(user_id)})


@app.route("/profile/<user_id>", methods=["POST"])
def save_user_profile_route(user_id):
    data = request.get_json() or {}
    profile = {
        "height_cm": data.get("height_cm"),
        "weight_kg": data.get("weight_kg"),
        "medications": data.get("medications", ""),
    }
    save_profile(user_id, profile)
    return jsonify({"user_id": user_id, "profile": profile})


# -------------------------
# History API
# -------------------------
@app.route("/history/<user_id>")
def history(user_id):
    return jsonify({"user_id": user_id, "history": get_history(user_id)})


@app.route("/", methods=["GET"])
def welcome_health():
    return "Welcome to Health & Diet Care"


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    # turn off reloader to avoid multiple processes / loops
    app.run(debug=False)
