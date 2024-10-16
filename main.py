import asyncio

from assistants.reminiscent_about_classes.reminiscent_about_classes_bot import ReminiscentAboutClassesBot
from assistants.english_words_gamer.english_words_gamer_bot import EnglishWordsGamerBot


async def main():
    remin_bot = ReminiscentAboutClassesBot()
    await remin_bot.start()

    # english_bot = EnglishWordsGamerBot()
    # await english_bot.start()


if __name__ == "__main__":
    asyncio.run(main())
