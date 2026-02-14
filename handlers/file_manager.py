import os
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from .decorators import superuser_only


def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(pwd_handler, Command('pwd'))
    dispatcher.message.register(ls_handler, Command('ls'))
    dispatcher.message.register(rm_handler, Command('rm'))
    dispatcher.message.register(cat_handler, Command('cat'))


@superuser_only
async def pwd_handler(message: Message):
    try:
        cwd = os.getcwd()
        await message.answer(f"📁 Current directory:\n{cwd}")
    except Exception:
        await message.answer("❌")


@superuser_only
async def ls_handler(message: Message):
    try:
        args = message.text.split()[1:] if message.text else []
        path = args[0] if args else os.getcwd()
        
        if not os.path.exists(path):
            await message.answer("❌")
            return

        files = os.listdir(path)
        if not files:
            await message.answer("📂 Empty folder")
            return

        files_list = "\n".join(files)
        await message.answer(f"📂 Contents of {path}:\n{files_list}")
    except Exception:
        await message.answer("❌")


@superuser_only
async def rm_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /rm <file>")
        return
    
    path = args[0]

    try:
        if not os.path.exists(path):
            await message.answer("❌")
            return

        if os.path.isdir(path):
            await message.answer("❌")
            return

        os.remove(path)
        await message.answer(f"✅ Deleted {path}")
    except Exception:
        await message.answer("❌")


@superuser_only
async def cat_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /cat <file>")
        return
    
    path = args[0]

    try:
        if not os.path.exists(path):
            await message.answer("❌")
            return

        if os.path.isdir(path):
            await message.answer("❌")
            return

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4000)
        await message.answer(f"📄 Content of {path}:\n{content}")
    except Exception:
        await message.answer("❌")
