from datetime import datetime
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from .decorators import superuser_only

bot: Bot = None
DOWNLOAD_DIR: Path = None


def register_handlers(dispatcher: Dispatcher, bot_instance: Bot, download_dir: Path):
    global bot, DOWNLOAD_DIR
    bot = bot_instance
    DOWNLOAD_DIR = download_dir
    
    dispatcher.message.register(download_file_handler, F.document | F.photo | F.video)


@superuser_only
async def download_file_handler(message: Message):
    try:
        if message.document:
            file_id = message.document.file_id
            filename = message.document.file_name
        elif message.photo:
            file_id = message.photo[-1].file_id
            filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        elif message.video:
            file_id = message.video.file_id
            filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        else:
            await message.answer("❌")
            return

        file = await bot.get_file(file_id)
        save_path = DOWNLOAD_DIR / filename
        
        await bot.download_file(file.file_path, destination=save_path)
        await message.answer("✅")
    except Exception as e:
        await message.answer("❌")
        print(e)
