#!/usr/bin/python3

# This bot does nothing much apart from returning user ID

import telebot
import os
import dotenv

dotenv.load_dotenv()

assert os.environ.get("telebot"), "Export Telegram bot token to environment"

bot = telebot.TeleBot(os.environ["telebot"])


@bot.message_handler(func=lambda msg: True)
def show_user_id(message):
    bot.send_message(
        message.chat.id,
        f"Your Telegram ID is **{message.from_user.id}**",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    print("Bot running - checking user ID")
    bot.infinity_polling()
