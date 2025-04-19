# bot.py
import os
import cohere
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
MODEL_NAME = "command"  # Cohere model name

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello! I'm a Cohere-powered AI assistant.\n"
        "You can ask me anything - I'm here to help!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # Generate response using Cohere
        response = co.chat(
            message=user_message,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=300
        )

        await update.message.reply_text(response.text)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot is running...")
    app.run_polling()
