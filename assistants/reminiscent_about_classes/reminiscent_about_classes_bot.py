from assistants.base_bot import BaseBot
from assistants.reminiscent_about_classes.settings import *
from assistants.reminiscent_about_classes.event_message import EventMessage
from databases.google_sheets_database import GoogleSheets

import asyncio
from aiogram import F
import datetime
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery


class ReminiscentAboutClassesBot(BaseBot):
    def __init__(self):
        super().__init__(TOKEN, DB_NAME)
        self.sheet = GoogleSheets(SCOPE, CREDS, TABLE_NAME, WORKSHEET).sheet

    def get_delta(self, callback):
        select_event_message = '''SELECT * FROM messages WHERE message_id = (?)'''
        event = EventMessage(*next(self.cursor.execute(select_event_message, (callback.message.message_id,))))

        response = self.sheet.get_all_records()[event.row_number]
        return (datetime.datetime.now() - datetime.datetime.strptime(response['Дата'], '%d.%m.%Y %H:%S')).seconds

    def register_handlers(self):
        @self.dp.message(Command('start'))
        async def cmd_start(message: Message):
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text='📖 GoogleSheets')],
                    [KeyboardButton(text='📚 Текущие события')],
                    [KeyboardButton(text='💰Ставка, кто сольётся следующим')]
                ],
                resize_keyboard=True,
            )
            await message.answer(
                text=f'Привет! Наша группу для проектов и учёбы: {TELEGRAM_GROUP_LINK}',
                reply_markup=keyboard
            )

        @self.dp.message(F.text == '📖 GoogleSheets')
        async def with_puree(message: Message):
            await message.reply(
                text=GOOGLESHEETS_LINK
            )

        @self.dp.message(F.text == '📚 Текущие события')
        async def without_puree(message: Message):
            insert_request = '''INSERT INTO messages (row_number, message_id) VALUES (?, ?)'''
            builder = InlineKeyboardBuilder(
                [[InlineKeyboardButton(text='✅ Подписаться', callback_data='subscribe'),
                  InlineKeyboardButton(text='❌ Отписаться', callback_data='unsubscribe')],
                 [InlineKeyboardButton(text='🔔 за 0 минут', callback_data='remind_in_start'),
                  InlineKeyboardButton(text='🔔 за 15 минут', callback_data='remind_in_fifteen_minutes'),
                  InlineKeyboardButton(text='🔔 за 1 час', callback_data='remind_in_an_hour')]
                 ]
            )
            for row_number, event in enumerate(self.sheet.get_all_records()):
                sending_message = await message.answer(
                    text=f"Автор: {event['Автор']}\n"
                         f"Название: {event['Название']}\n"
                         f"Тип: {event['Тип']}\n"
                         f"Описание: {event['Описание']}\n"
                         f"Дата и Время: {event['Дата']}\n"
                         f"Место: {event['Место']}\n"
                         f"Участники: {event['Участники']}\n""",
                    reply_markup=builder.as_markup()
                )
                self.cursor.execute(insert_request, (row_number, sending_message.message_id))
                self.connect.commit()

        @self.dp.callback_query(F.data == 'remind_in_an_hour')
        async def remind_in_an_hour(callback: CallbackQuery):
            await callback.message.answer(f'Напомню за 1 час до начала!')
            delta = self.get_delta(callback) - 3600
            for _ in range(delta):
                await asyncio.sleep(1)
            await self.bot.forward_message(chat_id=callback.message.chat.id,
                                           from_chat_id=callback.message.chat.id,
                                           message_id=callback.message.message_id)
            await callback.message.answer(f'Событие через 1 час!')

        @self.dp.callback_query(F.data == 'remind_in_fifteen_minutes')
        async def remind_in_fifteen_minutes(callback: CallbackQuery):
            await callback.message.answer(f'Напомню 15 минут до начала!')
            delta = self.get_delta(callback) - 900
            for _ in range(delta):
                await asyncio.sleep(1)
            await self.bot.forward_message(chat_id=callback.message.chat.id,
                                           from_chat_id=callback.message.chat.id,
                                           message_id=callback.message.message_id)
            await callback.message.answer(f'Событие через 15 минут!')

        @self.dp.callback_query(F.data == 'remind_in_start')
        async def remind_in_start(callback: CallbackQuery):
            await callback.message.answer(f'Напомню когда начнётся!')
            for _ in range(self.get_delta(callback) - 900):
                await asyncio.sleep(1)
            await self.bot.forward_message(chat_id=callback.message.chat.id,
                                           from_chat_id=callback.message.chat.id,
                                           message_id=callback.message.message_id)
            await callback.message.answer(f'Событие началось!')

        @self.dp.callback_query(F.data == 'subscribe')
        async def subscribe(callback: CallbackQuery):
            select_event_message = '''SELECT * FROM messages WHERE message_id = (?)'''
            event = EventMessage(*next(self.cursor.execute(select_event_message, (callback.message.message_id,))))

            response = self.sheet.get_all_records()[event.row_number]
            response['Участники'] += f'{callback.from_user.username}\n'
            self.sheet.update_acell(f'G{event.row_number + 2}', response['Участники'])
            await callback.message.answer(f'Вы подписались на {response['Название']}')

        @self.dp.callback_query(F.data == 'unsubscribe')
        async def unsubscribe(callback: CallbackQuery):
            select_event_message = '''SELECT * FROM messages WHERE message_id = (?)'''
            event = EventMessage(*next(self.cursor.execute(select_event_message, (callback.message.message_id,))))
            response = self.sheet.get_all_records()[event.row_number]
            names = response['Участники'].split('\n')
            names.remove(callback.from_user.username)
            response['Участники'] = '\n'.join(names)
            self.sheet.update_acell(f'G{event.row_number + 2}', response['Участники'])
            await callback.message.answer(f'Вы отписались от {response['Название']}')

        @self.dp.message(F.text == '💰Ставка, кто сольётся следующим')
        async def place_bet(message: Message):
            await message.answer('Тут долен быть алгоритм, но Тимур играл в Factorio.')
