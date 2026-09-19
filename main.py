import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Ρύθμιση Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ανάκτηση μεταβλητών από το περιβάλλον (Railway Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Έλεγχος αν υπάρχουν τα Keys
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Λείπει το TELEGRAM_BOT_TOKEN! Πρόσθεσέ το στα Variables του Railway.")
if not GROQ_API_KEY:
    raise ValueError("❌ Λείπει το GROQ_API_KEY! Πρόσθεσέ το στα Variables του Railway.")

# Αρχικοποίηση Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Εντολή /start"""
    await update.message.reply_text("Γεια σου! Είμαι ο Jarvis. Στείλε μου μήνυμα για να μιλήσουμε!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Διαχείριση μηνυμάτων από τον χρήστη"""
    user_text = update.message.text
    
    try:
        # Κλήση στο Groq API με το νέο ενεργό μοντέλο
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Είσαι ένας χρήσιμος, φιλικός και έξυπνος AI βοηθός με το όνομα Jarvis."
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        # Απάντηση στον χρήστη
        bot_response = chat_completion.choices[0].message.content
        await update.message.reply_text(bot_response)

    except Exception as e:
        logger.error(f"Σφάλμα κατά την επεξεργασία: {e}")
        await update.message.reply_text("⚠️ Προέκυψε σφάλμα κατά την επικοινωνία με το Groq API.")

def main() -> None:
    """Εκκίνηση του Bot"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Εκκίνηση Bot
    logger.info("Το Telegram Bot ξεκίνησε...")
    app.run_polling()

if __name__ == "__main__":
    main()
