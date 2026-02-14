#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
import pyautogui
from handlers import register_all_handlers

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPERUSER = os.getenv('SUPERUSER')

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not SUPERUSER:
    raise RuntimeError("SUPERUSER is not set")

SUPERUSER = int(SUPERUSER)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

pyautogui.FAILSAFE = False

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

register_all_handlers(dp, bot, SUPERUSER, DOWNLOAD_DIR)


async def on_startup():
    try:
        await bot.send_message(chat_id=SUPERUSER, text="🟢 Bot is polling")
    except Exception as e:
        print(f"Startup notify error: {e}")


async def main():
    await on_startup()
    print('Polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)