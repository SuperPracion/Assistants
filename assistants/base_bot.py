from multiprocessing.util import sub_warning

from aiogram import Bot, Dispatcher
from abc import ABC, abstractmethod

class BaseBot(ABC):
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

    async def start(self):
        """Метод для запуска работы"""
        self.register_handlers()
        await self.dp.start_polling(self.bot)

    @abstractmethod
    def register_handlers(self):
        """Метод для описания команд"""
        pass

    async def shutdown(self):
        """Метод остановки"""
        await self.bot.close()
