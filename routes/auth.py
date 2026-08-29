from flask import Blueprint, request, jsonify
from database.db import users
import bcrypt
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["POST"])
def signup():


    data = request.json

    username = data["username"]
    email = data["email"]
    password = data["password"]

    existing_user = users.find_one({"email": email})

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password
    })

    return jsonify({
        "message": "User registered successfully"
    })
    
@auth.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data["email"]
    password = data["password"]

    user = users.find_one({"email": email})

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):

        token = create_access_token(
            identity=email
        )

        return jsonify({
            "message": "Login successful",
            "token": token
        })

    return jsonify({
        "message": "Wrong password"
    }), 401
    
    