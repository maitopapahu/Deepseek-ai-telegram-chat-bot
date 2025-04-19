import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")  # Generate using: openssl rand -hex 32

# Initialize application without webhook parameters
application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Webhook Bot Active!")

# Register handlers
application.add_handler(CommandHandler("start", start))

@app.post(f'/{SECRET_TOKEN}')
async def webhook():
    update = Update.de_json(await request.get_json(), application.bot)
    await application.process_update(update)
    return '', 200

@app.get('/')
def health_check():
    return "🤖 Server Running", 200

if __name__ == "__main__":
    # Set webhook programmatically
    url = f"https://your-app-name.koyeb.app/{SECRET_TOKEN}"
    await application.bot.set_webhook(url)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
