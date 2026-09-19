import os
import logging
import asyncio
import requests
import feedparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"

user_memories = {}

def query_huggingface(messages):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": messages[-1]["content"],
        "parameters": {"max_new_tokens": 500, "return_full_text": False}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "Δεν πήρα απάντηση.")
    elif "error" in result:
        return f"⚠️ HF Error: {result['error']}"
    return "⚠️ Σφάλμα απόκρισης."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_memories[user_id] = []
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Έτοιμος για λειτουργία χωρίς όρια!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_text_lower = user_text.lower()

    if not HF_TOKEN:
        await update.message.reply_text("⚠️ Λείπει το HF_TOKEN!")
        return

    try:
        if "ειδήσεις" in user_text_lower or "νεα" in user_text_lower or "νέα" in user_text_lower:
            await update.message.reply_text("🔄 Μαζεύω τις τελευταίες ειδήσεις...")
            feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
            top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:7]])
            prompt = f"Είσαι ο Jarvis. Συνοψισε τις ειδήσεις στα ελληνικά:\n\n{top_news}"
            
            reply = query_huggingface([{"role": "user", "content": prompt}])
            await update.message.reply_text(reply)
        else:
            prompt = f"Είσαι ο Jarvis, ένας φιλικός AI βοηθός. Απάντησε στα ελληνικά στο εξής: {user_text}"
            reply = query_huggingface([{"role": "user", "content": prompt}])
            await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Σφάλμα: {str(e)}")

async def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis ξεκινάει...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
