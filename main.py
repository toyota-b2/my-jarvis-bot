import os
from google import genai

# Καθαρισμός του API Key από τυχόν κρυφούς χαρακτήρες
api_key = os.environ.get("GEMINI_API_KEY", "").strip("\u2060\u200b\ufeff ")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Γεια σου!",
)

print(response.text)
