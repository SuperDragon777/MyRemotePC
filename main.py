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
class ColoredFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{self.BOLD}{record.levelname:8}{self.RESET}"
        record.name = f"\033[34m{record.name}{self.RESET}"
        return super().format(record)


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    file_handler = logging.FileHandler(
        log_dir / 'bot.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


load_dotenv()
logger = setup_logging()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPERUSER = os.getenv('SUPERUSER')

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment")
    raise RuntimeError("BOT_TOKEN is not set")

if not SUPERUSER:
    logger.critical("SUPERUSER is not set in environment")
    raise RuntimeError("SUPERUSER is not set")

try:
    SUPERUSER = int(SUPERUSER)
    logger.info(f"Superuser ID: {SUPERUSER}")
except ValueError:
    logger.critical(f"Invalid SUPERUSER value: {SUPERUSER}")
    raise RuntimeError("SUPERUSER must be a valid integer")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
logger.info(f"Download directory: {DOWNLOAD_DIR.absolute()}")

pyautogui.FAILSAFE = False
logger.debug("PyAutoGUI FAILSAFE disabled")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

register_all_handlers(dp, bot, SUPERUSER, DOWNLOAD_DIR)
logger.info("Handlers registered successfully")


async def on_startup():
    try:
        await bot.send_message(chat_id=SUPERUSER, text="🟢 Bot is polling")
        logger.info("Startup notification sent to superuser")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")


async def on_shutdown():
    try:
        await bot.send_message(chat_id=SUPERUSER, text="🔴 Bot stopped")
        logger.info("Shutdown notification sent to superuser")
    except Exception as e:
        logger.error(f"Failed to send shutdown notification: {e}")
    
    await bot.session.close()
    logger.info("Bot session closed")


async def main():
    logger.info("="*50)
    logger.info("Starting bot...")
    logger.info("="*50)
    
    await on_startup()
    
    try:
        logger.info("Bot is now polling for updates")
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)