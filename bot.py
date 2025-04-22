import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # your https://xyz.koyeb.app

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram post URL!")

# Media downloader logic (simplified)
async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram post URL.")
        return

    # Dummy response (replace this with real downloader logic)
    await update.message.reply_text("Downloading media... (replace this with actual logic)")
    # You can integrate an API or scraping tool here to download and send the media

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

# Flask route for webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

# Health check route for Koyeb
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# Start webhook on port 8000
if __name__ == "__main__":
    import asyncio
    async def run():
        await bot_app.bot.set_webhook(f"{APP_URL}/webhook")
        app.run(port=8000, host="0.0.0.0")

    asyncio.run(run())
    
