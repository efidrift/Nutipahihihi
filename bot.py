import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен берётся из переменных окружения (никогда не хардкодь!)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("⛔ Установите переменную окружения BOT_TOKEN")

# База слов. В будущем можно загружать из CSV/JSON/БД
WORDS = [
    {"en": "Apple", "ru": "Яблоко"},
    {"en": "House", "ru": "Дом"},
    {"en": "Water", "ru": "Вода"},
    {"en": "Sun", "ru": "Солнце"},
    {"en": "Book", "ru": "Книга"},
    {"en": "Computer", "ru": "Компьютер"},
    {"en": "Time", "ru": "Время"},
    {"en": "Friend", "ru": "Друг"},
    {"en": "Language", "ru": "Язык"},
    {"en": "Dream", "ru": "Мечта / Сон"},
]

class FlashcardState(StatesGroup):
    viewing = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def create_kb(show_answer: bool = False) -> InlineKeyboardMarkup:
    kb = []
    if not show_answer:
        kb.append([InlineKeyboardButton(text="👁 Показать перевод", callback_data="show_ru")])
    kb.append([InlineKeyboardButton(text="➡️ Следующее слово", callback_data="next")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

async def send_card(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("idx", 0)
    words = data.get("words", [])
    show_answer = data.get("show_answer", False)

    # Если слова закончились, перемешиваем заново
    if idx >= len(words):
        await state.update_data(idx=0, words=random.sample(WORDS, len(WORDS)), show_answer=False)
        data = await state.get_data()
        idx = 0

    word = words[idx]
    text = f"🇬🇧 <b>{word['en']}</b>\n"
    text += f"🇷🇺 <i>{word['ru']}</i>" if show_answer else "<i>Нажми кнопку, чтобы увидеть перевод</i>"

    await message.answer(text, reply_markup=create_kb(show_answer), parse_mode="HTML")

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    shuffled = random.sample(WORDS, len(WORDS))
    await state.set_state(FlashcardState.viewing)
    await state.update_data(words=shuffled, idx=0, show_answer=False)
    await send_card(message, state)

@dp.callback_query(FlashcardState.viewing)
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    action = callback.data

    if action == "show_ru":
        await state.update_data(show_answer=True)
    elif action == "next":
        await state.update_data(idx=data.get("idx", 0) + 1, show_answer=False)

    await callback.answer()
    await send_card(callback.message, state)

async def main():
    print("🤖 Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())