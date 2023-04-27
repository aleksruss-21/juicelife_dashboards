from aiogram import types
from aiogram.dispatcher import FSMContext

from telegram_bot import bot
from telegram_bot.tg_service import tg_messages


async def callback_dashboard(call: types.CallbackQuery, state: FSMContext) -> None:
    """Callback for 'Дашборд' button"""
    await bot.answer_callback_query(call.id)
    with open("telegram_bot/tg_files/telegram_dashboard.png", "rb") as file:
        await call.message.edit_media(types.InputMedia(type="photo", media=file))

    template_btn = types.InlineKeyboardButton(
        text="📊 Пример дашборда",
        url="https://datastudio.google.com/reporting/f4f258cd-9920-4d5b-9594-435c99ca7c8c/page/VHb6C",
    )
    tariff_btn = types.InlineKeyboardButton(
        text="📝 Тарифы", callback_data="dashboard_tariffs"
    )
    promo_btn = types.InlineKeyboardButton(
        text="🎁 Попробовать 7 дней", callback_data="dashboard_promo"
    )
    markup = types.InlineKeyboardMarkup().row(template_btn, tariff_btn)
    markup.add(promo_btn)

    await call.message.edit_caption(
        tg_messages.dashboard_welcome, parse_mode="HTML", reply_markup=markup
    )


async def callback_dashboard_send_tariffs(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    """Callback for 'Дашборд.Тарифы' button"""
    await bot.answer_callback_query(call.id)
    with open("telegram_bot/tg_files/telegram_prices.png", "rb") as file:
        await call.message.edit_media(types.InputMedia(type="photo", media=file))

    main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
    promo_btn = types.InlineKeyboardButton(
        text="🎁 Попробовать 7 дней", callback_data="dashboard_promo"
    )
    markup = types.InlineKeyboardMarkup().add(main_btn, promo_btn)

    await call.message.edit_caption(
        tg_messages.dashboard_tariffs, parse_mode="HTML", reply_markup=markup
    )


async def callback_dashboard_promo(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    """Callback for 'Дашборд.Попробовать 7 дней' button"""
    await bot.answer_callback_query(call.id)
    with open("telegram_bot/tg_files/telegram_dashboard.png", "rb") as file:
        await call.message.edit_media(types.InputMedia(type="photo", media=file))

    auth_btn = types.InlineKeyboardButton(
        text="⚙️ Авторизовать аккаунт", callback_data="oauth"
    )
    main_btn = types.InlineKeyboardButton(text="📂 Главное меню", callback_data="main")
    support_btn = types.InlineKeyboardButton(
        text="🧔🏽 Попробовать", url="t.me/aleksruss"
    )
    markup = types.InlineKeyboardMarkup().row(auth_btn, main_btn)
    markup.add(support_btn)
    await call.message.edit_caption(
        tg_messages.dashboard_promo, parse_mode="HTML", reply_markup=markup
    )
