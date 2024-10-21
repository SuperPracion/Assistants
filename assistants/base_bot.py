from sqlite3 import connect
from aiogram import Bot, Dispatcher
from abc import ABC, abstractmethod

class BaseBot(ABC):
    def __init__(self, token, db_name):
        self.token = token
        self.bot = Bot(self.token)
        self.dp = Dispatcher()
        self.db_name = db_name
        self.connect = connect(self.db_name)
        self.cursor = self.connect.cursor()

    async def start(self, *args, **kwargs):
        """Метод для запуска работы"""
        self.register_handlers()
        await self.dp.start_polling(self.bot, *args, **kwargs)

    @abstractmethod
    def register_handlers(self):
        """Метод для описания команд"""
        pass

    async def shutdown(self):
        """Метод остановки"""
        await self.bot.close()

    async def auto_db_commit(func):
        async def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self.connect.commit()
            return res
        return wrapper