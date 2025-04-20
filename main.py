import os
import requests
import instaloader
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, Dispatcher, MessageHandler, filters
)

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app-name.koyeb.app/webhook

# Instaloader init
L = instaloader.Instaloader()

# Flask app
app = Flask(__name__)

# Bot + Dispatcher
bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()
dispatcher: Dispatcher = application.dispatcher


# Extract shortcode from URL
def extract_shortcode(url: str) -> str:
    url = url.strip('/')
    parts = url.split('/')
    for i in range(len(parts)):
        if parts[i] in ['p', 'reel', 'tv'] and i + 1 < len(parts):
            return parts[i + 1]
    return parts[-1] if len(parts[-1]) == 11 else ''


# Get media from shortcode
def get_media_url(shortcode: str) -> str:
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return post.video_url if post.is_video else post.url
    except:
        return None


# Command handler
async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /download <Instagram URL>")
        return

    url = context.args[0]
    await update.message.reply_text("Processing...")

    shortcode = extract_shortcode(url)
    if not shortcode:
        await update.message.reply_text("Invalid Instagram URL.")
        return

    media_url = get_media_url(shortcode)
    if not media_url:
        await update.message.reply_text("Failed to fetch media.")
        return

    ext = '.mp4' if media_url.endswith('.mp4') else '.jpg'
    filename = f"media{ext}"

    try:
        r = requests.get(media_url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with open(filename, 'rb') as f:
            if ext == '.mp4':
                await update.message.reply_video(f)
            else:
                await update.message.reply_photo(f)

        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Download error: {e}")


# Register handlers
dispatcher.add_handler(CommandHandler("download", download_command))


# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "ok", 200


# Setup webhook
@app.route("/")
def home():
    bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    return "Webhook set!", 200


# Start the Flask app
if __name__ == "__main__":
    app.run(port=5000)
      
