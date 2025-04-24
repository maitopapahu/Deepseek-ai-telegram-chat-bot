import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# --- Data Preprocessing and Model Training ---
# Load the historical color data (adjust based on your actual data source)
data = pd.read_csv("color_history.csv")

# Feature engineering (adjust according to your data)
features = ['Streak Length', 'Previous Color 1', 'Previous Color 2', 'Frequency of Red', 'Frequency of Green']
X = data[features]
y = data['Color']  # Target column (Color)

# Encoding the color (Red = 0, Green = 1, Violet = 2)
y = y.map({'Red': 0, 'Green': 1, 'Violet': 2})

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model
joblib.dump(model, 'color_prediction_model.pkl')

# --- Telegram Bot Code ---
# Load the trained model
model = joblib.load('color_prediction_model.pkl')

# Set up logging for the Telegram bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to predict color
def predict_color(features):
    prediction = model.predict([features])
    return 'Red' if prediction == 0 else 'Green' if prediction == 1 else 'Violet'

# Start command handler for the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the 91Club Color Prediction Bot! Type /predict to get a prediction.")

# Predict command handler
def predict(update: Update, context: CallbackContext):
    # Example feature values (replace with actual user input or historical data)
    features = [2, 1, 1, 10, 8]  # Streak length, Previous Color 1, Previous Color 2, Frequency of Red, Frequency of Green
    predicted_color = predict_color(features)
    
    # Send the prediction to the user
    update.message.reply_text(f"Predicted Next Color: {predicted_color}")

# Error handling for the bot
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to set up the bot
def main():
    # Insert your Bot's API Token here
    TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')  # Using environment variable for security
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers for start and predict
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("predict", predict))

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the bot and keep it running
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    
