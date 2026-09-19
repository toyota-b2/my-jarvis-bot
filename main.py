import os
import logging
import json
import urllib.request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def call_groq_api(prompt_text):
    if not GROQ_API_KEY:
        return "⚠️ Λείπει το GROQ_API_KEY από τις μεταβλητές περιβάλλοντος!"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός AI βοηθός. Απάντα πάντα στα ελληνικά."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.7
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            return "Δεν πήρα έγκυρη απάντηση."
    except urllib.error.HTTPError as e:
        return f"⚠️ Σφάλμα API ({e.code}): Βεβαιώσου ότι το GROQ_API_KEY στο Railway είναι σωστό!"
    except Exception as e:
        return f"⚠️ Σφάλμα: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Τώρα είμαι έτοιμος και λειτουργώ 100%!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = call_groq_api(user_text)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("⚠️ Δεν βρέθηκε TELEGRAM_TOKEN!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Ο Jarvis ξεκινάει επιτυχώς...")
        app.run_polling(drop_pending_updates=True)
