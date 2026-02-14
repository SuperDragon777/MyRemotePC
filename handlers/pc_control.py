import os
import subprocess
import threading
import psutil
import comtypes
import asyncio
import concurrent.futures
import pyttsx3
from datetime import datetime
from PIL import ImageGrab
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
import volume
from .decorators import superuser_only

bot: Bot = None


def register_handlers(dispatcher: Dispatcher, bot_instance: Bot):
    global bot
    bot = bot_instance
    
    dispatcher.message.register(screenshot_handler, Command('screenshot'))
    dispatcher.message.register(winl_handler, Command('winl'))
    dispatcher.message.register(shutdown_handler, Command('shutdown'))
    dispatcher.message.register(hibernate_handler, Command('hibernate'))
    dispatcher.message.register(f4_handler, Command('f4'))
    dispatcher.message.register(volume_handler, Command('volume'))
    dispatcher.message.register(say_handler, Command('say'))
    dispatcher.message.register(cmd_handler, Command('cmd'))
    dispatcher.message.register(tm_handler, Command('tm'))
    dispatcher.message.register(kill_handler, Command('kill'))


@superuser_only
async def screenshot_handler(message: Message):
    try:
        status_msg = await message.answer("📸 Делаю скриншот...")
        
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        screenshot = ImageGrab.grab()
        
        screenshot.save(filename, "JPEG", quality=85, optimize=True)
        
        await status_msg.delete()
        
        photo = FSInputFile(filename)
        await message.answer_photo(photo=photo, caption="📸 Screenshot")
        
        os.remove(filename)
    except Exception as e:
        await message.answer(f"❌ Error: {e}")


@superuser_only
async def winl_handler(message: Message):
    try:
        def execute():
            subprocess.run('rundll32.exe user32.dll,LockWorkStation')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🚪 Locking...")
    except Exception:
        await message.answer("❌")


@superuser_only
async def shutdown_handler(message: Message):
    try:
        def execute():
            subprocess.run('shutdown /s /t 0 /f', shell=True, check=True)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("🔴 Shutting down...")
    except Exception:
        await message.answer("❌")


@superuser_only
async def hibernate_handler(message: Message):
    try:
        def execute():
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("💤 Hibernating...")
    except Exception:
        await message.answer("❌")


@superuser_only
async def f4_handler(message: Message):
    try:
        def execute():
            import pyautogui
            pyautogui.hotkey('alt', 'f4')
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        
        await message.answer("⏳ Executing...")
    except Exception:
        await message.answer("❌")


@superuser_only
async def volume_handler(message: Message):
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


@superuser_only
async def say_handler(message: Message):
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


@superuser_only
async def cmd_handler(message: Message):
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


@superuser_only
async def tm_handler(message: Message):
    try:
        status_msg = await message.answer("⏳ Сбор данных...")
        
        all_procs = list(psutil.process_iter(['pid', 'name']))
        for proc in all_procs:
            try:
                proc.cpu_percent()
            except:
                pass
        
        await asyncio.sleep(0.5)
        
        processes = []
        for proc in all_procs:
            try:
                info = proc.info
                if info['name'] == 'System Idle Process':
                    continue
                
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'] or 'Unknown',
                    'cpu': proc.cpu_percent(),
                    'mem': proc.memory_percent(),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        await status_msg.delete()
        
        processes.sort(key=lambda x: x['cpu'], reverse=True)
        
        text = "<b>🔥 TOP 25 CPU</b>\n\n"
        
        for i, p in enumerate(processes[:25], 1):
            if p['cpu'] > 50:
                emoji = "🔴"
            elif p['cpu'] > 20:
                emoji = "🟡"
            else:
                emoji = "🟢"
            
            text += f"{i:>2}. {emoji} <code>{p['cpu']:>5.1f}%</code> {p['name'][:28]} <code>{p['pid']}</code>\n"
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        
        text += f"\n💻 CPU: <b>{cpu}%</b> │ 💾 RAM: <b>{mem.percent}%</b>"
        text += f"\n📊 Процессов: <b>{len(processes)}</b>"
        
        await message.answer(text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Ошибка")


@superuser_only
async def kill_handler(message: Message):
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
