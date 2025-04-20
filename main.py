import os
import requests
import instaloader
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# Flask app
app = Flask(__name__)

# Load token and webhook from env
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Telegram bot
bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Instaloader for scraping
L = instaloader.Instaloader()

# Extract shortcode from Instagram URL
def extract_shortcode(url: str) -> str:
    parts = url.strip('/').split('/')
    for i in range(len(parts)):
        if parts[i] in ['p', 'reel', 'tv'] and i + 1 < len(parts):
            return parts[i + 1]
    return parts[-1]

# Get media link (image/video)
def get_media_url(shortcode: str) -> str:
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return post.video_url if post.is_video else post.url
    except Exception as e:
        print("Error:", e)
        return None

# Command: /download <url>
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /download <Instagram URL>")
        return

    url = context.args[0]
    shortcode = extract_shortcode(url)
    media_url = get_media_url(shortcode)

    if not media_url:
        await update.message.reply_text("Failed to retrieve media.")
        return

    ext = '.mp4' if media_url.endswith('.mp4') else '.jpg'
    filename = f"media{ext}"
    try:
        r = requests.get(media_url, stream=True)
        with open(filename, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        with open(filename, "rb") as f:
            if ext == '.mp4':
                await update.message.reply_video(f)
            else:
                await update.message.reply_photo(f)

        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Error sending media: {e}")

# Add Telegram handler
application.add_handler(CommandHandler("download", download))

# Flask route to set webhook
@app.route("/")
def index():
    bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    return "Webhook set!", 200

# Webhook receiver
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
    
