import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

openai.api_key = "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"
user_data = {}  # store temporary user info

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me the name for your logo.")

# Get logo name from user
async def get_logo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"text": update.message.text}
    
    # Show style options
    keyboard = [
        [InlineKeyboardButton("Minimal", callback_data="Minimal")],
        [InlineKeyboardButton("Modern", callback_data="Modern")],
        [InlineKeyboardButton("Luxury", callback_data="Luxury")],
        [InlineKeyboardButton("Retro", callback_data="Retro")],
        [InlineKeyboardButton("Futuristic", callback_data="Futuristic")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a style for your logo:", reply_markup=reply_markup)

# Handle style button
async def handle_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("Please send the brand name first.")
        return

    logo_text = user_data[user_id]["text"]
    style = query.data
    prompt = f"Logo for a brand called '{logo_text}', {style} style, clean design, white background"
    
    # Generate image with DALL·E
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024"
    )
    image_url = response.data[0].url
    await query.message.reply_photo(photo=image_url, caption=f"Here’s your {style} style logo!")

# Setup bot
app = ApplicationBuilder().token("7529913637:AAFr-E6m5HRQLwhCRGUZBhT9pUfzcwRnG4Q").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_logo_text))
app.add_handler(CallbackQueryHandler(handle_style))
app.run_polling()
