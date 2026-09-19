import os
import logging
import feedparser
import google.generativeai as genai
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
    # Δημιουργία νέας συνεδρίας συνομιλίας με οδηγίες προσωπικότητας
    user_chats[user_id] = model.start_chat(history=[])
    system_instruction = (
        "Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός προσωπικός AI βοηθός. "
        "Θυμάσαι τις πληροφορίες που σου δίνει ο χρήστης στη συζήτηση (όπως το όνομά του ή την περιοχή του) "
        "και τις χρησιμοποιείς για να απαντάς φυσικά."
    )
    user_chats[user_id].send_message(system_instruction)
    
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Πλέον έχω πλήρη μνήμη! Πώς μπορώ να σε βοηθήσω;")

# Κεντρικός μηχανισμός επεξεργασίας μηνυμάτων
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_text_lower = user_text.lower()

    # Δημιουργία συνεδρίας αν δεν υπάρχει ήδη
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    chat = user_chats[user_id]

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

    # Για οποιαδήποτε άλλη πρόταση / ερώτηση (χρησιμοποιεί τη μνήμη του chat)
    else:
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis είναι ενεργός με μνήμη...")
    app.run_polling()
