# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from youtube import search_youtube

BOT_TOKEN = "7529913637:AAFr-E6m5HRQLwhCRGUZBhT9pUfzcwRnG4Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎶 Send /song <name> to search YouTube for music!")

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Usage: /song <song name>")
        return

    query = ' '.join(context.args)
    yt_link = search_youtube(query)

    if yt_link:
        buttons = [[InlineKeyboardButton("▶️ Watch on YouTube", url=yt_link)]]
        await update.message.reply_text(
            f"🔎 Top result for *{query}*:\n{yt_link}",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("🚫 No results found.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("song", song))
    app.run_polling()
    
