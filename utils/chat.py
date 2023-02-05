import logging

from aiogram import Bot, Dispatcher

from config import *

bot = Bot(token=INVITE_TOKEN)
dp = Dispatcher()


async def get_invite_link(chat_id, member_limit=1):
    try:
        link = await bot.create_chat_invite_link(chat_id=int(chat_id), member_limit=int(member_limit))
        return link.invite_link
    except:
        link = await bot.create_chat_invite_link(chat_id=int(chat_id), member_limit=int(member_limit))
        return link["invite_link"]


async def ban_user(chat_id, user_id):
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except:
        return False

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=False, on_shutdown=shutdown)