from aiogram import Bot, Dispatcher
from pathlib import Path
from .decorators import set_superuser

from . import basic
from . import system
from . import pc_control
from . import input
from . import file_manager
from . import internet
from . import messages
from . import files
from . import default


def register_all_handlers(dp: Dispatcher, bot: Bot, superuser_id: int, download_dir: Path):
    set_superuser(superuser_id)
    
    basic.register_handlers(dp, bot)
    system.register_handlers(dp)
    pc_control.register_handlers(dp, bot)
    input.register_handlers(dp)
    file_manager.register_handlers(dp)
    internet.register_handlers(dp)
    messages.register_handlers(dp)
    files.register_handlers(dp, bot, download_dir)
    default.register_handlers(dp)
