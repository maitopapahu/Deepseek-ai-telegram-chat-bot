import os
import logging
import yt_dlp
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables for Telegram bot
TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")  # your Koyeb URL

# Flask app setup
app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# Handle start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me an Instagram post URL and I'll fetch the media.")

# Handle Instagram URL and download media
async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram post URL.")
        return

    await update.message.reply_text("Downloading media...")

    # Using yt-dlp to download the Instagram media
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_url = info_dict.get("url", None)
            await update.message.reply_video(video_url)  # Send video back

    except Exception as e:
        logger.error(f"Error downloading Instagram media: {e}")
        await update.message.reply_text("Sorry, something went wrong while downloading the media.")

# Flask route for webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    logger.debug(f"Received update: {update_data}")  # Log for debugging

    # Process the update
    update = Update.de_json(update_data, bot_app.bot)
    bot_app.update_queue.put(update)

    return "ok"

# Health check route for Koyeb
@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!"

# Start the Flask app and webhook
async def set_webhook():
    bot = bot_app.bot
    await bot.set_webhook(f"{APP_URL}/webhook")

async def main():
    await set_webhook()
    app.run(port=8000, host="0.0.0.0")

# Run the app
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
