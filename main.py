import os
import logging
import feedparser
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Ρύθμιση Logging
logging.basicConfig(level=logging.INFO)

# Σύνδεση με το Gemini API
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

# Αρχικοποίηση μοντέλου
model = genai.GenerativeModel('gemini-3.6-flash')

# Λεξικό για διατήρηση της μνήμης (Chat Session) ανά χρήστη
user_chats = {}

# Εντολή /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats[user_id] = model.start_chat(history=[])
    
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Πώς μπορώ να σε βοηθήσω;")

# Κεντρικός μηχανισμός επεξεργασίας μηνυμάτων
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_text_lower = user_text.lower()

    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    chat = user_chats[user_id]

    try:
        # Αν η εντολή αφορά ειδήσεις
        if "ειδήσεις" in user_text_lower or "νεα" in user_text_lower or "νέα" in user_text_lower:
            await update.message.reply_text("🔄 Μαζεύω τις τελευταίες ειδήσεις...")
            
            feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
            top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:7]])
            
            prompt = (
                f"Ο χρήστης ζήτησε ενημέρωση ειδήσεων: '{user_text}'. "
                f"Με βάση αυτούς τους τίτλους ειδήσεων, κάνε μια σύντομη και καθαρή σύνοψη:\n\n{top_news}"
            )
            response = chat.send_message(prompt)
            await update.message.reply_text(response.text)

        # Για οποιαδήποτε άλλη πρόταση / ερώτηση
        else:
            response = chat.send_message(user_text)
            await update.message.reply_text(response.text)

    except ResourceExhausted:
        await update.message.reply_text("⚠️ Ξεπεράστηκε το δωρεάν όριο αιτημάτων του Gemini API. Παρακαλώ περίμενε 1 λεπτό και δοκίμασε ξανά!")
    except GoogleAPIError as e:
        await update.message.reply_text("⚠️ Υπήρξε ένα πρόβλημα με το AI. Δοκίμασε σε λίγο.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Υπήρξε ένα άγνωστο σφάλμα.")

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis είναι ενεργός...")
    app.run_polling()
