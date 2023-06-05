from telegram_bot import dp, Form
from telegram_bot.tg_service.tg_menu_main import (
    send_welcome,
    callback_daily,
    callback_main_menu,
    callback_add_account,
    form_verify_code_get_login,
    form_get_goal_id,
    callback_overview,
    callback_agency_logins,
)

from telegram_bot.tg_service.tg_menu_dashboard import (
    callback_dashboard,
    callback_dashboard_promo,
    callback_dashboard_send_tariffs,
)

from telegram_bot.tg_service.tg_menu_settings import (
    callback_verified_accounts,
    callback_delete_acc,
    callback_back_main,
    callback_ask_delete_acc,
)

from aiogram import executor

dp.register_message_handler(send_welcome, commands=["start"])

dp.register_message_handler(form_verify_code_get_login, state=Form.get_token)
dp.register_message_handler(form_get_goal_id, state=Form.get_goal_id)


dp.register_callback_query_handler(callback_daily, lambda call: call.data == "daily", state='*')
dp.register_callback_query_handler(callback_dashboard, lambda call: call.data == "dashboard", state='*')
dp.register_callback_query_handler(callback_dashboard_send_tariffs, lambda call: call.data == "dashboard_tariffs", state='*')
dp.register_callback_query_handler(callback_dashboard_promo, lambda call: call.data == "dashboard_promo", state='*')
dp.register_callback_query_handler(callback_main_menu, lambda call: call.data == "main", state='*')
dp.register_callback_query_handler(callback_add_account, lambda call: call.data == "oauth", state='*')
dp.register_callback_query_handler(callback_agency_logins, lambda call: call.data.startswith("login_agency"), state='*')


dp.register_callback_query_handler(callback_verified_accounts, lambda call: call.data == "settings", state='*')

dp.register_callback_query_handler(callback_ask_delete_acc, lambda call: call.data.startswith("acc_info"), state='*')
dp.register_callback_query_handler(callback_delete_acc, lambda call: call.data.startswith("delete"), state='*')
dp.register_callback_query_handler(callback_back_main, lambda call: call.data == "back_main", state='*')

dp.register_callback_query_handler(callback_overview, lambda call: call.data == "overview", state='*')

executor.start_polling(dispatcher=dp)
