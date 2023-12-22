#!/usr/bin/python3
import os
import logging
import telebot
import requests
import json
from telebot import types
from dotenv import load_dotenv
from Bard import Chatbot
from WebChatGPT import ChatGPT

__prog__ = "telegram-chatbots"
__version__ = "0.1.0"

format_exception = lambda e: e.args[1] if len(e.args) > 1 else str(e)

load_dotenv(".env")

from_env = lambda key, default: os.environ.get(key, default)

logging_levels = {
    "10": 10,
    "20": 20,
    "30": 30,
    "40": 40,
    "50": 50,
}

logging_params = {
    "format": "%(asctime)s - %(levelname)s : %(message)s",
    "level": logging_levels.get(from_env("logging_level", 20)),
    "datefmt": "%d-%b-%Y %H:%M:%S",
}

if from_env("log_path", False):
    logging_params["filename"] = from_env("log_path", "telegram-chatbots.log")

awesome_prompts_pdf = (
    "https://github.com/Simatwa/gpt-cli/blob/main/assets/all-acts.pdf?raw=true"
)
awesome_prompts_json = (
    "https://github.com/Simatwa/gpt-cli/blob/main/assets/all-acts.json?raw=true"
)

logging.basicConfig(**logging_params)
logging.info(f"{__prog__} - v{__version__}")
allowed_user_ids = from_env("users_id", "").split(",")

show_exceptions = from_env("show_exceptions", "true") == "true"

logging.info(f"I will show exceptions - {show_exceptions}")

ERR = None if show_exceptions else "Error occurred while generating response!"

logging.info(f"Whitelisted users : {allowed_user_ids}")

default_settings = {
    "chatbot": from_env("default_chatbot", "chatgpt"),
    "awesome_status": True,
}

conversations, awesome_prompts = {}, {}

logging.info("Initializing Bard Chatbot")
bard = Chatbot(
    from_env("bard", ""),
)

logging.info("Initializing ChatGPT Chatbot")

chatgpt = ChatGPT(
    from_env("openai_cookie_file", ""),
)

logging.info("Initializing Telegram bot")
bot = telebot.TeleBot(from_env("telebot", ""), parse_mode="Markdown")

bot.remove_webhook()  # Remove any webhook if available

if from_env("awesome_prompts", "true") == "true":
    logging.info("Loading awesome-prompts")
    awesome_prompts = requests.get(awesome_prompts_json).json()
    new_make = {}
    for count, key_value in enumerate(awesome_prompts.items()):
        # Links also index to a prompt
        new_make[str(count)] = key_value[1]
    awesome_prompts.update(new_make)
    del new_make


for user in allowed_user_ids:
    assert user.isdigit(), "User id can contain digits only"
    conversations[int(user)] = default_settings


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


def verified_only():
    """Terminates if user is anonymous"""

    def decorator(func):
        def main(message):
            if not is_verified(message):
                # Not a whitelisted user
                logging.info(
                    f"ANONYMOUS SERVING : {message.from_user.id} ({message.from_user.first_name}) - {message.text}"
                )
                return bot.reply_to(
                    message,
                    anonymous_user(message),
                )
            return func(message)

        return main

    return decorator


@bot.message_handler(commands=["start", "help"])
@verified_only()
def display_help(message):
    sender = message.from_user.first_name
    help_message = f"""
	Hi **{sender}**.
    This bot will allow you to directly chat with **Bard** and **ChatGPT**
    
    > Available commands
    
    /start or /help : Show this messsage
    /myid : Check your Telegram's ID
    /bard : Chat with Bard - **Google**
    /chatgpt : Chat with ChatGPT - **OpenAI**
    /awesome : Control awesome parsing state
    /check <key> : Check awesome prompt value by key

    To parse awesome-prompts use the format %(key)s in your text.
    Where <key> is the awesome-prompt title or index.
    
    Default LLM is the one you recently used. ({conversations[message.from_user.id]['chatbot']})
    
    Have some fun!
   
   """.strip()
    logging.info(
        f"HELP SERVING : {message.from_user.id} ({message.from_user.first_name}) - {message.text}"
    )
    bot.reply_to(
        message,
        help_message,
    )


