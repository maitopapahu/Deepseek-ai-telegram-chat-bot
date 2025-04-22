from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN"
WEBHOOK_URL = "https://your-koyeb-app-name.koyeb.app/"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I’m alive!")

bot_app.add_handler(CommandHandler("start", start))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

@app.route("/", methods=["GET"])
def set_webhook():
    bot_app.bot.set_webhook(WEBHOOK_URL)
    return "Webhook set"

# For Gunicorn
if __name__ == "__main__":
    app.run(debug=True)
