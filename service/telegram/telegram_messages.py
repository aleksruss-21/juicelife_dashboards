from aiogram.types.message import Message


def welcome_message(name: str) -> str:
    """First message to user"""
    msg = f"""
Привет, {name}! 👋

Приветствует тебя бот-помощник по работе с рекламными кампаниями.

<b> ▫️ Что сейчас умеет бот? </b>
- присылать ежедневную сводку результатов работы кампаний в Яндекс.Директ;
- собирать персональный дашборд по работе в Яндекс.Директ"""
    return msg


def send_nots_new_user(message: Message) -> str:
    """New user notification to aleks bot"""
    msg = f"""
        <b>Juice.Direct | Новый подписчик!</b>

        id: {message.chat.id}
        username: @{message.chat.username}
        Имя: {message.chat.first_name}
        Фамилия: {message.chat.last_name}"""

    return msg


def send_nots_token(message: Message, login: str) -> str:
    msg = f"""
<b>Juice.Direct | Успешная авторизация!</b>

username: @{message.chat.username}
login: {login}"""
    return msg


def goals_success(goal_id: str, login: str) -> str:
    msg = f"☑️ Цель <b>№{goal_id}</b> для аккаунта <b>{login}</b> успешно добавлена!"
    return msg


daily_msg = (
    "Получайте ежедневную сводку работы РК в Яндекс.Директ. "
    "Авторизуйте аккаунт, чтобы начать получать сообщения ежедневно: 👇"
)
auth_msg = "Чтобы авторизовать аккаунт, перейдите по ссылке и пришлите код в сообщении."
goals_welcome = "Для отслеживания числа конверский, требуется ввести ID цели из Яндекс.Метрики. Введите ID цели:"
goals_welcome2 = "<i>🤖 Пробую получить список целей самостоятельно...</i>"
goals_not_number = "⚠️ ID цели должно быть числом. Пожалуйста, попробуйте заново."
goals_no_campaigns = (
    "⚠️ За последний период в данном аккаунте не было рекламных кампаний. " "Пожалуйста, добавьте цели вручную."
)
goals_manual = (
    "Введите ID цели самостоятельно. ID цели можно найти в Яндекс.Метрике.\n\n"
    "<i>Если возникли проблемы, напишите @aleksruss </i>"
)
