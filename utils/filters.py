from aiogram import Router
from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.types.chat import Chat
from typing import Union
from db.db import Database
from db.objects import *

from keyboards.markups import check_subscribe_keyboard

db = Database()

class AdminCheck(BaseFilter):
    admins: list

    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:
        return message.from_user.id in self.admins


class StandartCheck(BaseFilter):

    async def __call__(self, message: Union[Message, CallbackQuery]) -> bool:
        return True


class ChatType(BaseFilter):
    chat_type: str = "private"

    async def __call__(self, message: Message , event_chat: Chat) -> bool:
        if event_chat:
            return event_chat.type == "private"
        else:
            return False


class GroupType(BaseFilter):
    chat_type: str = "supergroup"

    async def __call__(self, message: Message , event_chat: Chat) -> bool:
        if event_chat:
            return event_chat.type in ["group", "supergroup"]
        else:
            return False


class BannedType(BaseFilter):
     async def __call__(self, message: Message , event_chat: Chat) -> bool:
        if event_chat:
            return str(message.from_user.id) not in [i.user_id for i in db.s.query(Banned_user).all()]
        else:
            return False


GroupRouter = Router()
GroupRouter.callback_query.bind_filter(GroupType)
GroupRouter.message.bind_filter(GroupType)

AdminRouter = Router()
AdminRouter.callback_query.bind_filter(AdminCheck)
AdminRouter.message.bind_filter(AdminCheck)
AdminRouter.callback_query.bind_filter(ChatType)
AdminRouter.message.bind_filter(ChatType)

OtherRouter = Router()
OtherRouter.callback_query.bind_filter(StandartCheck)
OtherRouter.message.bind_filter(StandartCheck)
OtherRouter.callback_query.bind_filter(ChatType)
OtherRouter.message.bind_filter(ChatType)
OtherRouter.callback_query.bind_filter(BannedType)
OtherRouter.message.bind_filter(BannedType)

