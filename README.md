<h1 align="center"> telegram-chatbots </h1>

<p align="center">
<a href="https://https://github.com/Simatwa/telegram-chatbots/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg"/></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/static/v1?logo=Black&label=Code-style&message=Black"/></a>
<a href="https://wakatime.com/badge/github/Simatwa/telegram-chatbots"><img src="https://wakatime.com/badge/github/Simatwa/telegram-chatbots.svg" alt="wakatime"></a>
</p>

<p align="center">
<img src="https://github.com/Simatwa/telegram-chatbots/blob/main/assets/demo.png?raw=true" width="60%" height="auto" alt="Bot Demo"> 
</p>

Unofficial Telegram bot for ChatGPT and Bard 

## Pre-requisites 

1. [Python](https://python.org)>=3.10 Installed
2. [Telegram Bot token](https://core.telegram.org/bots#botfather)

## Installation

Clone and install dependencies

```
git clone https://github.com/Simatwa/telegram-bots
cd telegram-bots
pip install -r requirements.txt
```

## Usage

It is presumed that you're in possession of [Telegram Bot Token](https://telegram/), if that's not the case then have one from [@BotFather](https://core.telegram.org/bots#botfather).

Since this script depends on [GoogleBard](https://github.com/acheong08/Bard) and [WebChatGPT](https://github.com/Simatwa/WebChatGPT) libraries, purpose to walkthrough their documentations then use that knowledge to find the required information stated in the [env](env) file.

They include :

| Variable | Info |
| ---------- | ------- |
| [bard](https://github.com/acheong08/Bard)  | Google's bard session key |
| [openai_cookie_file](https://github.com/Simatwa/WebChatGPT) | Path to openai-cookie-file.json | 
| [openai_authorization](https://github.com/Simatwa/WebChatGPT) | Openai Authorization token | 

After filling the [env](env) file, rename it to `.env` and then vallah you're good to go.

Simply run `python main.py` and have some fun.

## Disclaimer

The code in this repository is an unofficial implementation and integration of OpenAI's ChatGPT and Bard models. It is not endorsed or supported by either partys. In addition, this code might not reflect the latest practices or updates from them. It is provided as-is, and there are no guarantees regarding its performance, reliability, or security. Use it at **Your Own Risk**. The developer of this repository disclaim any liability for the usage or consequences of utilizing these scripts.