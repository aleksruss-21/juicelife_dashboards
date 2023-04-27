from aiogram import types
from aiogram.dispatcher import FSMContext

from telegram_bot import bot
from telegram_bot.tg_storage.tg_app_database import (
    get_users_accounts,
    delete_dashboard_token,
)
from telegram_bot.tg_service import tg_messages


async def callback_verified_accounts(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    """Send accounts of user with inline buttons"""
    await bot.answer_callback_query(call.id)
    markup_logins = types.InlineKeyboardMarkup()
    for login in await get_users_accounts(call.message):
        btn = types.InlineKeyboardButton(login[0], callback_data=f"acc_info|{login[0]}")
        markup_logins.add(btn)

    auth_btn = types.InlineKeyboardButton(
        text="➕ Добавить аккаунт", callback_data="oauth"
    )
    main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
    markup_logins.add(auth_btn, main_btn)

    await bot.edit_message_caption(
        call.message.chat.id,
        call.message.message_id,
        caption=tg_messages.settings_list_accounts,
        parse_mode="HTML",
        reply_markup=markup_logins,
    )


async def callback_ask_delete_acc(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback of delete button. Asks if user really wants to delete acc"""
    await bot.answer_callback_query(call.id)
    login = call.data.split("|")[1]

    markup = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton("Да", callback_data=f"delete|{login}")
    btn_no = types.InlineKeyboardButton("Отмена", callback_data="back_main")
    markup.row(btn_yes, btn_no)

    await call.message.edit_caption(
        tg_messages.settings_delete_acc(login), parse_mode="HTML", reply_markup=markup
    )
    await state.finish()


async def callback_delete_acc(call: types.CallbackQuery, state: FSMContext) -> None:
    """Delete token for direct account from database"""
    login = call.data.split("|")[1]
    user_id = call.message.chat.id
    await delete_dashboard_token(user_id, login)
    await bot.answer_callback_query(call.id, text="Успешно удалено!")
    await state.finish()
    await callback_verified_accounts(call, state)


async def callback_back_main(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback to cancel delete account"""
    await bot.answer_callback_query(call.id)
    await callback_verified_accounts(call, state)
    await state.finish()
