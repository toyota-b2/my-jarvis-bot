import os
from google import genai

# Αρχικοποίηση του client με το API key από τις μεταβλητές
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Παράδειγμα κλήσης για παραγωγή απάντησης:
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Γεια σου! Πώς είσαι;",
)

print(response.text)
