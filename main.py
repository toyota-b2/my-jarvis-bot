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
model = genai.GenerativeModel('gemini-2.5-flash')


# Εντολή /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Πώς μπορώ να σε βοηθήσω;")

# Κεντρικός μηχανισμός απάντησης
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_text_lower = user_text.lower()
    
    # Αν η πρόταση περιέχει λέξεις όπως "ειδήσεις" ή "νέα"
    if "ειδήσεις" in user_text_lower or "νεα" in user_text_lower or "νέα" in user_text_lower:
        await update.message.reply_text("🔄 Μαζεύω τις τελευταίες ειδήσεις...")
        
        # Λήψη RSS feed ειδήσεων
        feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
        top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:7]])
        
        prompt = (
            f"Ο χρήστης σου ζήτησε: '{user_text}'. "
            f"Είσαι ο Jarvis. Με βάση αυτούς τους τίτλους ειδήσεων, κάνε μια σύντομη και καθαρή ενημέρωση:\n\n{top_news}"
        )
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    
    # Για οποιαδήποτε άλλη συζήτηση ή ερώτηση
    else:
        prompt = (
            f"Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός AI βοηθός. "
            f"Απάντησε σύντομα και φυσικά στο εξής μήνυμα: {user_text}"
        )
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis είναι ενεργός...")
    app.run_polling()
