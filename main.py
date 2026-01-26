import os
import sys
import platform
import psutil
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import wraps
from PIL import ImageGrab
import ctypes
import threading
import subprocess
import pyautogui
import time

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPERUSER = os.getenv('SUPERUSER')

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

if not SUPERUSER:
    raise RuntimeError("SUPERUSER is not set")

SUPERUSER = int(SUPERUSER)

def superuser_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user

        if not user or user.id != SUPERUSER:
            if update.message:
                await update.message.reply_text("⛔ nah bro, you can't do that")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper

@superuser_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('blank')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Available commands:
    /start
    /help
    /suicide
    /system
    /uptime
    /screenshot
    /superuser
    /msg <text>
    /winl
    /shutdown
    /hibernate
    /type <text>
    """
    await update.message.reply_text(help_text)


@superuser_only
async def suicide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bye 👋")
    await context.application.shutdown()
    await context.application.stop()

@superuser_only
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{platform.system()} {platform.release()}")

@superuser_only
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime_sec = int(datetime.now().timestamp() - psutil.boot_time())
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    seconds = uptime_sec % 60
    
    await update.message.reply_text(f"{days}d {hours}h {minutes}m {seconds}s")

@superuser_only
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot = ImageGrab.grab() # сделали скрин
        screenshot.save(filename) # сохранили его
        
        await update.message.reply_photo(photo=open(filename, 'rb'), caption="") # отправили
        os.remove(filename) # удалили локально
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def superuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == SUPERUSER:
        await update.message.reply_text("✅ True")
    else:
        await update.message.reply_text("❌ False")

@superuser_only
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("‼️")
        return
    
    text = ' '.join(context.args)
    
    try:
        def show_messagebox():
            ctypes.windll.user32.MessageBoxW(0, text, "MyRemotePC", 0)
        
        thread = threading.Thread(target=show_messagebox, daemon=True)
        thread.start()
        
        await update.message.reply_text("✅")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def winl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def execute():
            subprocess.run('rundll32.exe user32.dll,LockWorkStation')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("🚪 Locking...")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def execute():
            subprocess.run('shutdown /s /t 0 /f', shell=True, check=True)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("🔴 Shutting down...")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def hibernate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def execute():
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("💤 Hibernating...")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /type <text>")
        return
    
    text = ' '.join(context.args)
    
    try:
        def execute():
            time.sleep(0.5)
            pyautogui.typewrite(text, interval=0.05)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("⌨️ Typing...")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'idk what to do')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('suicide', suicide))
    app.add_handler(CommandHandler('system', system))
    app.add_handler(CommandHandler('uptime', uptime))
    app.add_handler(CommandHandler('screenshot', screenshot))
    app.add_handler(CommandHandler('superuser', superuser))
    app.add_handler(CommandHandler('msg', msg))
    app.add_handler(CommandHandler('winl', winl))
    app.add_handler(CommandHandler('shutdown', shutdown))
    app.add_handler(CommandHandler('hibernate', hibernate))
    app.add_handler(CommandHandler('type', type))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Polling...')
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        sys.exit(0)