@bot.message_handler(commands=["myid"])
def user_id(message):
    """Respond with user id"""
    logging.info(
        f"USER-ID SERVING : {message.from_user.id} ({message.from_user.first_name}) - {message.text} "
    )
    bot.reply_to(
        message,
        text=f"Your Telegram ID is **{message.from_user.id}**",
    )


@bot.message_handler(commands=["awesome"])
@verified_only()
def config_awesome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(
        "Activate-Awesome", callback_data=f"{message.from_user.id}:on"
    )
    item2 = types.InlineKeyboardButton(
        "Deactivate-Awesome", callback_data=f"{message.from_user.id}:off"
    )
    item3 = types.InlineKeyboardButton(
        "Retain-current", callback_data=f"{message.from_user.id}:retain"
    )

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def awesome_callback_query(call):
    user_id, call_data = call.data.split(":")
    if call_data == "on":
        conversations[int(user_id)]["awesome_status"] = True
        bot.send_message(
            int(user_id),
            f"Awesome ON \n View latest awesome-prompts from [here]({awesome_prompts_pdf}.)",
            parse_mode="Markdown",
        )
    elif call_data == "off":
        conversations[int(user_id)]["awesome_status"] = False
        bot.send_message(call.message.chat.id, "Awesome OFF")
    else:
        status = conversations[int(user_id)]["awesome_status"]
        bot.send_message(call.message.chat.id, f"Awesome {'ON' if status else 'OFF'}")


@bot.message_handler(commands=["check"])
@verified_only()
def awesome_check(message):
    """Checks for a particular prompt"""
    key = " ".join(message.text.split(" ")[1:])
    bot.send_message(
        message.chat.id,
        awesome_prompts.get(key)
        or f"No awesome prompt associated with the key '{key}'.",
        parse_mode="Markdown",
    )


def handle_chatbot(llm_name: str = "", default_text: str = ERR):
    """Handles chatbot exceptions & validates user safely

    Args:
        llm_name (str, optional): LLM name for generating response
        default_text (str, optional): Text to be returned incase of an exception.''.
    """

    def decorator(func):
        def main(message):
            try:
                if llm_name:
                    conversations[message.from_user.id]["chatbot"] = llm_name
                logging.info(
                    f"[{llm_name.upper()}] Serving : {message.from_user.id} ({message.from_user.first_name}) - {message.text}"
                )
                if conversations[message.from_user.id]["awesome_status"]:
                    try:
                        message.text = message.text % (awesome_prompts)
                    except KeyError as e:
                        bot.reply_to(
                            message,
                            f"Failed to parse awesome-prompt - {format_exception(e)}",
                        )
                        return
                return func(message)

            except Exception as e:
                logging.error(format_exception(e))
                return bot.reply_to(
                    message,
                    f"*{default_text or format_exception(e)}*",
                )

        return main

    return decorator


@bot.message_handler(
    commands=["bard"],
)
@verified_only()
@handle_chatbot("bard")
def chat_with_bard(message):
    bot.reply_to(
        message,
        bard.ask(message.text).get("content"),
    )


@bot.message_handler(commands=["chatgpt"])
@verified_only()
@handle_chatbot("chatgpt")
def chat_with_chatgpt(message):
    bot.reply_to(
        message,
        chatgpt.chat(message.text),
    )


@bot.message_handler(func=lambda msg: True, content_types=["text"])
@verified_only()
@handle_chatbot("Auto")
def auto_detect_chatbot(message):
    if conversations[message.from_user.id]["chatbot"] == "bard":
        bot.reply_to(
            message,
            bard.ask(message.text).get("content"),
        )
    else:
        bot.reply_to(
            message,
            chatgpt.chat(message.text),
        )


if __name__ == "__main__":
    logging.info("Bot is up and running!")
    bot.infinity_polling()
