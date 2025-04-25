import os
import telebot
import requests
import json
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

USER_DATA_FILE = 'users.json'
MAILTM_API = 'https://api.mail.tm'

# -------- Helper Functions --------
def load_users():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_domains():
    r = requests.get(f"{MAILTM_API}/domains")
    return [d["domain"] for d in r.json()["hydra:member"]]

def register_account(email, password):
    payload = {"address": email, "password": password}
    r = requests.post(f"{MAILTM_API}/accounts", json=payload)
    return r.status_code == 201

def get_token(email, password):
    payload = {"address": email, "password": password}
    r = requests.post(f"{MAILTM_API}/token", json=payload)
    if r.status_code == 200:
        return r.json()["token"]
    return None

# -------- Bot Commands --------
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, """
Welcome to Temp Mail Bot!

/new - Create a new temp email
/myemail - Show your current temp email
/inbox - List your inbox messages
/read <id> - Read a specific message
/delete - Delete your temp email
/help - Show this help again
    """)

@bot.message_handler(commands=['new'])
def new_email(message):
    domains = get_domains()
    markup = InlineKeyboardMarkup()
    for domain in domains:
        markup.add(InlineKeyboardButton(domain, callback_data=f"domain:{domain}"))
    bot.send_message(message.chat.id, "Choose a domain for your temp email:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("domain:"))
def handle_domain_select(call):
    domain = call.data.split(":")[1]
    users = load_users()
    user_id = str(call.from_user.id)

    username = random_string()
    email = f"{username}@{domain}"
    password = random_string(12)

    if register_account(email, password):
        token = get_token(email, password)
        if token:
            users[user_id] = {"email": email, "password": password, "token": token}
            save_users(users)
            bot.send_message(call.message.chat.id, f"Your temp email:\n`{email}`", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "Failed to get token.")
    else:
        bot.send_message(call.message.chat.id, "Failed to register email.")

@bot.message_handler(commands=['myemail'])
def my_email(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id in users:
        email = users[user_id]["email"]
        bot.send_message(message.chat.id, f"Your temp email:\n`{email}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "No temp email found. Use /new to create one.")

@bot.message_handler(commands=['inbox'])
def check_inbox(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id not in users:
        return bot.send_message(message.chat.id, "No temp email found. Use /new to create one.")

    token = users[user_id]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{MAILTM_API}/messages", headers=headers)
    messages = r.json().get("hydra:member", [])

    if not messages:
        return bot.send_message(message.chat.id, "Inbox is empty.")

    text = ""
    for msg in messages:
        text += f"ID: `{msg['id']}`\nFrom: {msg['from']['address']}\nSubject: *{msg['subject']}*\n\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['read'])
def read_email(message):
    args = message.text.split()
    if len(args) < 2:
        return bot.send_message(message.chat.id, "Usage: /read <message_id>")

    msg_id = args[1]
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id not in users:
        return bot.send_message(message.chat.id, "No temp email found. Use /new to create one.")

    token = users[user_id]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{MAILTM_API}/messages/{msg_id}", headers=headers)
    if r.status_code != 200:
        return bot.send_message(message.chat.id, "Failed to fetch message.")

    msg = r.json()
    text = f"*Subject:* {msg['subject']}\n*From:* {msg['from']['address']}\n\n{msg['text'] or '[No text content]'}"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['delete'])
def delete_email(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if user_id in users:
        del users[user_id]
        save_users(users)
        bot.send_message(message.chat.id, "Your temp email has been deleted.")
    else:
        bot.send_message(message.chat.id, "You don't have a temp email to delete.")

# -------- Start Bot --------
bot.polling()
      
