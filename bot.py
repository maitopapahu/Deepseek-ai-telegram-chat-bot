from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from rembg import remove
from io import BytesIO

# Your Telegram Bot token
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Function to handle the /start command
def start(update: Update, context):
    update.message.reply_text("Welcome! Send me an image, and I will remove the background.")

# Function to handle incoming images
def handle_image(update: Update, context):
    # Get the photo sent by the user
    photo = update.message.photo[-1]  # Get the highest resolution photo
    photo_file = photo.get_file()
    photo_bytes = photo_file.download_as_bytearray()
    
    # Use rembg to remove the background
    output = remove(photo_bytes)
    
    # Send back the processed image
    bio = BytesIO(output)
    bio.name = 'output.png'
    bio.seek(0)
    update.message.reply_photo(photo=bio)

def main():
    # Create the Updater and pass in your bot's token
    updater = Updater(TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add handlers for commands and messages
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    
    # Start the bot
    updater.start_polling()
    
    # Run the bot until you send a signal to stop (Ctrl+C)
    updater.idle()

if __name__ == '__main__':
    main()
    
