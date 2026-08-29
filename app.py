from flask import Flask
from flask_jwt_extended import JWTManager



print("Step 1")

from routes.auth import auth

print("Step 2")

from routes.chat import chat

print("Step 3")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"


jwt = JWTManager(app) 

app.register_blueprint(auth)
app.register_blueprint(chat)

print("Step 4")

print("Routes:")
print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)