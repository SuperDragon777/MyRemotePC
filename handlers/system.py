import platform
import psutil
import socket
import requests
from datetime import datetime
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from .decorators import superuser_only


def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(system_handler, Command('system'))
    dispatcher.message.register(uptime_handler, Command('uptime'))
    dispatcher.message.register(cpu_handler, Command('cpu'))
    dispatcher.message.register(ram_handler, Command('ram'))
    dispatcher.message.register(disk_handler, Command('disk'))
    dispatcher.message.register(battery_handler, Command('battery'))
    dispatcher.message.register(ip_handler, Command('ip'))


@superuser_only
async def system_handler(message: Message):
    await message.answer(f"{platform.system()} {platform.release()}")


@superuser_only
async def uptime_handler(message: Message):
    uptime_sec = int(datetime.now().timestamp() - psutil.boot_time())
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    seconds = uptime_sec % 60
    
    await message.answer(f"{days}d {hours}h {minutes}m {seconds}s")


@superuser_only
async def cpu_handler(message: Message):
    try:
        usage = psutil.cpu_percent(interval=1)
        await message.answer(f"🧠 CPU load: {usage}%")
    except Exception:
        await message.answer("❌")


@superuser_only
async def ram_handler(message: Message):
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


@superuser_only
async def disk_handler(message: Message):
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


@superuser_only
async def battery_handler(message: Message):
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


@superuser_only
async def ip_handler(message: Message):
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
