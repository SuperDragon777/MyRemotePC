#!/usr/bin/env python3

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
import socket
import requests
from pathlib import Path
import volume
import comtypes
import asyncio
import concurrent.futures
import pyttsx3
import webbrowser

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

pyautogui.FAILSAFE = False # without this, moving mouse to corner won't raise exception

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

async def on_startup(app: Application):
    try:
        await app.bot.send_message(
            chat_id = SUPERUSER,
            text="🟢 Bot is polling"
        )
    except Exception as e:
        print(f"Startup notify error: {e}")

@superuser_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('blank')

@superuser_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "/cmd <command> — Run command (use carefully)\n\n"

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

    await update.message.reply_text(help_text, parse_mode="Markdown")



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

async def github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("https://github.com/SuperDragon777/MyRemotePC")

@superuser_only
async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        external_ip = requests.get(
            'https://api.ipify.org',
            timeout=5
        ).text

        await update.message.reply_text(
            f"🏠 Local: {local_ip}\n"
            f"🌍 External: {external_ip}"
        )

    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def f4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def execute():
            pyautogui.hotkey('alt', 'f4')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("⏳ Executing...")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        usage = psutil.cpu_percent(interval=1)
        await update.message.reply_text(f"🧠 CPU load: {usage}%")
    except Exception:
        await update.message.reply_text("❌")

@superuser_only
async def ram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mem = psutil.virtual_memory()

        total = mem.total // (1024 ** 2)
        used = mem.used // (1024 ** 2)
        free = mem.available // (1024 ** 2)
        percent = mem.percent

        await update.message.reply_text(
            f"📦 Total: {total} MB\n"
            f"📊 Used: {used} MB\n"
            f"🟢 Free: {free} MB\n"
            f"📈 Load: {percent}%"
        )
    except Exception:
        await update.message.reply_text("❌")

@superuser_only
async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        usage = psutil.disk_usage('/')

        total = usage.total // (1024 ** 3)
        used = usage.used // (1024 ** 3)
        free = usage.free // (1024 ** 3)
        percent = usage.percent

        await update.message.reply_text(
            f"📦 Total: {total} GB\n"
            f"📊 Used: {used} GB\n"
            f"🟢 Free: {free} GB\n"
            f"📈 Load: {percent}%"
        )
    except Exception:
        await update.message.reply_text("❌")

@superuser_only
async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bat = psutil.sensors_battery()

        if bat is None:
            await update.message.reply_text("🔌 Battery not found")
            return

        percent = bat.percent
        plugged = bat.power_plugged

        status = "🔌 Charging" if plugged else "🔋 On battery"

        await update.message.reply_text(
            f"⚡ Charge: {percent}%\n"
            f"{status}"
        )

    except Exception:
        await update.message.reply_text("❌")

@superuser_only
async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.document:
        tg_file = message.document
        filename = tg_file.file_name

    elif message.photo:
        tg_file = message.photo[-1]
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    elif message.video:
        tg_file = message.video
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    else:
        await update.message.reply_text("❌")
        return

    try:
        file = await tg_file.get_file()
        save_path = DOWNLOAD_DIR / filename

        await file.download_to_drive(custom_path=str(save_path))

        await update.message.reply_text("✅")

    except Exception as e:
        await update.message.reply_text("❌")
        print(e)

@superuser_only
async def pwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cwd = os.getcwd()
        await update.message.reply_text(f"📁 Current directory:\n{cwd}")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        path = context.args[0] if context.args else os.getcwd()
        if not os.path.exists(path):
            await update.message.reply_text("❌")
            return

        files = os.listdir(path)
        if not files:
            await update.message.reply_text("📂 Empty folder")
            return

        files_list = "\n".join(files)
        await update.message.reply_text(f"📂 Contents of {path}:\n{files_list}")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def rm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /rm <file>")
        return
    path = context.args[0]

    try:
        if not os.path.exists(path):
            await update.message.reply_text("❌")
            return

        if os.path.isdir(path):
            await update.message.reply_text("❌")
            return

        os.remove(path)
        await update.message.reply_text(f"✅ Deleted {path}")

    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /cat <file>")
        return
    path = context.args[0]

    try:
        if not os.path.exists(path):
            await update.message.reply_text("❌")
            return

        if os.path.isdir(path):
            await update.message.reply_text("❌")
            return

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4000)
        await update.message.reply_text(f"📄 Content of {path}:\n{content}")

    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def volume_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            def get_vol():
                comtypes.CoInitialize()
                try:
                    current = volume.current_volume()
                    return current
                finally:
                    comtypes.CoUninitialize()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                current = await context.application.bot_data.get('loop', asyncio.get_event_loop()).run_in_executor(
                    executor, get_vol
                )
            await update.message.reply_text(f"🔊 Current volume: {current}%")
            return
        
        percent = int(context.args[0])
        
        if percent < 0 or percent > 100:
            await update.message.reply_text("❌ Volume must be 0-100")
            return
        
        def execute():
            comtypes.CoInitialize()
            try:
                old_volume = volume.current_volume()
                volume.volume(percent)
            finally:
                comtypes.CoUninitialize()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text(f"🔊 Volume changed to {percent}%")
        
    except ValueError:
        await update.message.reply_text("❌")
    except Exception as e:
        await update.message.reply_text(f"❌")

@superuser_only
async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /say <text>")
        return
    
    text = ' '.join(context.args)
    
    def speak(text: str):
        try:
            comtypes.CoInitialize()
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            comtypes.CoUninitialize()
        except Exception as e:
            print("TTS error:", e)
    
    threading.Thread(
        target=speak,
        args=(text,),
        daemon=False
    ).start()
    
    await update.message.reply_text("🗣️ Speaking...")

