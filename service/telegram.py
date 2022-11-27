from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import Message

from storage.database import add_user_tg, add_token_direct, get_users_accounts
from service.yandex_queries import URL_OAUTH, verify_direct, get_login_direct


def run_telegram():
    tg_token = "5601478515:AAHxOEstj9wNxAxtPXLSXiGhWEGWHsgGeTY"
    bot = Bot(tg_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    class Form(StatesGroup):
        get_token = State()

    @dp.message_handler(commands=["start"])
    async def send_welcome(message: Message) -> None:
        """Welcome message after /start commands"""
        await add_user_tg(message)
        await bot.send_message(
            message.chat.id,
            "Бот-помощник по рекламе в Яндекс.Директ. Используй /add_account, чтобы авторизовать аккаунт Яндекс.Директ",
        )

    @dp.message_handler(commands=["add_account"])
    async def account(message: Message) -> None:
        btn_login = types.InlineKeyboardButton("Авторизоваться", url=URL_OAUTH)
        markup_login = types.InlineKeyboardMarkup().add(btn_login)

        await bot.send_message(
            message.chat.id,
            "Авторизуйся, чтобы добавить аккаунт. Для этого, перейдите по ссылке и пришлите код подтверждения.",
            reply_markup=markup_login,
        )
        await Form.get_token.set()

    @dp.message_handler(state=Form.get_token)
    async def verify_code(message: types.message.Message, state: FSMContext):
        async with state.proxy() as data:
            data["get_token"] = message.text
            await state.finish()

        token = await verify_direct(message.text)
        if token:
            login = await get_login_direct(token)
            await add_token_direct(message.chat.id, token, login)
            await bot.send_message(message.chat.id, "☑️ Успешная авторизация!")
        else:
            await bot.send_message(message.chat.id, "Введен неверный код. Попробуйте еще раз. /add_account")

    @dp.message_handler(commands=["accounts"])
    async def verified_accounts(message: Message) -> None:
        """Send accounts of user with inline buttons"""
        markup_logins = types.InlineKeyboardMarkup()
        for login in await get_users_accounts(message):
            btn = types.InlineKeyboardButton(login[0], callback_data="Test")
            markup_logins.add(btn)

        await bot.send_message(
            message.chat.id,
            "Список авторизованных аккаунтов в Яндекс.Директ:",
            reply_markup=markup_logins,
        )

    executor.start_polling(dispatcher=dp)
