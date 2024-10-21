from assistants.base_bot import BaseBot
from assistants.english_words_gamer.polls import Poll
from assistants.english_words_gamer.word import Word
from assistants.english_words_gamer import settings

import asyncio
from tinydb import TinyDB, Query
from random import randint, shuffle
from aiogram import types
from aiogram.filters.command import Command


class EnglishWordsGamerBot(BaseBot):
    def __init__(self):
        super().__init__(settings.bot_token, settings.bd_name)

    def new_register_handlers(self):
        @self.dp.message(Command('start'))
        async def start(message: types.Message):
            select_words = '''SELECT * FROM words_en WHERE parts_of_speech = 'NN' ORDER BY RANDOM() LIMIT 4'''
            insert_poll = '''INSERT INTO polls_en (word_id, correct_option_id, chat_id, poll_id) VALUES (?, ?, ?, ?)'''
            selection = self.cursor.execute(select_words)
            words = [Word(*data) for data in selection]
            search_word = words[0]
            shuffle(words)
            send_poll = await message.answer_poll(
                question=f'🤔Как же переводится слово {search_word.word} {search_word.abbreviation}?',
                options=[f'{word.translation}' for word in words],
                type='quiz',
                correct_option_id=words.index(search_word),
                is_anonymous=False
            )
            self.cursor.execute(insert_poll, (search_word.id, send_poll.poll.correct_option_id, message.chat.id, send_poll.poll.id))
            self.connect.commit()
            await asyncio.sleep(settings.poll_interval)

        @self.dp.poll_answer()
        async def poll_answer(answer: types.PollAnswer):
            select_poll = '''SELECT * FROM polls_en WHERE poll_id = (?)'''
            select_words = '''SELECT * FROM words_en WHERE id = (?)'''
            update_words = '''UPDATE words_en SET total_answers = (?) correct_answers = (?) WHERE id = (?)'''
            poll = Poll(*self.cursor.execute(select_poll, answer.poll_id))
            word = Word(*self.cursor.execute(select_words, poll.word_id))
            if poll.correct_option_id == answer.option_ids:
                word.correct_answers += 1
            word.total_answers += 1
            self.cursor.execute(update_words, (word.total_answers, word.correct_answers, word.id))
            self.connect.commit()

    def register_handlers(self):
        # TODO добавить обработку только для админов и конкретного чата
        @self.dp.message(Command('start'))
        async def start_command(message: types.Message):
            while True:
                with TinyDB('words.json', encoding='utf-8') as words:
                    rnd_words = list()
                    for _ in range(4):
                        rnd_words.append(words.search(Query().id == randint(0, len(words)))[0])

                correct_word = rnd_words[0]
                shuffle(rnd_words)
                send_poll = await message.answer_poll(
                    question=f'🤔Как же переводится слово {correct_word['word']} {correct_word['abbreviation']}?',
                    options=[f'{word['translation']}' for word in rnd_words],
                    type='quiz',
                    correct_option_id=words.index(correct_word),
                    is_anonymous=False
                )

                with TinyDB('polls.json', encoding='utf-8') as polls:
                    polls.insert({'poll_id': send_poll.poll.id,
                                  'word_id': correct_word['id'],
                                  'correct_option_id': send_poll.poll.correct_option_id})
                await asyncio.sleep(settings.poll_interval)

        @self.dp.message(Command('stop'))
        async def help_command(message: types.Message):
            await self.shutdown()

        @self.dp.poll_answer()
        async def poll_answer(answer: types.PollAnswer):
            with (
                TinyDB('polls.json', encoding='utf-8') as polls,
                TinyDB('words.json', encoding='utf-8') as words
            ):
                poll = polls.search(Query().poll_id == answer.poll_id)[0]
                word = words.search(Query().id == poll['word_id'])[0]

                if poll['correct_option_id'] == answer.option_ids[0]:
                    word['correct_answers'] += 1
                word['total_answers'] += 1
                words.upsert(word, Query().id == poll['word_id'])
