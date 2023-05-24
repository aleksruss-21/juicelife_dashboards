import cfg
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

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
    agency_login = State()
    goals = State()
    token = State()
    is_agency = State()
    # current_goal = State()
