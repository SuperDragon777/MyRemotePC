from functools import wraps
from aiogram.types import Message

SUPERUSER = None


def set_superuser(superuser_id: int):
    global SUPERUSER
    SUPERUSER = superuser_id


def superuser_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != SUPERUSER:
            await message.answer("⛔ nah bro, you can't do that")
            return
        return await func(message, *args, **kwargs)
    return wrapper
