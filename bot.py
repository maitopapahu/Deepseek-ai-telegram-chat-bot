import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

PICSART_API_KEY = "eyJraWQiOiI5NzIxYmUzNi1iMjcwLTQ5ZDUtOTc1Ni05ZDU5N2M4NmIwNTEiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2UtNmVhMWEwNzMtNTFhNS00ZTg0LThiNjAtY2Q1N2JkMWZjZTAwIiwiYXVkIjoiNDcyMTYxODU4MDAyMTAxIiwibmJmIjoxNzQ1MzA4MTY2LCJzY29wZSI6WyJiMmItYXBpLmdlbl9haSIsImIyYi1hcGkuaW1hZ2VfYXBpIl0sImlzcyI6Imh0dHBzOi8vYXBpLnBpY3NhcnQuY29tL3Rva2VuLXNlcnZpY2UiLCJvd25lcklkIjoiNDcyMTYxODU4MDAyMTAxIiwiaWF0IjoxNzQ1MzA4MTY2LCJqdGkiOiJkMjA4OWZiZC1jYTNkLTRkMzQtODA0My1jZjM2NGY2YzVmMmEifQ.aJMJoVepVbldCrAarJFPZ7rNF3XxLzZfxLFMW3ZmYZjbmBBsODl1qHep64kUYD2wI4RyzZcWAXEIb51F1V1eafym4fEy_PWQCP2MXZ5FEXyEcJJpAUM4e5S1CEXMwvqoRvXfrI9O4C2jp65HbUWEJLwYU018XiUUxzIbNjZVsgDS9ob7aXpm8jwvg8IEDMkgytIzdCcOsaWoNMUX5spGH3FjOpKs12B2_ZAFEiGQJ4paq03psDvMIKpkiKClVKrF6zAC3vPZLQ0XF--Ixa7Dob4S43JUbops2RGxzci0Rs_FHco6Iaa0hnRlYKkY8Yhk4q-HQ2XY_x4BP_KHrJuWvg"
user_data = {}

# Step 1: Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me the brand name you want a logo for.")

# Step 2: Receive brand name
async def get_brand_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"brand": update.message.text}
    
    # Style options
    keyboard = [
        [InlineKeyboardButton("Minimal", callback_data="Minimal")],
        [InlineKeyboardButton("Modern", callback_data="Modern")],
        [InlineKeyboardButton("Luxury", callback_data="Luxury")],
        [InlineKeyboardButton("Retro", callback_data="Retro")],
        [InlineKeyboardButton("Futuristic", callback_data="Futuristic")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a style:", reply_markup=reply_markup)

# Step 3: Handle style selection and generate logo
async def handle_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("Please send the brand name first.")
        return

    brand = user_data[user_id]["brand"]
    style = query.data

    prompt = f"Logo design for a brand named '{brand}' in {style} style, high quality, clean background"

    # Send to Picsart API
    headers = {
        "x-api-key": PICSART_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.picsart.io/tools/text-to-image",
        headers=headers,
        json={"prompt": prompt, "n": 1, "size": "1024x1024"}
    )

    if response.status_code == 200:
        image_url = response.json()["data"][0]["url"]
        await query.message.reply_photo(photo=image_url, caption=f"Here’s your {style} logo for '{brand}'")
    else:
        await query.message.reply_text("Sorry, something went wrong with logo generation.")

# Initialize bot
app = ApplicationBuilder().token("7529913637:AAFr-E6m5HRQLwhCRGUZBhT9pUfzcwRnG4Q").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_brand_name))
app.add_handler(CallbackQueryHandler(handle_style))
app.run_polling()
