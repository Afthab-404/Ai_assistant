import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


print("Gemini API Loaded Successfully")

client = genai.Client(api_key=api_key)

def get_ai_response(message):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=message
    )

    return response.text