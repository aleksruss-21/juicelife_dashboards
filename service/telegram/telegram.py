from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import Message

from datetime import datetime, timedelta

import cfg
import service.yandex
from storage.database import (
    add_user_tg,
    add_token_direct,
    get_users_accounts,
    delete_dashboard_token,
    add_goal_id_direct,
)
from service.yandex_queries import URL_OAUTH, verify_direct, get_login_direct
from service.telegram import telegram_messages


def run_telegram():
    """Run telegram instance"""
    tg_token = cfg.config.telegram.tg_token
    tg_nots_token = cfg.config.telegram.tg_nots_token
    bot = Bot(tg_token)
    aleks_bot = Bot(tg_nots_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    class Form(StatesGroup):
        get_token = State()
        get_goal_id = State()
        get_goal_id_manual = State()
        login = State()
        goals = State()
        token = State()
        current_goal = State()

    @dp.message_handler(commands=["start"])
    async def send_welcome(message: Message) -> None:
        """Welcome message after /start commands"""
        if await add_user_tg(message) is True:
            await aleks_bot.send_message(90785234, telegram_messages.send_nots_new_user(message), parse_mode="HTML")

        daily_btn = types.InlineKeyboardButton("📅 Ежедневная сводка", callback_data="daily")
        dashboard_btn = types.InlineKeyboardButton("📈 Дашборд", callback_data="dashboard")
        auth_btn = types.InlineKeyboardButton("⚙️ Авторизованные аккаунты", callback_data="settings")
        markup = types.InlineKeyboardMarkup()
        markup.add(daily_btn, dashboard_btn)
        markup.row(auth_btn)

        await bot.send_photo(
            message.chat.id,
            open("./files/telegram_welcome.png", "rb"),
            caption=telegram_messages.welcome_message(message.chat.first_name),
            parse_mode="HTML",
            reply_markup=markup,
        )

    @dp.callback_query_handler(lambda call: call.data == "daily")
    async def callback_daily(call: types.CallbackQuery, state: FSMContext) -> None:
        await bot.answer_callback_query(call.id)

        auth_btn = types.InlineKeyboardButton(text="⚙️ Авторизовать аккаунт", callback_data="oauth")
        main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
        markup = types.InlineKeyboardMarkup().row(auth_btn, main_btn)

        await bot.edit_message_caption(
            call.message.chat.id,
            call.message.message_id,
            caption=telegram_messages.daily_msg,
            parse_mode="HTML",
            reply_markup=markup,
        )

    @dp.callback_query_handler(lambda call: call.data == "oauth")
    async def account(call: types.CallbackQuery, state: FSMContext) -> None:
        """Add account to database /add_account"""
        await bot.answer_callback_query(call.id)

        btn_login = types.InlineKeyboardButton("🌐 Авторизоваться", url=URL_OAUTH)
        markup_login = types.InlineKeyboardMarkup().add(btn_login)

        await bot.edit_message_caption(
            call.message.chat.id, call.message.message_id, caption=telegram_messages.auth_msg, reply_markup=markup_login
        )
        await Form.get_token.set()

    @dp.message_handler(state=Form.get_token)
    async def verify_code(message: types.message.Message, state: FSMContext) -> None:
        async with state.proxy() as data:
            data["get_token"] = message.text
            await state.finish()

        token = await verify_direct(message.text)
        if token:
            login = await get_login_direct(token)
            async with state.proxy() as data:
                data["login"] = login
                data["token"] = token
                await state.finish()
            await add_token_direct(message.chat.id, token, login)
            await bot.send_message(
                message.chat.id, f"☑️ Аккаунт <b>{login}</b> успешно авторизован!", parse_mode="HTML"
            )

            await aleks_bot.send_message(90785234, telegram_messages.send_nots_token(message, login), parse_mode="HTML")
            await set_goals(message, token, state)
        else:
            await bot.send_message(message.chat.id, "Введен неверный код. Попробуйте добавить аккаунт снова /start.")

    async def manual_goals(message: Message) -> None:
        await bot.send_message(message.chat.id, telegram_messages.goals_manual, parse_mode="HTML")
        await Form.get_goal_id_manual.set()

    async def set_goals(message: Message, token: str, state: FSMContext) -> None:
        """Ask user to set goal id number"""
        await bot.send_message(message.chat.id, telegram_messages.goals_welcome)
        await bot.send_message(message.chat.id, telegram_messages.goals_welcome2, parse_mode="HTML")
        goals = await service.yandex.arr_goals(token)
        if goals == "No campaigns":
            await bot.send_message(message.chat.id, telegram_messages.goals_no_campaigns)
            await manual_goals(message)
        elif goals == "Error | Key Error":
            await bot.send_message(
                message.chat.id,
                "Получить список целей не удалось.",
            )
            await manual_goals(message)

        else:
            async with state.proxy() as data:
                data["goals"] = [str(goal["goal_id"]) for goal in goals]
                await state.finish()

            arr_str = ""
            for goal in goals:
                arr_str += f"<b>{goal['goal_id']}</b> - {goal['name']}\n"
                if len(arr_str) > 3000:
                    await bot.send_message(message.chat.id, arr_str, parse_mode="HTML", disable_web_page_preview=True)
                    arr_str = ""

            await Form.get_goal_id.set()

    @dp.message_handler(state=Form.get_goal_id_manual)
    async def get_goal_id_manual(message: Message, state: FSMContext) -> None:
        """Manual add goal"""
        if message.text == "/start":
            await send_welcome(message)
        try:
            int(message.text)
        except ValueError:
            await bot.send_message(message.chat.id, telegram_messages.goals_not_number)
            await manual_goals(message)
        else:
            async with state.proxy() as data:
                data["get_goal_id"] = message.text
                login = data["login"]
                await state.finish()
                await add_goal_id_direct(message.chat.id, message.text, login)
                await bot.send_message(
                    message.chat.id, telegram_messages.goals_success(message.text, login), parse_mode="HTML"
                )

    @dp.message_handler(state=Form.get_goal_id)
    async def get_goal_id(message: Message, state: FSMContext) -> None:
        """Auto add goal"""
        if message.text == "/start":
            await send_welcome(message)
        else:
            async with state.proxy() as data:
                data["get_goal_id"] = message.text
                login = data["login"]
                goals = data["goals"]
                token = data["token"]
                await state.finish()
            if str(message.text) in goals:
                await add_goal_id_direct(message.chat.id, message.text, login)
                yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
                btn = types.InlineKeyboardButton(f"📅 Сводка за {yesterday}", callback_data="overview")
                markup = types.InlineKeyboardMarkup().add(btn)
                await bot.send_message(
                    message.chat.id,
                    telegram_messages.goals_success(message.text, login),
                    parse_mode="HTML",
                    reply_markup=markup,
                )
            else:
                await bot.send_message(message.chat.id, "️️⚠️ Не существует такой цели.")
                await set_goals(message, token, state)

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

    @dp.callback_query_handler(lambda call: call.data == "overview")
    async def callback_overview(call: types.CallbackQuery, state: FSMContext) -> None:
        await bot.answer_callback_query(call.id)
        async with state.proxy() as data:
            login = data["login"]
            token = data["token"]
            goal = data["get_goal_id"]
            await state.finish()
        mg = service.yandex.get_report_tg(token, goal, login)
        await telegram_daily(mg, call.message.chat.id)

    executor.start_polling(dispatcher=dp)


async def telegram_daily(mg: tuple, tg_id: int) -> None:
    """Send telegram daily"""
    tg_token = cfg.config.telegram.tg_token
    tg_nots_token = cfg.config.telegram.tg_nots_token
    bot = Bot(tg_token)
    aleks_bot = Bot(tg_nots_token)
    for message in mg:
        await bot.send_message(tg_id, message, parse_mode="HTML")
    await aleks_bot.send_message(
        90785234,
        f"""
<b>Juice.Direct | {tg_id} отправлено!</b>""",
        parse_mode="HTML",
    )
    session = await bot.get_session()
    session_tg = await aleks_bot.get_session()
    await session.close()
    await session_tg.close()
