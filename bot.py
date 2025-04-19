import os
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO

# Initialize OpenCV super-resolution model
def init_sr_model():
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    path = "FSRCNN_x2.pb"  # Fast Super-Resolution CNN model
    sr.readModel(path)
    sr.setModel("fsrcnn", 2)  # 2x scaling
    return sr

sr_model = init_sr_model()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖼️ Image Enhancer Bot\n"
        "Send me an image for 2x enhancement!"
    )

async def enhance_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get image from message
        photo_file = await update.message.photo[-1].get_file()
        image_stream = BytesIO()
        await photo_file.download_to_memory(out=image_stream)
        image_stream.seek(0)
        
        # Convert to OpenCV format
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Enhance image
        enhanced = sr_model.upsample(img)

        # Convert back to Telegram format
        _, img_byte_arr = cv2.imencode('.jpg', enhanced)
        output_stream = BytesIO(img_byte_arr.tobytes())

        # Send enhanced image
        await update.message.reply_photo(
            photo=output_stream,
            caption="Enhanced 2x using FSRCNN"
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, enhance_image))
    app.run_polling()