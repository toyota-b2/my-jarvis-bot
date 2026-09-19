import os
import logging
import feedparser
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Ρύθμιση Logging
logging.basicConfig(level=logging.INFO)

# Σύνδεση με το Groq API (Δωρεάν & Υπερταχύ)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Μνήμη συνομιλίας ανά χρήστη
user_memories = {}

# Εντολή /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_memories[user_id] = [
        {"role": "system", "content": "Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός προσωπικός AI βοηθός. Θυμάσαι τις πληροφορίες που σου δίνει ο χρήστης στη συζήτηση (όπως το όνομά του ή την περιοχή του) και απαντάς πάντα στα ελληνικά."}
    ]
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Τώρα κινούμαι με υπερηχητική ταχύτητα χωρίς όρια! Πώς μπορώ να σε βοηθήσω;")

# Κεντρικός μηχανισμός επεξεργασίας μηνυμάτων
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_text_lower = user_text.lower()

    # Αρχικοποίηση μνήμης αν δεν υπάρχει
    if user_id not in user_memories:
        user_memories[user_id] = [
            {"role": "system", "content": "Είσαι ο Jarvis, ένας έξυπνος, φιλικός και εξυπηρετικός προσωπικός AI βοηθός. Θυμάσαι τις πληροφορίες που σου δίνει ο χρήστης στη συζήτηση (όπως το όνομά του ή την περιοχή του) και απαντάς πάντα στα ελληνικά."}
        ]

    # Αν η εντολή αφορά ειδήσεις
    if "ειδήσεις" in user_text_lower or "νεα" in user_text_lower or "νέα" in user_text_lower:
        await update.message.reply_text("🔄 Μαζεύω τις τελευταίες ειδήσεις...")
        
        feed = feedparser.parse("https://news.google.com/rss?hl=el&gl=GR&ceid=GR:el")
        top_news = "\n\n".join([f"• {item.title}" for item in feed.entries[:7]])
        
        prompt = f"Ο χρήστης ζήτησε ειδήσεις: '{user_text}'. Με βάση αυτούς τους τίτλους, κάνε μια γρήγορη σύνοψη:\n\n{top_news}"
        
        # Προσθήκη στο ιστορικό
        user_memories[user_id].append({"role": "user", "content": prompt})
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_memories[user_id]
        )
        
        bot_reply = response.choices[0].message.content
        user_memories[user_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)

    # Για οποιαδήποτε άλλη κουβέντα (με πλήρη μνήμη)
    else:
        user_memories[user_id].append({"role": "user", "content": user_text})
        
        # Περιορισμός ιστορικού στα τελευταία 20 μηνύματα για οικονομία
        if len(user_memories[user_id]) > 20:
            user_memories[user_id] = [user_memories[user_id][0]] + user_memories[user_id][-19:]

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_memories[user_id]
        )
        
        bot_reply = response.choices[0].message.content
        user_memories[user_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)

if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Ο Jarvis είναι ενεργός μέσω Groq...")
    app.run_polling()
