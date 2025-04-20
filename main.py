import os
import requests
import instaloader
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, ContextTypes, Application
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
loader = instaloader.Instaloader()

# Initialize Telegram application for handler usage
application = Application.builder().token(BOT_TOKEN).build()

def extract_shortcode(url: str) -> str:
    url = url.strip('/')
    parts = url.split('/')
    for i in range(len(parts)):
        if parts[i] in ['p', 'reel', 'tv'] and i + 1 < len(parts):
            return parts[i + 1]
    return parts[-1]

def get_media_url(shortcode: str) -> str:
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        return post.video_url if post.is_video else post.url
    except:
        return None

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        with open(filename, 'rb') as f:
            if ext == '.mp4':
                await update.message.reply_video(f)
            else:
                await update.message.reply_photo(f)

        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

application.add_handler(CommandHandler("download", download_command))

@app.route('/')
def home():
    bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    return 'Webhook set', 200

@app.route('/webhook', methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(application.process_update(update))
    return 'ok', 200

if __name__ == "__main__":
    app.run(port=5000)
    
