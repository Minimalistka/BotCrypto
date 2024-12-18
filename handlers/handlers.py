from aiogram import Bot, Router, types
from aiogram.filters import Command
import sqlite3
import os
import aiohttp
from lexicon.lexicon import LEXICON_RU
from config_data.config import Config, load_config
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class values(StatesGroup):
    eur = State()
    rub = State()
    gbp = State()
    jpy = State()
    cny = State()





router = Router()
config: Config = load_config()
bot = Bot(token=config.tg_bot.token)
api_key = config.tg_bot.api_key

# Создаём красивую клавиатуру с кнопками
keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [types.KeyboardButton(text="💸 Курс валют"), types.KeyboardButton(text="🔄 Конвертировать валюту")],
                [types.KeyboardButton(text="🤖 О боте"), types.KeyboardButton(text="⚙️ Поддержка")]
            ]
        )

# Функция для получения курсов валют через API Open Exchange Rates
async def get_exchange_rates():
    url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data.get("rates", {})


if not os.path.exists("currency.db"):
    conn = sqlite3.connect("currency.db")
    cursor = conn.cursor()
    # Создаём таблицу, если её ещё нет
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
    conn.commit()
    conn.close()


# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Сохраняем пользователя в базу данных
    conn = sqlite3.connect("currency.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

    await message.answer(text=LEXICON_RU['/start'], reply_markup=keyboard, parse_mode="HTML")

# Обработчик команды /help
@router.message(Command("help"))
async def start_command(message: types.Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=keyboard, parse_mode="HTML")

# Обработчик для команды "Курс валют"
@router.message(lambda message: message.text == "💸 Курс валют")
async def currency_rates(message: types.Message):
    rates = await get_exchange_rates()
    if rates:
        # Формируем список курсов валют с эмодзи и красивым оформлением
        response = "💸 <b>Актуальные курсы валют (USD):</b>\n\n"
        response += "\n".join([f" <b>{currency}</b>: {rate}" for currency, rate in rates.items() if currency in ["EUR", "RUB", "GBP", "JPY", "CNY"]])
    else:
        response = " ❗ <b>Не удалось получить курсы валют. Попробуйте позже.</b>"

    await message.answer(response, parse_mode="HTML")

# Обработчик для конвертации валют
@router.message(lambda message: message.text == "🔄 Конвертировать валюту")
async def convert_currency(message: types.Message):
    # Создаём клавиатуру с инлайн-кнопками
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [{"text": " USD в EUR", "callback_data": "convert_usd_eur"}],
            [{"text": " USD в RUB", "callback_data": "convert_usd_rub"}],
            [{"text": " USD в GBP", "callback_data": "convert_usd_gbp"}],
            [{"text": " USD в JPY", "callback_data": "convert_usd_jpy"}],
            [{"text": " USD в CNY", "callback_data": "convert_usd_cny"}]
        ]
    )

    await message.answer(
            "🔄 <b>Выберите направление конвертации:</b>", reply_markup=keyboard, parse_mode="HTML"
    )

# Определяем состояния
class ConvertState(StatesGroup):
    conversion = State()  # Выбранное направление
    amount = State()  # Введённая сумма

# Обработчик для обработки нажатий на инлайн-кнопки
@router.callback_query(lambda c: c.data.startswith("convert"))
async def process_conversion(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    rates = await get_exchange_rates()

    if rates:
        # Сохраняем выбранное направление и курсы валют
        await state.update_data(conversion=data, rates=rates)

        await callback_query.message.answer(
            "Введите сумму в USD, которую хотите конвертировать:"
        )
        # Устанавливаем состояние для ожидания суммы
        await state.set_state(ConvertState.amount)
    else:
        await callback_query.message.answer(
            "Не удалось получить курсы валют. Попробуйте позже."
        )


@router.message(lambda message: message.text.isdigit())
async def get_amount(message: Message, state: FSMContext):
    user_data = await state.get_data()
    conversion = user_data.get("conversion")
    rates = user_data.get("rates")
    amount = float(message.text)

    if not rates:
        await message.answer("Курсы валют не найдены. Попробуйте позже.")
        return

    # Карта конверсии
    conversion_map = {
        "convert_usd_eur": "EUR",
        "convert_usd_rub": "RUB",
        "convert_usd_gbp": "GBP",
        "convert_usd_jpy": "JPY",
        "convert_usd_cny": "CNY",
    }

    target_currency = conversion_map.get(conversion)
    if target_currency and target_currency in rates:
        rate = rates[target_currency]
        result = amount * rate
        response = f"💷 <b>{amount} USD = {result:.2f} {target_currency}</b>"
    else:
        response = "❗ <b>Ошибка: неизвестный запрос или курс валют недоступен.</b>"

    await message.answer(response, parse_mode="HTML")
    await state.clear()
# Обработчик для команды "О боте"
@router.message(lambda message: message.text == "🤖 О боте")
async def about_bot(message: types.Message):
    await message.answer(text=LEXICON_RU['О боте'], parse_mode="HTML")

# Обработчик для команды "Поддержка"
@router.message(lambda message: message.text == "⚙️ Поддержка")
async def support(message: types.Message):
    await message.answer(text=LEXICON_RU['Поддержка'], parse_mode="HTML")


