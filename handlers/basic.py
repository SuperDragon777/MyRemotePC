import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from .decorators import superuser_only

bot: Bot = None
dp: Dispatcher = None


def register_handlers(dispatcher: Dispatcher, bot_instance: Bot):
    global bot, dp
    bot = bot_instance
    dp = dispatcher
    
    dispatcher.message.register(start, CommandStart())
    dispatcher.message.register(help_command, Command('help'))
    dispatcher.message.register(suicide, Command('suicide'))
    dispatcher.message.register(superuser, Command('superuser'))
    dispatcher.message.register(github, Command('github'))


@superuser_only
async def start(message: Message):
    await message.answer('blank')


@superuser_only
async def help_command(message: Message):
    help_text = (
        "📥 *File Handling*\n"
        "If you send a file (photo, video, document), it will be downloaded to the PC in the `downloads` folder.\n\n"

        "⚡ *System Commands*\n"
        "/system — Show OS info\n"
        "/uptime — Show system uptime\n"
        "/cpu — CPU load\n"
        "/ram — RAM usage\n"
        "/disk — Disk usage\n"
        "/battery — Battery status\n"
        "/ip — Local & External IP\n\n"

        "🖥️ *PC Control*\n"
        "/screenshot — Take screenshot\n"
        "/winl — Lock workstation\n"
        "/shutdown — Shutdown PC\n"
        "/hibernate — Hibernate PC\n"
        "/f4 — Press Alt+F4\n"
        "/volume [0-100] — Get/set volume\n"
        "/say <text> — Text to speech\n"
        "/cmd <command> — Run command (use carefully)\n"
        "/tm — Show active processes\n"
        "/kill <pid> - Kill process by PID\n\n"

        "⌨️ *Keyboard & Mouse*\n"
        "/type <text> — Type text via keyboard\n"
        "/mouse <x> <y> — Move mouse to coordinates\n"
        "/mpos — Get current mouse position\n"
        "/click [left/right/middle] — Click mouse button (default: left)\n"
        "/dclick — Double-click mouse\n"
        "/scroll <amount> — Scroll (positive = up, negative = down)\n\n"

        "💬 *Messages*\n"
        "/msg <text> — Show message box\n\n"

        "📂 *File Manager*\n"
        "/pwd — Current directory\n"
        "/ls [path] — List files\n"
        "/cat <file> — Read text file\n"
        "/rm <file> — Delete file\n\n"

        "🛠️ *Bot Info*\n"
        "/start — Start bot\n"
        "/help — This help menu\n"
        "/superuser — Check superuser\n"
        "/suicide — Stop bot\n"
        "/github — GitHub link\n\n"
        
        "🌐 *Internet*\n"
        "/browser <url> — Open URL in browser\n"
        "/ping <host> — Ping host\n"
        "/wifi — Show WiFi networks\n\n"
    )

    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@superuser_only
async def suicide(message: Message):
    await message.answer("Bye 👋")
    await bot.session.close()
    sys.exit(0)


async def superuser(message: Message):
    from .decorators import SUPERUSER
    if message.from_user.id == SUPERUSER:
        await message.answer("✅ True")
    else:
        await message.answer("❌ False")


async def github(message: Message):
    await message.answer("https://github.com/SuperDragon777/MyRemotePC")
