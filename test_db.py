from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["ai_assistant"]

users = db["users"]

users.insert_one({
    "name": "Afthab"
})

print("MongoDB Connected Successfully")