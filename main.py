#!/usr/bin/env python3

import os
import sys
import platform
import psutil
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
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
import logging

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

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def superuser_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != SUPERUSER:
            await message.answer("⛔ nah bro, you can't do that")
            return
        return await func(message, *args, **kwargs)
    return wrapper


@dp.message(CommandStart())
@superuser_only
async def start(message: Message):
    await message.answer('blank')


@dp.message(Command('help'))
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


@dp.message(Command('suicide'))
@superuser_only
async def suicide(message: Message):
    await message.answer("Bye 👋")
    await bot.session.close()
    sys.exit(0)


@dp.message(Command('system'))
@superuser_only
async def system(message: Message):
    await message.answer(f"{platform.system()} {platform.release()}")


@dp.message(Command('uptime'))
@superuser_only
async def uptime(message: Message):
    uptime_sec = int(datetime.now().timestamp() - psutil.boot_time())
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    seconds = uptime_sec % 60
    
    await message.answer(f"{days}d {hours}h {minutes}m {seconds}s")


@dp.message(Command('screenshot'))
@superuser_only
async def screenshot(message: Message):
    try:
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        
        photo = FSInputFile(filename)
        await message.answer_photo(photo=photo, caption="")
        os.remove(filename)
    except Exception as e:
        await message.answer(f"Error: {e}")


@dp.message(Command('superuser'))
async def superuser(message: Message):
    if message.from_user.id == SUPERUSER:
        await message.answer("✅ True")
    else:
        await message.answer("❌ False")


@dp.message(Command('msg'))
@superuser_only
async def msg(message: Message):
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


@dp.message(Command('winl'))
@superuser_only
async def winl(message: Message):
    try:
        def execute():
            subprocess.run('rundll32.exe user32.dll,LockWorkStation')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🚪 Locking...")
    except Exception:
        await message.answer("❌")


@dp.message(Command('shutdown'))
@superuser_only
async def shutdown(message: Message):
    try:
        def execute():
            subprocess.run('shutdown /s /t 0 /f', shell=True, check=True)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🔴 Shutting down...")
    except Exception:
        await message.answer("❌")


@dp.message(Command('hibernate'))
@superuser_only
async def hibernate(message: Message):
    try:
        def execute():
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("💤 Hibernating...")
    except Exception:
        await message.answer("❌")


