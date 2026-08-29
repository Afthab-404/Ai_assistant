from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import chats, profiles
from gemini_service import get_ai_response

chat = Blueprint("chat", __name__)


@chat.route("/chat", methods=["POST"])
@jwt_required()
def chat_ai():
    current_user = get_jwt_identity()

    data = request.json
    message = data["message"]

    history = list(
        chats.find({"user": current_user})
        .sort("_id", -1)
        .limit(5)
    )

    context = ""

    for chat_item in reversed(history):
        context += f"""
User: {chat_item['message']}
Assistant: {chat_item['reply']}
"""

    profile = profiles.find_one(
        {"email": current_user},
        {"_id": 0}
    )

    full_prompt = f"""
User Profile:

{profile}

Previous Conversation:

{context}

Current User Message:

{message}
"""

    reply = get_ai_response(full_prompt)

    chats.insert_one({
        "user": current_user,
        "message": message,
        "reply": reply
    })

    return jsonify({
        "user": current_user,
        "reply": reply
    })


@chat.route("/history", methods=["GET"])
@jwt_required()
def history():
    current_user = get_jwt_identity()

    history = list(
        chats.find(
            {"user": current_user},
            {"_id": 0}
        )
    )

    return jsonify(history)


@chat.route("/profile", methods=["POST"])
@jwt_required()
def save_profile():
    current_user = get_jwt_identity()

    data = request.json

    profiles.update_one(
        {"email": current_user},
        {
            "$set": data
        },
        upsert=True
    )

    return jsonify({
        "message": "Profile saved"
    })
