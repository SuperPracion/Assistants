from assistants.base_bot import BaseBot
from assistants.reminiscent_about_classes import settings

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tinydb import TinyDB, Query
from aiogram import F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery


class ReminiscentAboutClassesBot(BaseBot):
    def __init__(self):
        super().__init__(settings.bot_token)
        # Вынести в настройки
        self.googlesheets_link = settings.googlesheets_link
        self.inline_buttons = None
        self.keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📖 GoogleSheets")],
                [KeyboardButton(text="📚 Текущие события")]
            ],
            resize_keyboard=True,
        )
        # Вынести в отдельный класс
        self._creds = ServiceAccountCredentials.from_json_keyfile_name(settings.creds, settings.scope)
        self._client = gspread.authorize(self._creds)
        self.spreadsheet = self._client.open(settings.table_name).get_worksheet(settings.worksheet)

    def register_handlers(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                text='Привет! Наша группу для проектов и учёбы: https://t.me/svetlana_stukalova',
                reply_markup=self.keyboard
            )

        @self.dp.message(F.text == "📖 GoogleSheets")
        async def with_puree(message: Message):
            await message.reply(
                text=f'📖 <a href={self.googlesheets_link}>GoogleSheets</a>',
                parse_mode="HTML"
            )

        @self.dp.message(F.text == "📚 Текущие события")
        async def without_puree(message: Message):
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text="Подписаться",
                callback_data="subscribe"),
                InlineKeyboardButton(
                    text="Отписаться",
                    callback_data="unsubscribe"
                )
            )
            with TinyDB(settings.MESSAGES_BD, encoding='utf-8') as messages:
                for row_number, event in enumerate(self.spreadsheet.get_all_records()):
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
                    record = messages.get(Query().row_number == row_number)
                    if record:
                        record['messages'].append(sending_message.message_id)
                        messages.upsert(record, Query().row_number == row_number)
                    else:
                        messages.insert(
                            {'row_number': row_number, 'messages': [sending_message.message_id]})

        @self.dp.callback_query(F.data == "subscribe")
        async def send_random_value(callback: CallbackQuery):
            with TinyDB(settings.MESSAGES_BD, encoding='utf-8') as messages:
                for record_data in messages.all():
                    if callback.message.message_id in record_data['messages']:
                        row_number = record_data['row_number']

            response = self.spreadsheet.get_all_records()[row_number]
            response['Участники'] += f'{callback.from_user.username}\n'
            self.spreadsheet.update_acell(f'G{row_number + 2}', response['Участники'])

            await callback.message.answer(f'Вы подписались на {response['Название']}')

        @self.dp.callback_query(F.data == "unsubscribe")
        async def send_random_value(callback: CallbackQuery):
            with TinyDB(settings.MESSAGES_BD, encoding='utf-8') as messages:
                for record_data in messages.all():
                    if callback.message.message_id in record_data['messages']:
                        row_number = record_data['row_number']

            response = self.spreadsheet.get_all_records()[row_number]
            names = response['Участники'].split('\n')
            names.remove(callback.from_user.username)
            response['Участники'] = '\n'.join(names)
            self.spreadsheet.update_acell(f'G{row_number + 2}', response['Участники'])

            await callback.message.answer(f'Вы подписались на {response['Название']}')

        @self.dp.message(Command('help'))
        async def help_command(message: Message):
            await message.reply("Список доступных команд:\n/start - Начало работы\n/help - Помощь")
