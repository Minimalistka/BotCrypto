from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def mainKeyboard():
    # Создаём красивую клавиатуру с кнопками
    keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [types.KeyboardButton(text="💸 Курс валют"), types.KeyboardButton(text="🔄 Конвертировать валюту")],
                [types.KeyboardButton(text="🤖 О боте"), types.KeyboardButton(text="⚙️ Поддержка")]
            ]
        )

# Создаём красивую клавиатуру с инлайн-кнопками
keyboard_in = InlineKeyboardMarkup(
        inline_keyboard=[
            [{"text": " USD в EUR", "callback_data": "convert_usd_eur"}],
            [{"text": " USD в RUB", "callback_data": "convert_usd_rub"}],
            [{"text": " USD в GBP", "callback_data": "convert_usd_gbp"}],
            [{"text": " USD в JPY", "callback_data": "convert_usd_jpy"}],
            [{"text": " USD в CNY", "callback_data": "convert_usd_cny"}]
        ]
    )