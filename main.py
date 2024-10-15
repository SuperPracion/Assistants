import asyncio

from assistants.reminiscent_about_classes.reminiscent_about_classes_bot import MyBot
from assistants.reminiscent_about_classes.settings import bot_token

async def main():
    my_bot = MyBot(bot_token)
    await my_bot.start()


if __name__ == "__main__":
    asyncio.run(main())