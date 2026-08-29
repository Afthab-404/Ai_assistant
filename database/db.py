from pymongo import MongoClient

client = MongoClient("mongodb://Localhost:27017")
db = client["ai_assistant"]

users = db["users"]
chats = db["chats"]
profiles = db["profiles"]