import os
import logging
import asyncio
import feedparser
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Ρύθμιση Logging
logging.basicConfig(level=logging.INFO)

# Σύνδεση με το Groq API
GROQ_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Μνήμη συνομιλίας ανά χρήστη
user_memories = {}

SYSTEM_PROMPT = (
    "Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός προσωπικός AI βοηθός. "
    "Θυμάσαι τις πληροφορίες που σου δίνει ο χρήστης στη συζήτηση "
    "και απαντάς πάντα στα ελληνικά."
)

# Εντολή /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_memories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Τώρα είμαι ενεργός! Στείλε μου μήνυμα για να δοκιμάσουμε.")

# Κεντρικός μηχανισμός επεξεργασίας μηνυμάτων
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_text_lower = user_text.lower()

    if not GROQ_KEY:
        await update.message.reply_text("⚠️ Λείπει το GROQ_API_KEY από τις μεταβλητές του Railway!")
        return

    if user_id not in user_memories:
        user_memories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    try:
        # Αν η εντολή αφορά ειδήσεις
        if "ειδήσεις" in user_text_lower or "νεα" in user_text_lower or "νέα" in user_text_lower:
            await update.message.reply_text("🔄 Μαζεύω τις τελευταίες ειδήσεις...")
            
            feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
            top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:7]])
            
            prompt = f"Ο χρήστης ζήτησε ειδήσεις: '{user_text}'. Με βάση αυτούς τους τίτλους, κάνε μια γρήγορη σύνοψη:\n\n{top_news}"
            user_memories[user_id].append({"role": "user", "content": prompt})
            
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",

                messages=user_memories[user_id]
            )
            
            bot_reply = response.choices[0].message.content
            user_memories[user_id].append({"role": "assistant", "content": bot_reply})
            await update.message.reply_text(bot_reply)

        # Για οποιαδήποτε άλλη κουβέντα
        else:
            user_memories[user_id].append({"role": "user", "content": user_text})
            
            if len(user_memories[user_id]) > 21:
                user_memories[user_id] = [user_memories[user_id][0]] + user_memories[user_id][-20:]

            response = groq_client.chat.completions.create(
                model="llama3-8b-8192",

                messages=user_memories[user_id]
            )
            
            bot_reply = response.choices[0].message.content
            user_memories[user_id].append({"role": "assistant", "content": bot_reply})
            await update.message.reply_text(bot_reply)

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await update.message.reply_text(f"⚠️ Σφάλμα: {str(e)}")

async def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Δεν βρέθηκε TELEGRAM_TOKEN!")
        return

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
