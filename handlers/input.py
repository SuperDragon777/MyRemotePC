import time
import threading
import pyautogui
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from .decorators import superuser_only
import keyboard

def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(type_text_handler, Command('type'))
    dispatcher.message.register(mouse_move_handler, Command('mouse'))
    dispatcher.message.register(mouse_click_handler, Command('click'))
    dispatcher.message.register(mouse_double_click_handler, Command('dclick'))
    dispatcher.message.register(mouse_scroll_handler, Command('scroll'))
    dispatcher.message.register(mouse_pos_handler, Command('mpos'))


@superuser_only
async def type_text_handler(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Usage: /type <text>")
        return
    
    text = ' '.join(message.text.split()[1:])
    
    try:
        def execute():
            keyboard.write(text, delay=0.05)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("⌨️ Typing...")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


@superuser_only
async def mouse_move_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if len(args) < 2:
        await message.answer("Usage: /mouse <x> <y>")
        return
    
    try:
        x = int(args[0])
        y = int(args[1])
        
        def execute():
            pyautogui.moveTo(x, y, duration=0.2)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer(f"🖱️ Moved to ({x}, {y})")
    except ValueError:
        await message.answer("❌ Invalid coordinates")
    except Exception:
        await message.answer("❌")


@superuser_only
async def mouse_click_handler(message: Message):
    try:
        args = message.text.split()[1:] if message.text else []
        button = args[0] if args else 'left'
        
        if button not in ['left', 'right', 'middle']:
            await message.answer("❌ Button must be: left, right, middle")
            return
        
        def execute():
            pyautogui.click(button=button)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer(f"🖱️ Clicked {button} button")
    except Exception:
        await message.answer("❌")


@superuser_only
async def mouse_double_click_handler(message: Message):
    try:
        def execute():
            pyautogui.doubleClick()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🖱️ Double clicked")
    except Exception:
        await message.answer("❌")


@superuser_only
async def mouse_scroll_handler(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /scroll <amount>")
        return
    
    try:
        amount = int(args[0])
        
        def execute():
            pyautogui.scroll(amount)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        direction = "up" if amount > 0 else "down"
        await message.answer(f"🖱️ Scrolled {direction}")
    except ValueError:
        await message.answer("❌ Invalid amount")
    except Exception:
        await message.answer("❌")


@superuser_only
async def mouse_pos_handler(message: Message):
    try:
        x, y = pyautogui.position()
        await message.answer(f"🖱️ Mouse position: ({x}, {y})")
    except Exception:
        await message.answer("❌")
