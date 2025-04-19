import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")  # Generate random string for webhook verification
PORT = int(os.environ.get("PORT", 8000))

# Initialize bot
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Webhook Bot Active!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔁 Echo: {update.message.text}")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.post(f'/{SECRET_TOKEN}')
async def webhook():
    update = Update.de_json(request.get_json(), bot)
    await application.process_update(update)
    return '', 200

@app.get('/')
def health_check():
    return "🤖 Bot Server Running", 200

if __name__ == "__main__":
    # Set webhook when starting
    url = f"https://your-app-name-12345.koyeb.app/{SECRET_TOKEN}"
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=SECRET_TOKEN,
        webhook_url=url
    )
    app.run(port=PORT)
