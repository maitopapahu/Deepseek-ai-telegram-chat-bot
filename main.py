import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")  # set this in your Koyeb secrets
BOT_USERNAME = os.getenv("BOT_USERNAME")  # your bot username without @
APP_URL = os.getenv("APP_URL")  # your Koyeb app URL like https://your-app.koyeb.app

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# --- Instagram Downloader using free API (like picuki-style scraping) ---
def scrape_instagram_post(url: str):
    try:
        api_url = f"https://instasupersave.com/api/convert"
        response = requests.post(api_url, data={"url": url})
        data = response.json()

        media_links = [item["url"] for item in data.get("media", [])]
        return media_links
    except Exception as e:
        print("Error scraping:", e)
        return []

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram post/reel/video link to download.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    if "instagram.com" in msg:
        await update.message.reply_text("Processing your Instagram link...")
        links = scrape_instagram_post(msg)
        if links:
            for media in links:
                await update.message.reply_text(media)
        else:
            await update.message.reply_text("Failed to fetch media. Try a different link.")
    else:
        await update.message.reply_text("Please send a valid Instagram link.")

# --- Register Handlers ---
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask Webhook Route ---
@app.route(f"/{BOT_USERNAME}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running."

# --- Set Webhook on Startup ---
async def set_webhook():
    await bot_app.bot.set_webhook(f"{APP_URL}/{BOT_USERNAME}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    bot_app.run_polling()  # local testing fallback
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
