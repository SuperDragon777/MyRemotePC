from aiogram import Dispatcher, F
from aiogram.types import Message
from .decorators import superuser_only


def register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(handle_message_handler, F.text & ~F.text.startswith('/'))


@superuser_only
async def handle_message_handler(message: Message):
    await message.answer('idk what to do')
