from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
from io import BytesIO
from rembg import remove

BOT_TOKEN = '7529913637:AAFr-E6m5HRQLwhCRGUZBhT9pUfzcwRnG4Q'  # Replace with your token

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a photo and I'll remove its background for you using AI (U²-Net, free & unlimited)!"
    )

async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    # Open and process image
    input_image = Image.open(BytesIO(photo_bytes)).convert("RGBA")
    output_bytes = remove(photo_bytes)
    output_image = Image.open(BytesIO(output_bytes))

    # Send result
    output_buffer = BytesIO()
    output_image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    await update.message.reply_photo(photo=output_buffer, caption="✅ Background removed! Powered by U²-Net (rembg).")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))
    print("Bot is running...")
    app.run_polling()
  
