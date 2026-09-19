import os
import logging
import asyncio
import json
import urllib.request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

HF_TOKEN = os.environ.get("HF_TOKEN")
# Χρήση του ανοιχτού μοντέλου Qwen2.5 μέσω Inference API
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"

user_memories = {}

def call_huggingface(prompt_text):
    if not HF_TOKEN:
        return "⚠️ Λείπει το HF_TOKEN από τις μεταβλητές περιβάλλοντος!"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": f"<|im_start|>system\nΕίσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός AI βοηθός. Απάντα πάντα στα ελληνικά.<|im_end|>\n<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n",
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7
        }
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if isinstance(result, list) and len(result) > 0:
                full_text = result[0].get("generated_text", "")
                # Καθαρισμός απάντησης
                if "<|im_start|>assistant\n" in full_text:
                    return full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
                return full_text
            return "Δεν πήρα έγκυρη απάντηση."
    except Exception as e:
        return f"⚠️ Σφάλμα API: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Τώρα λειτουργώ χωρίς εξωτερικές εξαρτήσεις και χωρίς όρια!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Ειδοποίηση ότι ο Jarvis σκέφτεται
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Κλήση στο API
    reply = call_huggingface(user_text)
    await update.message.reply_text(reply)

async def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("⚠️ Δεν βρέθηκε TELEGRAM_TOKEN!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis ξεκινάει επιτυχώς...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