@superuser_only
async def mouse_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /mouse <x> <y>")
        return
    
    try:
        x = int(context.args[0])
        y = int(context.args[1])
        
        def execute():
            pyautogui.moveTo(x, y, duration=0.2)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text(f"🖱️ Moved to ({x}, {y})")
    except ValueError:
        await update.message.reply_text("❌ Invalid coordinates")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def mouse_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        button = context.args[0] if context.args else 'left'
        
        if button not in ['left', 'right', 'middle']:
            await update.message.reply_text("❌ Button must be: left, right, middle")
            return
        
        def execute():
            pyautogui.click(button=button)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text(f"🖱️ Clicked {button} button")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def mouse_double_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        def execute():
            pyautogui.doubleClick()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text("🖱️ Double clicked")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def mouse_scroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /scroll <amount>")
        return
    
    try:
        amount = int(context.args[0])
        
        def execute():
            pyautogui.scroll(amount)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        direction = "up" if amount > 0 else "down"
        await update.message.reply_text(f"🖱️ Scrolled {direction}")
    except ValueError:
        await update.message.reply_text("❌ Invalid amount")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def mouse_pos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        x, y = pyautogui.position()
        await update.message.reply_text(f"🖱️ Mouse position: ({x}, {y})")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def browser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /browser <url>")
        return
    
    url = context.args[0]
    
    try:
        def execute():
            webbrowser.open(url)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await update.message.reply_text(f"🌐 Opening: {url}")
    except Exception as e:
        await update.message.reply_text("❌")

@superuser_only
async def wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        output = await asyncio.get_event_loop().run_in_executor(
            None, execute
        )
        
        if not output:
            await update.message.reply_text("❌ Error getting WiFi data")
            return
        
        try:
            output = output.encode('cp866').decode('utf-8', errors='ignore')
        except:
            pass
        
        if len(output) > 4000:
            output = output[:4000] + "..."
        
        await update.message.reply_text(f"📡 WiFi Networks:\n\n```\n{output}\n```", parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


@superuser_only
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ping <host>")
        return
    
    host = context.args[0]
    
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
        
        await update.message.reply_text(f"🏓 Pinging {host}...")
        
        output = await asyncio.get_event_loop().run_in_executor(
            None, execute
        )
        
        if not output:
            await update.message.reply_text("❌ No output from ping")
            return
        
        if len(output) > 4000:
            output = output[:4000] + "..."
        
        await update.message.reply_text(f"🏓 Ping {host}:\n\n```\n{output}\n```", parse_mode="Markdown")
        
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Ping timeout")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@superuser_only
async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /cmd <command>")
        return
    
    command = ' '.join(context.args)
    
    try:
        def execute():
            result = subprocess.run(
                command,
                capture_output=True,
                shell=True,
                timeout=30
            )
            try:
                stdout = result.stdout.decode('cp866')
            except:
                try:
                    stdout = result.stdout.decode('utf-8')
                except:
                    stdout = result.stdout.decode('cp1251', errors='ignore')
            
            try:
                stderr = result.stderr.decode('cp866')
            except:
                try:
                    stderr = result.stderr.decode('utf-8')
                except:
                    stderr = result.stderr.decode('cp1251', errors='ignore')
            
            return stdout, stderr, result.returncode
        
        await update.message.reply_text(f"⚙️ Executing: `{command}`", parse_mode="Markdown")
        
        stdout, stderr, returncode = await asyncio.get_event_loop().run_in_executor(
            None, execute
        )
        
        output = ""
        
        if stdout:
            output += f"📤 Output:\n```\n{stdout}\n```\n"
        
        if stderr:
            output += f"⚠️ Error:\n```\n{stderr}\n```\n"
        
        if not stdout and not stderr:
            output = "✅ Command executed (no output)"
        
        output += f"\n📊 Return code: {returncode}"
        
        if len(output) > 4000:
            output = output[:4000] + "\n\n... (truncated)"
        
        await update.message.reply_text(output, parse_mode="Markdown")
        
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Command timeout (30s)")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@superuser_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'idk what to do')

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )
    
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
    app.add_handler(CommandHandler('github', github))
    app.add_handler(CommandHandler('ip', ip))
    app.add_handler(CommandHandler('f4', f4))
    app.add_handler(CommandHandler('cpu', cpu))
    app.add_handler(CommandHandler('ram', ram))
    app.add_handler(CommandHandler('disk', disk))
    app.add_handler(CommandHandler('battery', battery))
    app.add_handler(CommandHandler('pwd', pwd))
    app.add_handler(CommandHandler('ls', ls))
    app.add_handler(CommandHandler('rm', rm))
    app.add_handler(CommandHandler('cat', cat))
    app.add_handler(CommandHandler('volume', volume_func))
    app.add_handler(CommandHandler('say', say))
    app.add_handler(CommandHandler('mouse', mouse_move))
    app.add_handler(CommandHandler('click', mouse_click))
    app.add_handler(CommandHandler('dclick', mouse_double_click))
    app.add_handler(CommandHandler('scroll', mouse_scroll))
    app.add_handler(CommandHandler('mpos', mouse_pos))
    app.add_handler(CommandHandler('browser', browser))
    app.add_handler(CommandHandler('wifi', wifi))
    app.add_handler(CommandHandler('ping', ping))
    app.add_handler(CommandHandler('cmd', cmd))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(
        MessageHandler(
            filters.Document.ALL | filters.PHOTO | filters.VIDEO,
            download_file
        )
    )

    print('Polling...')
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        sys.exit(0)