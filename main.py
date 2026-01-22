import os
import sys
import platform
import psutil
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import wraps
import pyautogui

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

@superuser_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    Доступные команды:
    /start
    /help
    /suicide
    /system
    /uptime
    /screenshot
    """
    await update.message.reply_text(help_text)


@superuser_only
async def suicide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bye 👋")
    context.application.stop_running = True
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
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        await update.message.reply_photo(
            photo=open(filename, 'rb'),
            caption="📸 Screenshot"
        )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


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

    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Bot started...')
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        sys.exit(0)