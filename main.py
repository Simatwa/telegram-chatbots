#!/usr/bin/python3
import os
import logging
import telebot
from dotenv import load_dotenv
from Bard import Chatbot
from WebChatGPT import ChatGPT

load_dotenv(".env")

from_env = lambda key, default: os.environ.get(key, default)

logging_levels = {
    "10": 10,
    "20": 20,
    "30": 30,
    "40": 40,
    "50": 50,
}

logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    level=logging_levels.get(from_env("logging_level", 20)),
    datefmt="%d-%b-%Y %H:%M:%S",
)


logging.info("Initializing Bard Chatbot")
bard = Chatbot(
    from_env("bard", ""),
)

logging.info("Initializing ChatGPT Chatbot")

chatgpt = ChatGPT(
    from_env("openai_authorization", ""),
    from_env("openai_cookie_file", ""),
)

logging.info("Initializing Telegram bot")
bot = telebot.TeleBot(from_env("telebot", ""))

allowed_user_ids = from_env("users_id", "").split(",")

logging.info(f"Whitelisted users : {allowed_user_ids}")

format_exception = lambda e: e.args[1] if len(e.args) > 1 else str(e)


def is_verified(message):
    """Ensures it serves the right user"""
    for id in allowed_user_ids:
        if str(message.from_user.id) == id:
            return True


def anonymous_user(message):
    """Generate message for strange user"""
    response = f"""
	Hi **{message.from_user.first_name}**.
	You are not authorised to use this Bot.
	I recommmend setting up your own bot like this.
	Get the sourcecodes from [Github](https://github.com/Simatwa/telegram-chatbots).
	"""
    return response.strip()


def bard_gen_response(text):
    """Generate response with Bard
    Args:
        text (str): Prompt

    Returns:
        str: Response generated
    """
    try:
        return bard.ask(text).get("content")
    except Exception as e:
        return format_exception(e)


def chatgpt_gen_response(text):
    """Generate response with ChatGPT

    Args:
        text (str): Prompt

    Returns:
        str: Response generated
    """
    try:
        return chatgpt.chat(text)
    except Exception as e:
        return format_exception(e)


@bot.message_handler(commands=["start", "help"])
def display_help(message):
    sender = message.from_user.first_name
    help_message = (
        f"""
	Hi **{sender}**.
    This bot will allow you to directly chat with **Bard** and **ChatGPT**
    
    > Available commands
    
    /start or /help : Show this messsage
    /myId : Check your Telegram's ID
    /bard : Chat with Bard - **Google**
    /chatgpt : Chat with ChatGPT - **OpenAI**
    
    Have some fun!
   
   """.strip()
        if is_verified(message)
        else anonymous_user(message)
    )
    bot.reply_to(message, help_message, parse_mode="Markdown")


@bot.message_handler(commands=["myId"])
def user_id(message):
    """Respond with user id"""
    bot.reply_to(
        message,
        text=f"Your Telegram ID is **{message.from_user.id}**",
        parse_mode="Markdown",
    )


def handle_chatbot(default_text:str=''):
    """Handles chatbot exceptions & validates users safely

    Args:
        default_text (str, optional): Text to be returned incase of an exception.''.
    """
    def decorator(func):
        def main(message):
            try:
                if not is_verified(message):
                    # Not whitelisted user
                    return bot.reply_to(message, anonymous_user(message), parse_mode="Markdown")
                return func(message)
            
            except Exception as e:
                return bot.reply_to(message,default_text or format_exception(e))
            
        return main
    return decorator

@bot.message_handler(commands=["bard"])
@handle_chatbot()
def chat_with_bard(message):
    bot.reply_to(message, bard_gen_response(message.text), parse_mode="Markdown")


@bot.message_handler(commands=["chatgpt"])
def chat_with_chatgpt(message):
    bot.reply_to(message, chatgpt_gen_response(message.text), parse_mode="Markdown")


if __name__ == "__main__":
    logging.info("Bot is up and running!")
    bot.infinity_polling()