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
model = genai.GenerativeModel('gemini-1.5-flash')

# Εντολή /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Πώς μπορώ να σε βοηθήσω σήμερα;")

# Εντολή για Ειδήσεις (/news)
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
    top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:5]])
    
    prompt = f"Κάνε μια γρήγορη, σύντομη σύνοψη για τις εξής ειδήσεις:\n{top_news}"
    response = model.generate_content(prompt)
    
    await update.message.reply_text(f"📰 **Τελευταίες Ειδήσεις:**\n\n{response.text}")

# Απάντηση σε μηνύματα
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = model.generate_content(f"Είσαι ο Jarvis, ένας έξυπνος AI βοηθός. Απάντησε σύντομα: {user_text}")
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis ξεκίνησε...")
    app.run_polling()
