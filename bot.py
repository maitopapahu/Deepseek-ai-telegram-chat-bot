import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

logging.basicConfig(level=logging.INFO)

# Command handler
def start(update, context):
    update.message.reply_text("Send an Instagram URL to download media.")

def handle_message(update, context):
    url = update.message.text.strip()
    if "instagram.com" in url:
        update.message.reply_text(f"Simulating download for: {url}")
        # You can add actual download logic here
    else:
        update.message.reply_text("Please send a valid Instagram URL.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", start))
dispatcher.add_handler(CommandHandler("download", handle_message))  # optional
dispatcher.add_handler(
    telegram.ext.MessageHandler(telegram.ext.Filters.text & ~telegram.ext.Filters.command, handle_message)
)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def home():
    return "Bot is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
  
