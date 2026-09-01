from flask import Flask
from flask_jwt_extended import JWTManager

from routes.auth import auth
from routes.chat import chat

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app) 


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

app.register_blueprint(auth)
app.register_blueprint(chat)

print("Routes:")
print(app.url_map)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
