from assistants.base_bot import BaseBot
from assistants.reminiscent_about_classes.settings import *

from aiogram import F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tinydb import TinyDB, Query

from databases.google_sheets_database import GoogleSheets


class ReminiscentAboutClassesBot(BaseBot):
    def __init__(self):
        super().__init__(TOKEN)
        self.sheet = GoogleSheets(SCOPE, CREDS, TABLE_NAME, WORKSHEET).sheet

    def register_handlers(self):
        @self.dp.message(Command('start'))
        async def cmd_start(message: Message):
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text='📖 GoogleSheets')],
                    [KeyboardButton(text='📚 Текущие события')],
                    [KeyboardButton(text='💰Ставка, кто проебёт сроки')]
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
            builder = InlineKeyboardBuilder(
                [[InlineKeyboardButton(text='Подписаться', callback_data='subscribe')],
                 [InlineKeyboardButton(text='Отписаться', callback_data='unsubscribe')]]
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
                with TinyDB(MESSAGES_BD, encoding='utf-8') as messages:
                    record = messages.get(Query().row_number == row_number)
                    if record:
                        record['messages'].append(sending_message.message_id)
                        messages.upsert(record, Query().row_number == row_number)
                    else:
                        messages.insert({'row_number': row_number, 'messages': [sending_message.message_id]})

        @self.dp.callback_query(F.data == 'subscribe')
        async def subscribe(callback: CallbackQuery):
            with TinyDB(MESSAGES_BD, encoding='utf-8') as messages:
                for record_data in messages.all():
                    if callback.message.message_id in record_data['messages']:
                        row_number = record_data['row_number']

            response = self.sheet.get_all_records()[row_number]
            response['Участники'] += f'{callback.from_user.username}\n'
            self.sheet.update_acell(f'G{row_number + 2}', response['Участники'])
            await callback.message.answer(f'Вы подписались на {response['Название']}')

        @self.dp.callback_query(F.data == 'unsubscribe')
        async def unsubscribe(callback: CallbackQuery):
            with TinyDB(MESSAGES_BD, encoding='utf-8') as messages:
                for record_data in messages.all():
                    if callback.message.message_id in record_data['messages']:
                        row_number = record_data['row_number']

            response = self.sheet.get_all_records()[row_number]
            names = response['Участники'].split('\n')
            names.remove(callback.from_user.username)
            response['Участники'] = '\n'.join(names)
            self.sheet.update_acell(f'G{row_number + 2}', response['Участники'])
            await callback.message.answer(f'Вы подписались на {response['Название']}')

        @self.dp.message(F.text == '💰Ставка, кто проебёт сроки')
        async def place_bet(message: Message):
            await message.reply(
                text=f'РОССИЙСКАЯ ГОСУДАРСТВЕННАЯ АНТИМОНОПОЛЬНАЯ СЛУЖБА ЗАСЕКЛА ПОПЫТКУ НЕЗАКОННОЙ ИГРОВОЙ ДЕЯТЕЛЬНОСТИ')
