import subprocess
import asyncio
import webbrowser
import threading
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from .decorators import superuser_only


def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(browser_handler, Command('browser'))
    dispatcher.message.register(wifi_handler, Command('wifi'))
    dispatcher.message.register(ping_handler, Command('ping'))


@superuser_only
async def browser_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /browser <url>")
        return
    
    url = args[0]
    
    try:
        def execute():
            webbrowser.open(url)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer(f"🌐 Opening: {url}")
    except Exception:
        await message.answer("❌")


@superuser_only
async def wifi_handler(message: Message):
    try:
        def execute():
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks'],
                capture_output=True,
                text=True,
                encoding='cp866',
                shell=True
            )
            return result.stdout
        
        output = await asyncio.get_event_loop().run_in_executor(None, execute)
        
        if not output:
            await message.answer("❌ Error getting WiFi data")
            return
        
        try:
            output = output.encode('cp866').decode('utf-8', errors='ignore')
        except:
            pass
        
        if len(output) > 4000:
            output = output[:4000] + "..."
        
        await message.answer(f"📡 WiFi Networks:\n\n```\n{output}\n```", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


@superuser_only
async def ping_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /ping <host>")
        return
    
    host = args[0]
    
    try:
        def execute():
            result = subprocess.run(
                f'chcp 65001 > nul && ping -n 4 {host}',
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=15,
                shell=True
            )
            return result.stdout
        
        await message.answer(f"🏓 Pinging {host}...")
        
        output = await asyncio.get_event_loop().run_in_executor(None, execute)
        
        if not output:
            await message.answer("❌ No output from ping")
            return
        
        if len(output) > 4000:
            output = output[:4000] + "..."
        
        await message.answer(f"🏓 Ping {host}:\n\n```\n{output}\n```", parse_mode=ParseMode.MARKDOWN)
    except subprocess.TimeoutExpired:
        await message.answer("❌ Ping timeout")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
