from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import Message

from storage.database import add_user_tg, add_token_direct, get_users_accounts, delete_dashboard_token
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
            btn = types.InlineKeyboardButton(login[0], callback_data=f"acc_info|{login[0]}")
            markup_logins.add(btn)

        await bot.send_message(
            message.chat.id,
            "Список авторизованных аккаунтов в Яндекс.Директ. Кликните, чтобы удалить аккаунт:",
            reply_markup=markup_logins,
        )

    @dp.callback_query_handler(lambda call: call.data.startswith("acc_info"))
    async def ask_delete_acc(call: types.CallbackQuery, state: FSMContext) -> None:
        """Callback of delete button. Asks if user really wants to delete acc"""
        await bot.answer_callback_query(call.id)
        login = call.data.split("|")[1]

        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("Да", callback_data=f"delete|{login}")
        btn_no = types.InlineKeyboardButton("Отмена", callback_data="back_main")
        markup.row(btn_yes, btn_no)

        await call.message.answer(f"Вы уверены, что хотите удалить доступы к аккаунту {login}?", reply_markup=markup)
        await state.finish()

    @dp.callback_query_handler(lambda call: call.data.startswith("delete"))
    async def delete_acc(call: types.CallbackQuery, state: FSMContext) -> None:
        """Delete token for direct account from database"""
        await bot.answer_callback_query(call.id)
        login = call.data.split("|")[1]
        user_id = call.message.chat.id
        await delete_dashboard_token(user_id, login)
        await state.finish()
        await bot.send_message(user_id, "Успешно удалено!")

    @dp.callback_query_handler(lambda call: call.data == "back_main")
    async def callback_back_main(call: types.CallbackQuery, state: FSMContext) -> None:
        """Callback to cancel delete account"""
        await bot.answer_callback_query(call.id)
        await verified_accounts(call.message)
        await state.finish()

    executor.start_polling(dispatcher=dp)