@dp.message(Command('type'))
@superuser_only
async def type_text(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Usage: /type <text>")
        return
    
    text = ' '.join(message.text.split()[1:])
    
    try:
        def execute():
            time.sleep(0.5)
            pyautogui.typewrite(text, interval=0.05)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("⌨️ Typing...")
    except Exception:
        await message.answer("❌")


@dp.message(Command('github'))
async def github(message: Message):
    await message.answer("https://github.com/SuperDragon777/MyRemotePC")


@dp.message(Command('ip'))
@superuser_only
async def ip(message: Message):
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        external_ip = requests.get('https://api.ipify.org', timeout=5).text

        await message.answer(
            f"🏠 Local: {local_ip}\n"
            f"🌍 External: {external_ip}"
        )
    except Exception:
        await message.answer("❌")


@dp.message(Command('f4'))
@superuser_only
async def f4(message: Message):
    try:
        def execute():
            pyautogui.hotkey('alt', 'f4')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("⏳ Executing...")
    except Exception:
        await message.answer("❌")


@dp.message(Command('cpu'))
@superuser_only
async def cpu(message: Message):
    try:
        usage = psutil.cpu_percent(interval=1)
        await message.answer(f"🧠 CPU load: {usage}%")
    except Exception:
        await message.answer("❌")


@dp.message(Command('ram'))
@superuser_only
async def ram(message: Message):
    try:
        mem = psutil.virtual_memory()

        total = mem.total // (1024 ** 2)
        used = mem.used // (1024 ** 2)
        free = mem.available // (1024 ** 2)
        percent = mem.percent

        await message.answer(
            f"📦 Total: {total} MB\n"
            f"📊 Used: {used} MB\n"
            f"🟢 Free: {free} MB\n"
            f"📈 Load: {percent}%"
        )
    except Exception:
        await message.answer("❌")


@dp.message(Command('disk'))
@superuser_only
async def disk(message: Message):
    try:
        usage = psutil.disk_usage('/')

        total = usage.total // (1024 ** 3)
        used = usage.used // (1024 ** 3)
        free = usage.free // (1024 ** 3)
        percent = usage.percent

        await message.answer(
            f"📦 Total: {total} GB\n"
            f"📊 Used: {used} GB\n"
            f"🟢 Free: {free} GB\n"
            f"📈 Load: {percent}%"
        )
    except Exception:
        await message.answer("❌")


@dp.message(Command('battery'))
@superuser_only
async def battery(message: Message):
    try:
        bat = psutil.sensors_battery()

        if bat is None:
            await message.answer("🔌 Battery not found")
            return

        percent = bat.percent
        plugged = bat.power_plugged

        status = "🔌 Charging" if plugged else "🔋 On battery"

        await message.answer(
            f"⚡ Charge: {percent}%\n"
            f"{status}"
        )
    except Exception:
        await message.answer("❌")


@dp.message(Command('pwd'))
@superuser_only
async def pwd(message: Message):
    try:
        cwd = os.getcwd()
        await message.answer(f"📁 Current directory:\n{cwd}")
    except Exception:
        await message.answer("❌")


@dp.message(Command('ls'))
@superuser_only
async def ls(message: Message):
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


@dp.message(Command('rm'))
@superuser_only
async def rm(message: Message):
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


@dp.message(Command('cat'))
@superuser_only
async def cat(message: Message):
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


@dp.message(Command('volume'))
@superuser_only
async def volume_func(message: Message):
    try:
        args = message.text.split()[1:] if message.text else []
        
        if not args:
            def get_vol():
                comtypes.CoInitialize()
                try:
                    current = volume.current_volume()
                    return current
                finally:
                    comtypes.CoUninitialize()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                current = await asyncio.get_event_loop().run_in_executor(executor, get_vol)
            await message.answer(f"🔊 Current volume: {current}%")
            return
        
        percent = int(args[0])
        
        if percent < 0 or percent > 100:
            await message.answer("❌ Volume must be 0-100")
            return
        
        def execute():
            comtypes.CoInitialize()
            try:
                volume.volume(percent)
            finally:
                comtypes.CoUninitialize()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer(f"🔊 Volume changed to {percent}%")
        
    except ValueError:
        await message.answer("❌")
    except Exception:
        await message.answer("❌")


@dp.message(Command('say'))
@superuser_only
async def say(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /say <text>")
        return
    
    text = ' '.join(args)
    
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
    
    threading.Thread(target=speak, args=(text,), daemon=False).start()
    
    await message.answer("🗣️ Speaking...")


@dp.message(Command('mouse'))
@superuser_only
async def mouse_move(message: Message):
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


@dp.message(Command('click'))
@superuser_only
async def mouse_click(message: Message):
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


@dp.message(Command('dclick'))
@superuser_only
async def mouse_double_click(message: Message):
    try:
        def execute():
            pyautogui.doubleClick()
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🖱️ Double clicked")
    except Exception:
        await message.answer("❌")


@dp.message(Command('scroll'))
@superuser_only
async def mouse_scroll(message: Message):
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


@dp.message(Command('mpos'))
@superuser_only
async def mouse_pos(message: Message):
    try:
        x, y = pyautogui.position()
        await message.answer(f"🖱️ Mouse position: ({x}, {y})")
    except Exception:
        await message.answer("❌")


@dp.message(Command('browser'))
@superuser_only
async def browser(message: Message):
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


@dp.message(Command('wifi'))
@superuser_only
async def wifi(message: Message):
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


@dp.message(Command('ping'))
@superuser_only
async def ping(message: Message):
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


@dp.message(Command('cmd'))
@superuser_only
async def cmd(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /cmd <command>")
        return
    
    command = ' '.join(args)
    
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
        
        await message.answer(f"⚙️ Executing: `{command}`", parse_mode=ParseMode.MARKDOWN)
        
        stdout, stderr, returncode = await asyncio.get_event_loop().run_in_executor(None, execute)
        
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
        
        await message.answer(output, parse_mode=ParseMode.MARKDOWN)
    except subprocess.TimeoutExpired:
        await message.answer("❌ Command timeout (30s)")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


@dp.message(Command('tm'))
@superuser_only
async def tm(message: Message):
    try:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append(
                    f"{info['pid']:>6} | "
                    f"{info['cpu_percent']:>5.1f}% CPU | "
                    f"{info['memory_percent']:>5.1f}% RAM | "
                    f"{info['name']}"
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not processes:
            await message.answer("❌ No processes found")
            return

        output = "PID    | CPU   | RAM   | NAME\n"
        output += "-" * 40 + "\n"
        output += "\n".join(processes[:40])

        if len(output) > 4000:
            output = output[:4000] + "\n... (truncated)"

        await message.answer(
            f"🧾 Active processes:\n\n```\n{output}\n```",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception:
        await message.answer("❌ Error getting process list")


@dp.message(Command('kill'))
@superuser_only
async def kill(message: Message):
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Usage: /kill <pid>")
        return

    try:
        pid = int(args[0])
        p = psutil.Process(pid)
        p.kill()
        await message.answer(f"💀 Killed process {pid}")
    except psutil.NoSuchProcess:
        await message.answer("❌ No such process")
    except Exception:
        await message.answer("❌ Access denied or error")


@dp.message(F.document | F.photo | F.video)
@superuser_only
async def download_file(message: Message):
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


@dp.message(F.text & ~F.text.startswith('/'))
@superuser_only
async def handle_message(message: Message):
    await message.answer('idk what to do')


async def on_startup():
    try:
        await bot.send_message(chat_id=SUPERUSER, text="🟢 Bot is polling")
    except Exception as e:
        print(f"Startup notify error: {e}")


async def main():
    await on_startup()
    print('Polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)