from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import requests

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEBHOOK_URL = "https://your-koyeb-app-name.koyeb.app/"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# START Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram URL to download the media.")

# Handle Instagram link
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com" in text:
        keyboard = [
            [InlineKeyboardButton("720p", callback_data=f"720p|{text}")],
            [InlineKeyboardButton("1080p", callback_data=f"1080p|{text}")],
            [InlineKeyboardButton("4K", callback_data=f"4k|{text}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose quality:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please send a valid Instagram post URL.")

# Handle button clicks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality, url = query.data.split("|")

    # Replace with your actual backend/API logic
    download_url = f"https://your-instagram-downloader-api.com/download?url={url}&quality={quality}"
    res = requests.get(download_url).json()
    media_link = res.get("media_url")

    if media_link:
        await query.message.reply_video(media_link) if 'video' in media_link else await query.message.reply_photo(media_link)
    else:
        await query.message.reply_text("Failed to fetch media.")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
bot_app.add_handler(CallbackQueryHandler(button_callback))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

@app.route("/", methods=["GET"])
def set_webhook():
    bot_app.bot.set_webhook(WEBHOOK_URL)
    return "Webhook set"

if __name__ == "__main__":
    app.run()
    
