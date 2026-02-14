import ctypes
import threading
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from .decorators import superuser_only


def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(msg_handler, Command('msg'))


@superuser_only
async def msg_handler(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await message.answer("‼️")
        return
    
    text = ' '.join(message.text.split()[1:])
    
    try:
        def show_messagebox():
            ctypes.windll.user32.MessageBoxW(0, text, "MyRemotePC", 0)
        
        thread = threading.Thread(target=show_messagebox, daemon=True)
        thread.start()
        
        await message.answer("✅")
    except Exception:
        await message.answer("❌")
