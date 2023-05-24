from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types.message import Message

from datetime import datetime, timedelta

from telegram_bot import bot, aleks_bot, Form
from service.yandex.yandex_main import get_report_tg, arr_goals
from service.yandex.yandex_queries import (
    URL_OAUTH,
    verify_direct,
    get_login_direct,
    get_agency_logins,
)
from telegram_bot.tg_storage.tg_app_database import (
    add_user_tg,
    add_token_direct,
    add_goal_id_direct,
)
from telegram_bot.tg_service import tg_messages
from telegram_bot.tg_service.tg_daily import telegram_daily


async def send_welcome(message: Message) -> None:
    """Welcome message after /start commands"""
    if await add_user_tg(message) is True:
        await aleks_bot.send_message(90785234, tg_messages.send_nots_new_user(message), parse_mode="HTML")

    daily_btn = types.InlineKeyboardButton("📅 Ежедневная сводка", callback_data="daily")
    # dashboard_btn = types.InlineKeyboardButton("📈 Дашборд", callback_data="dashboard")
    auth_btn = types.InlineKeyboardButton("⚙️ Авторизованные аккаунты", callback_data="settings")
    support_btn = types.InlineKeyboardButton("🧔🏽 Остались вопросы?", url="t.me/aleksruss")
    markup = types.InlineKeyboardMarkup()
    # markup.add(daily_btn, dashboard_btn)
    markup.add(daily_btn)
    markup.add(auth_btn)
    markup.add(support_btn)

    with open("telegram_bot/tg_files/telegram_welcome.png", "rb") as file:
        await bot.send_photo(
            message.chat.id,
            file,
            caption=tg_messages.welcome_message(message.chat.first_name),
            parse_mode="HTML",
            reply_markup=markup,
        )


