from db.db import Database
from config import *

from aiogram import Bot, Dispatcher, types, F

db = Database()

bot = Bot(token=ORDERS_TOKEN, parse_mode="HTML")
dp = Dispatcher()

throttled_rate = 2


async def new_order(string):
    await bot.send_message(admins_id[0], string)
    await bot.send_message(others[0], string)
    

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    dp.run_polling(bot)