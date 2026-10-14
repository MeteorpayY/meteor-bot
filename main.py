import os
import json
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FLASK WEB SERVER (Render par 24/7 online rakhne ke liye) ---
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is active on Cloud 24/7!"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- CONFIGURATION SYSTEM ---
CONFIG_FILE = "config.json"
ADMIN_ID = 6804321185

default_config = {
    "welcome_message": (
        "🌹 WELCOME TO THE METEOR PAY FAMILY! 🎉\n\n"
        "Hello Dear 👋 \n\n"
        "👤 Welcome, Dear:  {username}\n\n"
        "🎉 Congratulations and welcome to the METEOR PAY Family! 🚀\n\n"
        "💎🎁 REFERRAL REWARD PROGRAM 🎁\n\n"
        "Invite genuine new users to METEOR PAY and earn exciting rewards by helping them complete their tasks! 💰\n\n"
        "🔥 Reward Structure:\n\n"
        "👉 Complete 15 valid tasks within 5 days → ₹80 Group Reward 🎁\n\n"
        "👉 Complete 40 valid tasks within 3 days → ₹200 Group Reward 🎁\n\n"
        "💰 Special Bonus Offer\n\n"
        "If your referred user completes 40 valid tasks within 3 days:\n\n"
        "✅ ₹200 Group Reward ✅ ₹200 Application Reward\n\n"
        "🎉 Total Reward: ₹400\n\n"
        "💖 Once again, welcome to the METEOR PAY Family!\n\n"
        "💎 METEOR PAY — GROW TOGETHER! 💎"
    ),
    "button1_text": "Helpline 1 🛠",
    "button1_url": "https://t.me/ishita_Meteropay",
    "button2_text": "Helpline 2 🛠",
    "button2_url": "https://t.me/Akshatkke"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# --- NEW MEMBER WELCOME HANDLER (Group ke liye) ---
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    chat_title = update.effective_chat.title or "our group"

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue
        
        first_name = member.first_name
        mention_html = f'<a href="tg://user?id={member.id}">{first_name}</a>'
        
        msg_text = config["welcome_message"]
        msg_text = msg_text.replace("{username}", mention_html)
        msg_text = msg_text.replace("{name}", first_name)
        msg_text = msg_text.replace("{chat_title}", chat_title)

        keyboard = [
            [
                InlineKeyboardButton(config["button1_text"], url=config["button1_url"]),
                InlineKeyboardButton(config["button2_text"], url=config["button2_url"])
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=msg_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# --- START COMMAND (Private DM ke liye) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    config = load_config()
    user = update.effective_user
    mention_html = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
    
    msg_text = config["welcome_message"]
    msg_text = msg_text.replace("{username}", mention_html)
    msg_text = msg_text.replace("{name}", user.first_name)
    
    keyboard = [
        [
            InlineKeyboardButton(config["button1_text"], url=config["button1_url"]),
            InlineKeyboardButton(config["button2_text"], url=config["button2_url"])
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=msg_text, reply_markup=reply_markup, parse_mode="HTML")

# --- MANAGE COMMANDS (Only Admin) ---
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    new_text = update.message.text.split(maxsplit=1)
    if len(new_text) < 2:
        await update.message.reply_text("Usage:\n`/setwelcome <Aapka Naya Message>`", parse_mode="Markdown")
        return
    
    config = load_config()
    config["welcome_message"] = new_text[1]
    save_config(config)
    await update.message.reply_text("✅ Welcome Message successfully update ho gaya hai!")

async def set_btn1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        args = context.args
        text, url = args[0], args[1]
        config = load_config()
        config["button1_text"] = text
        config["button1_url"] = url
        save_config(config)
        await update.message.reply_text(f"✅ Button 1 Update:\nName: {text}\nURL: {url}")
    except Exception:
        await update.message.reply_text("Usage:\n`/setbtn1 ButtonName https://link.com`", parse_mode="Markdown")

async def set_btn2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        args = context.args
        text, url = args[0], args[1]
        config = load_config()
        config["button2_text"] = text
        config["button2_url"] = url
        save_config(config)
        await update.message.reply_text(f"✅ Button 2 Update:\nName: {text}\nURL: {url}")
    except Exception:
        await update.message.reply_text("Usage:\n`/setbtn2 ButtonName https://link.com`", parse_mode="Markdown")

def main():
    TOKEN = "8021088491:AAFbotvfedYg4gEkj1hamp8EMypPLU0MvTw"
    
    keep_alive()
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("setbtn1", set_btn1))
    app.add_handler(CommandHandler("setbtn2", set_btn2))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    print("Meteor Pay Welcome Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