async def callback_daily(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback for 'Ежедневная сводка' button"""
    await bot.answer_callback_query(call.id)

    auth_btn = types.InlineKeyboardButton(text="⚙️ Авторизовать аккаунт", callback_data="oauth")
    main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
    markup = types.InlineKeyboardMarkup().row(auth_btn, main_btn)

    await bot.edit_message_caption(
        call.message.chat.id,
        call.message.message_id,
        caption=tg_messages.daily_msg,
        parse_mode="HTML",
        reply_markup=markup,
    )


async def callback_main_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback to go to main menu"""
    await bot.answer_callback_query(call.id)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await send_welcome(call.message)


async def callback_add_account(call: types.CallbackQuery, state: FSMContext) -> None:
    """Add account to database /add_account"""
    await bot.answer_callback_query(call.id)

    btn_login = types.InlineKeyboardButton("🌐 Авторизоваться", url=URL_OAUTH)
    markup_login = types.InlineKeyboardMarkup().add(btn_login)

    await bot.edit_message_caption(
        call.message.chat.id,
        call.message.message_id,
        caption=tg_messages.auth_msg,
        parse_mode="HTML",
        reply_markup=markup_login,
    )
    await Form.get_token.set()


async def form_verify_code_get_login(message: Message, state: FSMContext) -> None:
    """Verify code part1."""
    async with state.proxy() as data:
        data["get_token"] = message.text
        await state.finish()

    token = await verify_direct(message.text)
    if token:
        login, account_type = await get_login_direct(token)
        if login == "Error":
            main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
            markup = types.InlineKeyboardMarkup().add(main_btn)
            await bot.send_message(
                message.chat.id,
                "⚠️ Произошла непредвиденная ошибка️",
                reply_markup=markup,
            )
        else:
            async with state.proxy() as data:
                data["login"] = login
                data["token"] = token
                data["is_agency"] = False
            if account_type == "AGENCY":
                async with state.proxy() as data:
                    data["is_agency"] = True
                logins = await get_agency_logins(token)
                await logins_agency(message, logins)
            else:
                await form_verify_check(message, state)
    else:
        await bot.send_message(
            message.chat.id,
            "Введен неверный код. Попробуйте добавить аккаунт снова /start.",
        )


async def form_verify_check(message: Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        token = data["token"]
        is_agency = data["is_agency"]
        if is_agency is True:
            login = data["agency_login"]
        else:
            login = data["login"]
    await add_token_direct(message.chat.id, token, login, is_agency)
    await bot.send_message(
        message.chat.id,
        f"☑️ Аккаунт <b>{login}</b> успешно авторизован!",
        parse_mode="HTML",
    )

    await aleks_bot.send_message(90785234, tg_messages.send_nots_token(message, login), parse_mode="HTML")
    await set_goals(message, state)


async def set_goals(message: Message, state: FSMContext) -> None:
    """Ask user to set goal id number"""
    async with state.proxy() as data:
        token = data["token"]
        is_agency = data["is_agency"]
        if is_agency is True:
            login = data["agency_login"]
        else:
            login = data["login"]
    await bot.send_message(message.chat.id, tg_messages.goals_welcome)
    await bot.send_message(message.chat.id, tg_messages.goals_welcome2, parse_mode="HTML")

    goals = await arr_goals(token, login)
    if goals == "No campaigns":
        await bot.send_message(message.chat.id, tg_messages.goals_no_campaigns)
        async with state.proxy() as data:
            data["get_goal_id"] = message.text
            await state.finish()
        yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
        btn = types.InlineKeyboardButton(f"📅 Сводка за {yesterday}", callback_data="overview")
        markup = types.InlineKeyboardMarkup().add(btn)
        await bot.send_message(
            message.chat.id,
            tg_messages.overview_without_goal,
            reply_markup=markup,
        )
    elif goals == "Error | Key Error":
        await bot.send_message(
            message.chat.id,
            "Получить список целей не удалось.",
        )
        async with state.proxy() as data:
            data["get_goal_id"] = message.text
            login = data["login"]
            await state.finish()
        yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
        btn = types.InlineKeyboardButton(f"📅 Сводка за {yesterday}", callback_data="overview")
        markup = types.InlineKeyboardMarkup().add(btn)
        await bot.send_message(
            message.chat.id,
            tg_messages.goals_success(message.text, login),
            parse_mode="HTML",
            reply_markup=markup,
        )
    elif goals == "No goals":
        await bot.send_message(message.chat.id, tg_messages.goals_empty)
        yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
        btn = types.InlineKeyboardButton(f"📅 Сводка за {yesterday}", callback_data="overview")
        markup = types.InlineKeyboardMarkup().add(btn)
        await bot.send_message(
            message.chat.id,
            tg_messages.overview_without_goal,
            reply_markup=markup,
        )

    else:
        async with state.proxy() as data:
            data["goals"] = [str(goal["goal_id"]) for goal in goals]

        arr_str = ""
        for goal in goals:
            arr_str += f"<b>{goal['goal_id']}</b> - {goal['name']}\n"
            if len(arr_str) > 3000:
                await bot.send_message(
                    message.chat.id,
                    arr_str,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
                arr_str = ""
        await bot.send_message(message.chat.id, arr_str, parse_mode="HTML", disable_web_page_preview=True)

        await Form.get_goal_id.set()


async def form_get_goal_id(message: Message, state: FSMContext) -> None:
    """Auto add goal"""
    if message.text == "/start":
        await send_welcome(message)
    else:
        async with state.proxy() as data:
            data["get_goal_id"] = message.text
            is_agency = data["is_agency"]
            goals = data["goals"]
            if is_agency is True:
                login = data["agency_login"]
            else:
                login = data["login"]
        if str(message.text) in goals:
            await add_goal_id_direct(message.chat.id, message.text, login)
            async with state.proxy() as data:
                data["get_goal_id"] = message.text
            yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
            btn = types.InlineKeyboardButton(f"📅 Сводка за {yesterday}", callback_data="overview")
            markup = types.InlineKeyboardMarkup().add(btn)
            await bot.send_message(
                message.chat.id,
                tg_messages.goals_success(message.text, login),
                parse_mode="HTML",
                reply_markup=markup,
            )
        else:
            await bot.send_message(message.chat.id, "️️⚠️ Не существует такой цели.")
            await set_goals(message, state)


async def logins_agency(message: Message, logins: list):
    """Send message to get agency's login"""
    markup = types.InlineKeyboardMarkup()

    for login in logins:
        btn = types.InlineKeyboardButton(text=login, callback_data=f"login_agency|{login}")
        markup.add(btn)

    await bot.send_message(
        message.chat.id,
        "Выберите аккаунт, который хотите добавить:",
        reply_markup=markup,
    )


async def callback_agency_logins(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback for getting agency's account"""
    await bot.answer_callback_query(call.id)
    login = call.data.split("|")[1]
    async with state.proxy() as data:
        data["agency_login"] = login
    await form_verify_check(call.message, state)


async def callback_overview(call: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.message.chat.id, "<i>🤖 Загружаю данные...</i>", parse_mode="HTML")
    async with state.proxy() as data:
        token = data["token"]
        goal = data.get("get_goal_id")
        is_agency = data["is_agency"]
        if is_agency is True:
            login = data["agency_login"]
        else:
            login = data["login"]
        await state.finish()

    mg = get_report_tg(token, goal, login, is_agency)
    await telegram_daily(mg, call.message.chat.id, login)
