import datetime
import logging
import os
import random
import requests
from pyqiwip2p import QiwiP2P
from typing import Union
import asyncio

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.exceptions import (TelegramAPIError, TelegramBadRequest, TelegramForbiddenError)
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import FSInputFile
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.methods.forward_message import ForwardMessage
from aiogram.dispatcher.filters.command import Command, CommandObject

from config import *
from keyboards import markups
from db.db import Database
from utils.utils import *
from utils import chat
from keyboards import items_markups as im
import traceback as tb
from keyboards import admin_markups as am
from utils.filters import AdminRouter, OtherRouter, ChatType, GroupRouter, BannedType
from db.objects import *
from aiogram.dispatcher.filters import BaseFilter

from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.types.chat_member_banned import ChatMemberBanned
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def check_subscribe(chat_member):
    # print(chat_member)
        if chat_member not in [ChatMemberLeft, ChatMemberBanned]:
            if chat_member.status != "left":
                return True
        return False


class SubscribeCheck(BaseFilter):
    async def __call__(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                return True
        except:
            keyboard = markups.check_subscribe_keyboard()
            if isinstance(message, types.Message):
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
                return False

        keyboard = markups.check_subscribe_keyboard()
        if isinstance(message, types.Message):
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
            return False


bot = Bot(token=TOKEN, parse_mode="HTML")
bot2 = Bot(token=TOKEN2, parse_mode="HTML")

dp = Router()
GlobalRouter = Dispatcher()

db = Database()

dp.message.bind_filter(ChatType)
dp.callback_query.bind_filter(ChatType)

dp.message.bind_filter(BannedType)
dp.callback_query.bind_filter(BannedType)

GlobalRouter.include_router(dp)
GlobalRouter.include_router(GroupRouter)
GlobalRouter.include_router(AdminRouter)
GlobalRouter.include_router(OtherRouter)



p2p = ''

bot_name = ''
bot_id = ''

logger = logging.getLogger(__name__)

start_blacklist = []

blacklist = [] + start_blacklist[::]

try:
    async def anti_flood(*args, **kwargs):
            pass

    async def new_user(username, user_id):
        string = f'<b>Новый пользователь!\n'\
                 f'Username: @{username}\n'\
                 f'UserId: {user_id}</b>'
        await bot2.send_message(admins_id[0], string)


    @AdminRouter.message(admins=admins_id, text="test")
    async def test(message: types.Message):
        # user_id = 1449391825
        # user = db.get_user(user_id)
        # user.referal = 330323911
        # db.s.commit()
        years = db.s.query(Item).filter(Item.subcategory == "1").all() + db.s.query(Item).filter(Item.subcategory == "5").all()
        oges = db.s.query(Item).filter(Item.subcategory == "2").all()
        halfyers = db.s.query(Item).filter(Item.subcategory == "168").all()

        for course in years:
            course.price = 350
            db.s.commit()
        await message.answer("Готово год")

        for course in halfyers:
            course.price = 450
            db.s.commit()
        await message.answer("Готово огэ")

        for course in oges:
            course.price = 350
            db.s.commit()
        await message.answer("Готово пол")


    def check_blacklist(function_to_decorate):
            async def func(message, **kwargs):
                if message.from_user.id not in blacklist:
                    await function_to_decorate(message)
                else:
                    pass
            return func

    async def check_subscribe(chat_member):
    # print(chat_member)
        if chat_member not in [ChatMemberLeft, ChatMemberBanned]:
            if chat_member.status != "left":
                return True
        return False

    # Менеджер
    @GlobalRouter.startup()
    async def startup():
        global bot_name, bot_id
        bot_name = (await bot.me()).username
        bot_id = (await bot.me()).id
        print(f'"@{bot_name}" запущен')


    @AdminRouter.message(admins=admins_id, text="Добавить кошелек")
    async def set_add_wallet(message: types.Message, state: FSMContext):
        await state.set_state(EDIT_PANEL.ADD_WALLET_NUM)
        markup = am.cancel_keyboard()
        mess = await message.answer("Впишите номер телефона кошелка", reply_markup=markup)
        await state.update_data(mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_WALLET_NUM)
    async def set_add_wallet_num(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        await mess.delete()
        await state.set_state(EDIT_PANEL.ADD_WALLET_P2P)
        markup = am.cancel_keyboard()
        mess = await message.answer("Впишите p2p ключ", reply_markup=markup)
        await state.update_data(mess=mess, num=message.text)

    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_WALLET_P2P)
    async def set_add_wallet_p2p(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        await mess.delete()
        markup = am.cancel_keyboard()
        await state.set_state(EDIT_PANEL.ADD_WALLET_API)
        mess = await message.answer("Впишите api ключ", reply_markup=markup)
        await state.update_data(mess=mess, p2p=message.text)

    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_WALLET_API)
    async def add_wallet(message: types.Message, state: FSMContext):
        data = await state.get_data()
        num = data.get("num")
        p2p = data.get("p2p")
        mess = data.get("mess")
        await mess.delete()
        api = message.text

        if await isgood_qiwi_wallet(api):
            mess = await message.answer("Загрузка...")
            db.s.add(Wallet(number=num, p2p_key=p2p, api_key=api))
            await message.answer("Готово")
            await mess.delete()
        else:
            await message.answer("Невалидный токен. Отмена")

        await state.clear()


    @AdminRouter.message(admins=admins_id, text="Удалить кошелек")
    async def set_del_wallet(message: types.Message, state: FSMContext):
        await state.set_state(EDIT_PANEL.DEL_WALLET)
        wallets = [f"<code>{i.number}</code>" for i in db.get_wallets()]
        text = '\n'.join(wallets)
        markup = am.cancel_keyboard()
        mess = await message.answer(f"Впишите номер кошелька для удаления:\n\n{text}", reply_markup=markup)
        await state.update_data(mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.DEL_WALLET)
    async def del_wallet(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        await mess.delete()
        wallet = db.get_wallet(message.text)
        if wallet:
            db.s.delete(wallet)
            db.s.commit()
            await message.answer("Готово")
        else:
            await message.answer("Кошелек не найден")
        await state.clear()


    @AdminRouter.message(admins=admins_id, text="Проверить все токены")
    async def check_tokens(message: types.Message):
        mess = await message.answer("Загрузка...")
        banned = []
        good = []
        generalBalance = 0


        for wallet in db.get_wallets():

            if await isgood_qiwi_wallet(wallet.api_key):
                balance = await get_qiwi_balance(wallet.number, wallet.api_key)
                
                good.append(f"<code>{wallet.number if wallet.isgood else wallet.number + '<i>(разбанен)</i>'}</code> - <b>{balance} ₽</b>")
                wallet.isgood = True
                db.s.commit()
                generalBalance += balance
            else:
                banned.append(f"<code>{wallet.number}</code>{'(<i>(забанен)</i>)' if wallet.isgood else ''}")
                wallet.isgood = False
                db.s.commit()
                continue
            
        str_banned = '\n'.join(banned)
        str_good = '\n'.join(good)

        await mess.delete()
        await message.answer(f"Забанено {len(banned)} кошельков\n\n{str_banned}")
        await message.answer(f"Хороших кошельков - {len(good)}\n\n{str_good}")
        await message.answer(f"<i>Общий баланс:</i> <b>{generalBalance} ₽</b>")


    @AdminRouter.message(admins=admins_id, text="👛Кошельки")
    async def wallet_menu(message: types.Message, state: FSMContext):
        keyboard = am.wallet_keyboard()
        await message.answer("👛Кошельки", reply_markup=keyboard)
        await message.delete()

    # Админка
    @AdminRouter.message(admins=admins_id, text="Задать общий процент для рефералов")
    async def set_all_referal_procent(message: types.Message, state: FSMContext):
        service = db.get_service_object("referal_procent")
        keyboard = am.cancel_keyboard()
        mess = await message.answer(f"<b>Текущий процент для рефералов: {float(service.text) * 100} % </b>\nВведите новый.", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_ALL_REFERAL_PROCENT)
        await state.update_data(service=service, mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_ALL_REFERAL_PROCENT)
    async def set_referal_procent(message: types.Message, state: FSMContext):
        try:
            if message.text.isdigit():
                data = await state.get_data()
                service = data.get("service")
                mess = data.get("mess")
                await mess.edit_text("Загрузка...")
                await state.clear()
                service.text = int(message.text) / 100
                db.s.commit()
                for i in db.get_users():
                    try:
                        i.ref_procent = service.text
                        db.s.commit()
                    except:
                        pass
                await message.delete()
                await mess.edit_text('Изменено', reply_markup=None)
            else:
                await message.answer("Ошибка")
        except:
            await message.answer("Ошибка")


    @AdminRouter.message(admins=admins_id, text="Сделать роллбэк")
    async def Session_rollback(message: types.Message, state: FSMContext):
        try:
            db.s.rollback()
            await message.answer('Готово')
        except:
            await message.answer('Ошибка')

            
    @AdminRouter.message(admins=top_up_ids, text="Получить данные о пользователе")
    async def set_get_user_lc(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            mess = await message.answer('Введите user_id пользователя', reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_USER_LC)
            await state.update_data(mess=mess)
        
        except:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, text="Отправить рассылку")
    async def set_mass_message(message: types.Message, state: FSMContext):
        try:
            mess = await message.answer("Очистка данных от предыдущей рассылки...")
            messages = db.get_mass_messages()
            for i in messages[::]:
                try:
                    db.s.delete(i)
                    db.s.commit()
                except:
                    pass
            await mess.delete()
            keyboard = am.cancel_add_item_photo_keyboard()
            mess = await message.answer("Отправьте фотографию для рассылки\n\n<b>либо перешлите сообщение из канала\nРассылка начнеться сразу!</b>", reply_markup=keyboard)
            await state.set_state(MASS_MESSAGE.SEND_MASS_MESSAGE_PHOTO)
            await state.update_data(mess=mess)
        
        except Exception:
            await message.answer('Ошибка')

    @AdminRouter.callback_query(admins=adding_ids, text="skip_photo", state=MASS_MESSAGE.SEND_MASS_MESSAGE_PHOTO)
    async def skip_photo_sp(callback: types.CallbackQuery, state: FSMContext):
        try:
            data = await state.get_data()
            mess = data.get("mess")

            photo = None

            keyboard = am.cancel_keyboard()
            await mess.edit_text("Введите текст для рассылки", reply_markup=keyboard)
            await state.set_state(MASS_MESSAGE.SEND_MASS_MESSAGE)

            await state.update_data(mess=mess, photo=photo)
        except:
            await callback.message.answer('Ошибка')

        
    @AdminRouter.message(admins=admins_id, state=MASS_MESSAGE.SEND_MASS_MESSAGE_PHOTO, content_types=["photo"])
    async def get_mass_messages_photo(message: types.Message, state: FSMContext):
        try:
            if not message.forward_from_chat:
                data = await state.get_data()
                mess = data.get("mess")

                photo = message.photo[0].file_id

                await message.delete()

                keyboard = am.cancel_keyboard()
                await mess.edit_text("Введите текст для рассылки", reply_markup=keyboard)
                await state.set_state(MASS_MESSAGE.SEND_MASS_MESSAGE)

                await state.update_data(mess=mess, photo=photo)
            else:
                k = 0
                mess = await message.answer(f'Обработка...\nОтправлено "{k}" пользователям')
                await state.clear()

                users = db.get_users()
                for user in users:
                    try:
                        mess1 = await bot.forward_message(chat_id=user.user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                        db.s.add(Mass_Message(user_id=user.user_id, message_id=mess1.message_id))
                        db.s.commit()
                        k += 1
                        await mess.edit_text(text=f'Обработка...\nОтправлено "{k}" пользователям')
                        await asyncio.sleep(0.5)
                    except Exception:
                        pass
                await mess.delete()
                await message.answer(f'Отправленно "{k}" пользователям')
        except:
            await message.answer('Ошибка')

    @AdminRouter.message(admins=admins_id, state=MASS_MESSAGE.SEND_MASS_MESSAGE)
    async def choose_mm(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        photo = data.get("photo")

        await mess.delete()

        keyboard = am.choose_mm_keyboard()
        mess = await message.answer("Посмотреть превью?", reply_markup=keyboard)
        await state.update_data(mess=mess, photo=photo, text=message.html_text)
        await state.set_state(MASS_MESSAGE.CHOOSE)


    @AdminRouter.callback_query(admins=admins_id, text="preview", state=MASS_MESSAGE.CHOOSE)
    async def mass_message_preview(message: types.Message, state: FSMContext):
        keyboard = am.mass_message_keyboard()
        data = await state.get_data()
        text = data.get("text")
        photo = data.get("photo")
        if photo:
            await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, reply_markup=keyboard)
        else:
            await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)



    @AdminRouter.callback_query(admins=admins_id, text="send", state=MASS_MESSAGE.CHOOSE)
    async def mass_message(message: types.Message, state: FSMContext):
        try:
            message = message.message
            data = await state.get_data()
            mess = data.get("mess")
            photo = data.get("photo")

            await mess.delete()

            k = 0
            mess = await message.answer(f'Обработка...\nОтправлено "{k}" пользователям')
            text = data.get("text")
            keyboard = am.mass_message_keyboard()
            await state.clear()

            users = db.get_users()
            # users = [db.get_user(416702541)]
            lost_users = []
            if photo:
                for user in users:
                    try:
                        mess1 = await bot.send_photo(chat_id=user.user_id, photo=photo, caption=text, reply_markup=keyboard)
                        db.s.add(Mass_Message(user_id=user.user_id, message_id=mess1.message_id))
                        db.s.commit()
                        k += 1
                        await mess.edit_text(text=f'Обработка...\nОтправлено "{k}" пользователям')
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        lost_users.append([str(user.user_id), str(e)])
            else:
                for user in users:
                    try:
                        mess1 = await bot.send_message(chat_id=user.user_id, text=text, reply_markup=keyboard)
                        db.s.add(Mass_Message(user_id=user.user_id, message_id=mess1.message_id))
                        db.s.commit()
                        k += 1
                        await mess.edit_text(text=f'Обработка...\nОтправлено "{k}" пользователям')
                        await asyncio.sleep(0.5)
                    except:
                        lost_users.append([str(user.user_id), str(e)])

            # await mess.delete()
            await message.answer(f'Отправленно "{k}" пользователям')
            k = 0
            temp = []
            if lost_users:
                for i in lost_users:
                    temp.append(":\n".join(i))
                    k += 1
                    if k % 10 == 0 and  k != 0:
                        await bot.send_message(chat_id=416702541, text="\n\n".join(temp))
                        temp = []
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, text="Удалить последнюю рассылку")
    async def del_mass_message(message: types.Message):
        try:
            mess = await message.answer("Удаление последней рассылки...")
            messages = db.get_mass_messages()
            for i in messages[::]:
                try:
                    await bot.delete_message(chat_id=i.user_id, message_id=i.message_id)
                except:
                    pass
            await mess.delete()
            await message.answer("Готово!")
        
        except Exception:
            await message.answer('Ошибка')

    @AdminRouter.message(admins=top_up_ids, state=OTHERS_STATES.GET_USER_LC)
    async def get_user_lc(message: types.Message, state: FSMContext):
        # try:
            data = await state.get_data()
            mess = data.get("mess")
            await mess.delete()
            keyboard = am.lc_keyboard(message.text)
            user = db.get_user(int(message.text))
            await message.answer(f"❤️Пользователь: @{user.username}\n💸Количество покупок: <b>{user.purchases_num}</b>\n🔑Личный ID: <b>{user.user_id}</b>\n💰Баланс: <b>{user.balance}₽</b>", reply_markup=keyboard)
            await state.clear()
        
        # except:
        #     await message.answer("Ошибка")


    @AdminRouter.message(admins=top_up_ids, text="Пополнить баланс пользователя")
    async def top_up_user_get_user_id(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            mess = await message.answer('Введите user_id пользователя', reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_USER_ID)
            await state.update_data(mess=mess)
        
        except Exception:
            await message.answer('Ошибка')

    @AdminRouter.message(admins=top_up_ids, state=OTHERS_STATES.GET_USER_ID)
    async def top_up_user_get_money(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            data = await state.get_data()
            mess = data.get("mess")
            await mess.edit_text('Введите сумму пополнения', reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_MONEY)
            await state.update_data(user_id=message.text)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=top_up_ids, state=OTHERS_STATES.GET_MONEY)
    async def top_up_user(message: types.Message, state: FSMContext):
        try:
            try:
                data = await state.get_data()
                mess = data.get("mess")
                user_id, money = data.get("user_id"), message.text

                user = db.get_user(user_id)
                user.balance = user.balance + float(money)
                db.s.commit()
                await mess.edit_text('Добавлено', reply_markup=None)
                await bot.send_message(chat_id=user_id, text=f'Баланс пополнен на <b>"{money}₽"</b>')
            except Exception:
                await message.answer('Ошибка')
            await mess.delete()
            await state.clear()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, text="Список всех пользователй")
    async def users_list(message: types.Message):
        try:
            if message.from_user.id in admins_id:
                users = db.get_users_username()
                await message.answer(f'Всего пользователей: {str(len(users))}')
                result = []
                for i in range(len(users)):
                    result.append(f'@{users[i]}')
                    if i % 100 == 0:
                        await message.answer(' | '.join(result))
                        result = []
                if result:
                    await message.answer(' | '.join(result))
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, text="Получить всю информацию о пополнении")
    async def set_get_payment(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            mess = await message.answer("Отправьте id пополнения", reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_PAYMENT_ID)
            await state.update_data(mess=mess)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=OTHERS_STATES.GET_PAYMENT_ID)
    async def get_payment(message: types.Message, state: FSMContext):
        if message.from_user.id in admins_id:
            try:
                data = await state.get_data()
                mess = data.get("mess")
                if message.text.isdigit():
                    ids = message.text
                    payment = db.get_payment_from_id(ids)
                    await message.answer(f'id: <code>#{payment.id}</code>\nПользователь id: <b>{payment.user_id}</b>\n\nСчет id: <code>{payment.bill_id}</code>\nНомер: <code>{payment.wallet}</code>\n\nСумма: <b>{payment.sum}</b>\nСтатус: <b>{payment.status}</b>\nДата и время: <b>{payment.datetime}</b>')
                else:
                    raise ZeroDivisionError
            except Exception:
                await message.answer('Ошибка')
            await mess.delete()
            await state.clear()


    @AdminRouter.message(admins=top_up_ids, text="Узнать id пользователя по никнейму")
    async def set_get_user_id_from_username(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            mess = await message.answer("Отправьте никнейм", reply_markup=keyboard)
            await state.set_state(EDIT_PANEL.GET_USER_ID_FROM_USERNAME)
            await state.update_data(mess=mess)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=top_up_ids, state=EDIT_PANEL.GET_USER_ID_FROM_USERNAME)
    async def get_user_id_from_username(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            mess = data.get("mess")
            text = message.text
            if "@" in text:
                text = text.replace("@", '')
            user = db.get_user_from_username(text)
            await message.answer(user.user_id)
        except Exception:
            await message.answer('Ошибка')
        await mess.delete()
        await state.clear()


    @AdminRouter.message(admins=admins_id, text="Кол-во пользователей")
    async def users_count(message: types.Message):
        try:
            if message.from_user.id in admins_id:
                users = db.get_users_username()
                await message.answer(f'Всего пользователей: {str(len(users))}')
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, text="Создать ссылку с купоном")
    async def set_add_link_coupon(message: types.Message, state: FSMContext):
        # try:
            await state.set_state(COUPONS_EDIT.ADD_LINK_COUPON_CHOOSE_TYPE)
            item = AddingLinkCoupon
            item.text = db.get_hex()
            keyboard = am.choose_link_coupon_keyboard()
            mess = await message.answer('Выберите тип купона.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()


    @AdminRouter.callback_query(admins=admins_id, state=COUPONS_EDIT.ADD_LINK_COUPON_CHOOSE_TYPE)  
    async def set_add_link_choose_type(callback: types.CallbackQuery, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")

            await mess.delete()

            await state.set_state(COUPONS_EDIT.ADD_LINK_COUPON_PROC)
            item.type = callback.data
            keyboard = am.cancel_keyboard()
            if item.type == "balance":
                mess = await callback.message.answer('Отправьте сумму пополнения, которую дает купон.', reply_markup=keyboard)
            elif item.type == "discount":
                mess = await callback.message.answer('Отправьте процент скидки купона.', reply_markup=keyboard)
            else:
                await callback.message.answer("Неопознанный тип")
                await state.clear()
                return
            await state.update_data(item=item, mess=mess)
        
        except Exception:
            await callback.message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_LINK_COUPON_PROC)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")

            if not message.text.isdigit():
                await mess.edit_text('Значение должно быть числом.')
                return

            await state.set_state(COUPONS_EDIT.ADD_LINK_COUPON_COUNT)
            item.value = int(message.text)
            
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте общее количество использований купона.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_LINK_COUPON_COUNT)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")

            if not message.text.isdigit():
                await mess.edit_text('Значение должно быть числом.')
                return

            await state.set_state(COUPONS_EDIT.ADD_LINK_COUPON_USER_COUNT)
            item.count = int(message.text)
            
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте количество использований купона для одного юзера.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_LINK_COUPON_USER_COUNT)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.ADD_LINK_COUPON_TIME)
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")
            if not message.text.isdigit():
                await mess.edit_text('Значение должно быть числом.')
                return
            item.user_activates = int(message.text)
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте сколько часов купон будет работать.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_LINK_COUPON_TIME)
    async def add_coupon_time(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")
            if not message.text.isdigit():
                keyboard = am.cancel_keyboard()
                await mess.edit_text('Не число', reply_markup=keyboard)
                return
            d = datetime.datetime.today()
            # d = datetime.date(d.year, d.month, d.day)
            t = datetime.timedelta(hours=int(message.text))
            date = d + t
            item.time = date


            # try:
            db.s.add(Linked_Coupon(text=item.text, func=f"{item.type}_{item.value}", count=item.count, date=date, used_users=[], user_activates=item.user_activates))
            db.s.commit()
            await message.answer(f'Ссылка создана.\n\n<code>https://t.me/{bot_name}?start={item.text}</code>')
        
        except:
            await message.answer('Ошибка')
        await state.clear()
        await message.delete()
        await mess.delete()


    @AdminRouter.message(admins=admins_id, text="Удалить ссылку с купоном")
    async def set_del_coupon(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.DEL_LINK_COUPON)
            keyboard = am.delete_link_coupon()
            await message.answer('Введите ссылку для удаления.', reply_markup=keyboard)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.callback_query(admins=admins_id, text="link_coupon_list")
    async def set_del_coupon(callback: types.CallbackQuery):
        coupons = [f"id: <b>#{i.id}</b>\nСсылка: <code>https://t.me/{bot_name}?start={i.text}</code>\nФункция: <b>{i.func}</b>\nОставшиеся кол-во использований: <b>{int(i.count) - len(i.used_users)}</b>\n Дедлайн: <b>{i.date}</b>" for i in db.get_link_coupons()]
        if coupons:
            await callback.message.answer('\n\n'.join(coupons))
        else:
            await callback.message.answer('Купонов нет')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.DEL_LINK_COUPON)
    async def del_coupon(message: types.Message, state: FSMContext):
        try:
            coupon = db.get_coupon("-" + message.text[(20 + len(bot_name)):])
            db.s.delete(coupon)
            db.s.commit()
            await message.answer('Купон удален.')
        
        except:
            await message.answer('Ошибка')
        await state.clear()


    @AdminRouter.message(admins=admins_id, text="Добавить промокод")
    async def set_add_coupon(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.ADD_COUPON_TEXT)
            keyboard = am.cancel_keyboard()
            mess = await message.answer('Отправьте текст промокода.', reply_markup=keyboard)
            item = AddingCoupon
            await state.update_data(item=item, mess=mess)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_COUPON_TEXT)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.ADD_COUPON_PROC)
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")
            item.text = message.text
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте процент скидки промокода.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_COUPON_PROC)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")

            if not message.text.isdigit():
                await mess.edit_text('Значение должно быть числом.')
                return
            await state.set_state(COUPONS_EDIT.ADD_COUPON_COUNT)
            item.proc = int(message.text)
            
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте количество использований промокода.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_COUPON_COUNT)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.ADD_COUPON_TIME)
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")
            if not message.text.isdigit():
                await mess.edit_text('Значение должно быть числом.')
                return
            item.count = int(message.text)
            keyboard = am.cancel_keyboard()
            await mess.edit_text('Отправьте сколько часов промокод будет работать.', reply_markup=keyboard)
            await state.update_data(item=item, mess=mess)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.ADD_COUPON_TIME)
    async def add_coupon_time(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            item = data.get("item")
            mess = data.get("mess")
            if not message.text.isdigit():
                keyboard = am.cancel_keyboard()
                await mess.edit_text('Не число', reply_markup=keyboard)
                return
            d = datetime.datetime.today()
            # d = datetime.date(d.year, d.month, d.day)
            t = datetime.timedelta(hours=int(message.text))
            date = d + t
            item.time = date
            # try:
            db.s.add(Coupon(text=item.text, proc=item.proc, count=item.count, date=date))
            db.s.commit()
            await message.answer('Промокод добавлен.')
        
        except:
            await message.answer('Ошибка')
        await state.clear()
        await message.delete()


    @AdminRouter.message(admins=admins_id, text="Удалить промокод")
    async def set_del_coupon(message: types.Message, state: FSMContext):
        try:
            await state.set_state(COUPONS_EDIT.DEL_COUPON)
            keyboard = am.delete_coupon()
            await message.answer('Введите название промокода для удаления.', reply_markup=keyboard)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.callback_query(admins=admins_id, text="coupon_list")
    async def set_del_coupon(callback: types.CallbackQuery):
        coupons = [f"id: <b>#{i.id}</b>\nНазвание: <code>{i.text}</code>\nСкидка: <b>{i.proc}%</b>\nКоличество использований: <b>{i.count}</b>\n Дедлайн: <b>{i.date}</b>" for i in db.get_coupons()]
        if coupons:
            await callback.message.answer('\n\n'.join(coupons))
        else:
            await callback.message.answer('Промокодов нет')


    @AdminRouter.message(admins=admins_id, state=COUPONS_EDIT.DEL_COUPON)
    async def del_coupon(message: types.Message, state: FSMContext):
        try:
            coupon = db.get_coupon(message.text)
            db.s.delete(coupon)
            db.s.commit()
            await message.answer('Промокод удален.')
        
        except:
            await message.answer('Ошибка')
        await state.clear()



    @AdminRouter.callback_query(admins=adding_ids, text_contains="create_category_")
    async def set_create_category(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.CREATE_CATEGORY)
        await state.update_data(precategory=callback.data[16:])
        await callback.message.answer("Отправьте название новой категории.")


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.CREATE_CATEGORY)
    async def create_category(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            category = Category()
            category.precategory = int(data.get("precategory"))
            category.name = message.text
            category.form = "1"
            db.s.add(category)
            db.s.commit()
            await message.answer("Добавлено")
        
        except:
            await message.answer("Ошибка")
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="rename_category_")
    async def set_rename_category(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.RENAME_CATEGORY)
        id = int(callback.data[16:])
        await callback.message.answer("Отправьте новое название категории.")
        await state.update_data(id=id)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.RENAME_CATEGORY)
    async def rename_category(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            id = data.get("id")
            category = db.get_category(int(id))
            category.name = message.text
            db.s.commit()
            await message.answer("Изменено")
        
        except:
            await message.answer("Ошибка")
        await state.clear()

    @AdminRouter.callback_query(admins=adding_ids, text_contains="get_link_ctg_")
    async def get_link_category(callback: types.CallbackQuery):
        try:
            await callback.message.answer(f"https://t.me/{bot_name}?start=ctg_{callback.data[13:]}")
        except:
            await callback.message.answer("Ошибка")

    @AdminRouter.callback_query(admins=adding_ids, text_contains="get_link_sub_")
    async def get_link_subcategory(callback: types.CallbackQuery):
        try:
            await callback.message.answer(f"https://t.me/{bot_name}?start=sub_{callback.data[13:]}")
        except:
            await callback.message.answer("Ошибка")

    @AdminRouter.callback_query(admins=adding_ids, text_contains="get_link_sj_")
    async def get_link_subject(callback: types.CallbackQuery):
        try:
            await callback.message.answer(f"https://t.me/{bot_name}?start=sj_{callback.data[12:]}")
        except:
            await callback.message.answer("Ошибка")

    @AdminRouter.callback_query(admins=adding_ids, text_contains="get_link_spctg_")
    async def get_link_spcategory(callback: types.CallbackQuery):
        try:
            await callback.message.answer(f"https://t.me/{bot_name}?start=spctg_{callback.data[15:]}")
        except:
            await callback.message.answer("Ошибка")


    @AdminRouter.callback_query(admins=adding_ids, text_contains="get_link_spsub_")
    async def get_link_spsubcategory(callback: types.CallbackQuery):
        try:
            await callback.message.answer(f"https://t.me/{bot_name}?start=spsub_{callback.data[15:]}")
        except:
            await callback.message.answer("Ошибка")




    @AdminRouter.callback_query(admins=adding_ids, text_contains="create_subcategory_")
    async def set_create_subcategory(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.CREATE_SUBCATEGORY)
        await callback.message.answer("Отправьте название новой подкатегории.")
        await state.update_data(category=callback.data[19:])


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.CREATE_SUBCATEGORY)
    async def create_subcategory(message: types.Message, state: FSMContext):
        # try:
            data = await state.get_data()
            precategory, category = data.get("category").split(":")
            subcategory = Subcategory()
            subcategory.name = message.text
            subcategory.category = category
            subcategory.precategory = precategory
            category_item = db.get_category(category)
            db.s.add(subcategory)
            db.s.commit()
            await message.answer("Добавлено")
        
        # except:
        #     await message.answer("Ошибка")
        # await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="rename_subcategory_")
    async def set_rename_subcategory(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.RENAME_SUBCATEGORY)
        id = int(callback.data[19:])
        await callback.message.answer("Отправьте новое название категории.")
        await state.update_data(id=id)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.RENAME_SUBCATEGORY)
    async def rename_subcategory(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            id = data.get("id")
            subcategory = db.get_subcategory(int(id))
            subcategory.name = message.text
            db.s.commit()
            await message.answer("Изменено")
        
        except:
            await message.answer("Ошибка")
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="create_speacial")
    async def set_create_special(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.CREATE_SPECIAL)
        await callback.message.answer("Отправьте название новой спец.подктегории")
        await state.update_data(category=callback.data[19:])


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.CREATE_SPECIAL)
    async def create_special(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            special = SpecialCourse()
            special.name = message.text
            db.s.add(special)
            db.s.commit()
            await message.answer("Добавлено")
        
        except:
            await message.answer("Ошибка")
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="rename_special_")
    async def set_rename_special(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.RENAME_SPECIAL)
        id = int(callback.data[15:])
        await callback.message.answer("Отправьте новое название спец.категории")
        await state.update_data(id=id)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.RENAME_SPECIAL)
    async def rename_special(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            id = data.get("id")
            special = db.get_special_course(int(id))
            special.name = message.text
            db.s.commit()
            await message.answer("Изменено")
        except:
            await message.answer("Ошибка")
        await state.clear()

    
    @AdminRouter.callback_query(admins=admins_id, text_contains='add_special_course_image_', state="*")
    async def set_add_special_course_image(callback: types.CallbackQuery, state: FSMContext):
        ids = str(callback.data)[25:]
        keyboard = am.cancel_keyboard()
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_IMAGE)
        mess = await callback.message.answer('Пришлите фото для специальной категории.', reply_markup=keyboard)
        await state.update_data(ids=ids, mess=mess)



    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_SPECIAL_COURSE_IMAGE, content_types=['photo'])
    async def add_special_image(message: types.Message, state: FSMContext):
        data = await state.get_data()
        ids = data.get("ids")
        try:
            photo = message.photo[-1].file_id
            special = db.get_special_course(ids)
            special.photo = photo
            db.s.commit()
            await message.answer('Фото добавлено!')
        except:
            await message.answer('Ошибка')
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="add_category_photo_")
    async def set_add_category_photo(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.ADD_CATEGORY_IMAGE)
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте фото для категории", reply_markup=keyboard)
        category = db.get_category(callback.data[19:])
        await state.update_data(item=category)


    @AdminRouter.callback_query(admins=adding_ids, text_contains="add_subcategory_image_")
    async def set_add_subcategory_photo(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(EDIT_PANEL.ADD_SUBCATEGORY_IMAGE)
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте фото для подкатегории", reply_markup=keyboard)
        subcategory = db.get_subcategory(callback.data[22:])
        await state.update_data(item=subcategory)


    @AdminRouter.message(admins=adding_ids, state=[EDIT_PANEL.ADD_CATEGORY_IMAGE, EDIT_PANEL.ADD_SUBCATEGORY_IMAGE], content_types=["photo"])
    async def add_category_photo(message: types.Message, state: FSMContext):
        try:
            photo = message.photo[0].file_id
            data = await state.get_data()
            item = data.get("item")
            item.photo = photo
            db.s.commit()
            await message.answer("Готово!")
        
        except:
            await message.answer("Ошибка")


    @AdminRouter.callback_query(admins=adding_ids, text_contains="del_category_")
    async def del_category_callback(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.del_it_keyboard()
        await callback.message.answer("Вы уверены?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.DEL_CATEGORY)
        await state.update_data(callback=callback)

    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_CATEGORY, text="decline")
    async def decline_del_it(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.clear()

    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_CATEGORY, text="confirm")
    async def del_category(callback1: types.CallbackQuery, state: FSMContext):
        try:
            data = await state.get_data()
            callback = data.get("callback")

            category = db.get_category(int(callback.data[13:]))
            db.s.delete(category)
            db.s.commit()

            callback.answer("Удалено")

            await list_subcategories(callback=callback, category=1)
        
        except:
            await callback.answer("Ошибка")
        await callback1.message.delete()
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="del_subcategory_")
    async def del_subcategory_callback(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.del_it_keyboard()
        await callback.message.answer("Вы уверены?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.DEL_SUBCATEGORY)
        await state.update_data(callback=callback)

    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_SUBCATEGORY, text="decline")
    async def decline_del_it(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_SUBCATEGORY, text="confirm")
    async def del_subcategory(callback1: types.CallbackQuery, state: FSMContext):
        try:
            data = await state.get_data()
            callback = data.get("callback")

            subcategory = db.get_subcategory(int(callback.data[16:]))
            db.s.delete(subcategory)
            db.s.commit()

            callback.answer("Удалено")

            await list_subcategories(callback=callback, category=1)
        
        except:
            await callback.answer("Ошибка")
        await callback1.message.delete()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="del_sp_")
    async def del_subcategory_callback(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.del_it_keyboard()
        await callback.message.answer("Вы уверены?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.DEL_SPECIAL)
        await state.update_data(callback=callback)

    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_SPECIAL, text="decline")
    async def decline_del_it(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.DEL_SPECIAL, text="confirm")
    async def del_subcategory(callback1: types.CallbackQuery, state: FSMContext):
        try:
            data = await state.get_data()
            callback = data.get("callback")

            subcategory = db.get_special_course(int(callback.data[7:]))
            db.s.delete(subcategory)
            db.s.commit()

            callback.answer("Удалено")

            await menu(callback.message)
        
        except:
            await callback.answer("Ошибка")
        await callback1.message.delete()


    @AdminRouter.message(admins=admins_id, text="Добавить промокод")
    async def set_add_coupon_text(message: types.Message, state: FSMContext):
        mess = await message.answer("<b>Отправьте текст промокода</b>")
        await state.set_state(EDIT_PANEL.ADD_COUPON_TEXT)
        await message.delete()
        item = Coupon()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_COUPON_TEXT)
    async def add_coupon_text(message: types.Message, state: FSMContext):
        # await message.answer("<b>Отправьте кол-во использований купона</b>")
        await state.set_state(EDIT_PANEL.ADD_COUPON_COUNT)
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        item.text = message.text
        await mess.edit_text("<b>Отправьте кол-во использований промокода</b>")
        await state.update_data(item=item, mess=mess)
        await message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_COUPON_COUNT)
    async def add_coupon_count(message: types.Message, state: FSMContext):
        # await message.answer("<b>Отправьте время жизни купона (в часах) купона</b>")
        await state.set_state(EDIT_PANEL.ADD_COUPON_DATE)
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        item.count = message.text
        await mess.edit_text("<b>Отправьте время жизни промокода (в часах)</b>")
        await state.update_data(item=item, mess=mess)
        await message.delete()

    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.ADD_COUPON_DATE)
    async def add_coupon_date(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        if not message.text.isdigit():
            await mess.edit_text("Это не число")
        else:
            hours = int(message.text)
            current_time = datetime.datetime.now()
            deadline_time = current_time + datetime.timedelta(hours=hours)
            item.date = deadline_time
            db.s.add(item)
            db.s.commit()
            await mess.delete()
            await message.answer(f"Промокод:\nТекст - <b>{item.text}</b>\nИспользования - <b>{item.count}</b>\nДата - до <b>{item.date}</b>\n\nДобавлен! ")
            await message.delete()
            await state.clear()


    @dp.callback_query(text_contains="send_message_to_")
    async def send_message_to_purchase_set(callback: types.CallbackQuery, state: FSMContext):
        purchase = db.get_purchase(int(callback.data[16:]))
        markup = am.cancel_keyboard()
        mess = await callback.message.answer("Введите сообщение для отравки пользователю", reply_markup=markup)
        await state.update_data(user_id=purchase.user_id, mess=mess)
        await state.set_state(EDIT_PANEL.SEND_MESSAGE_TO)


    @dp.message(state=EDIT_PANEL.SEND_MESSAGE_TO)
    async def send_message_to_purchase(message: types.Message, state: FSMContext):
        data = await state.get_data()
        user_id = data.get("user_id")
        text = message.html_text
        mess = data.get("mess")
        await state.clear()
        await bot.send_message(user_id, text)
        await message.answer("Сообщение отправленно")
        await mess.delete()


    # ------------------------------Добавление спец. курсов-----------------------------------------------------
    @AdminRouter.callback_query(admins=adding_ids, text_contains="cancel_add_course", state=[EDIT_PANEL.ADD_SPECIAL_COURSE_NAME,
                                                                                            EDIT_PANEL.ADD_SPECIAL_COURSE_DESCRIPTION,
                                                                                            EDIT_PANEL.ADD_SPECIAL_COURSE_PHOTO,
                                                                                            EDIT_PANEL.ADD_SPECIAL_COURSE_PRICE,
                                                                                            EDIT_PANEL.ADD_SPECIAL_COURSE_CHAT_ID])
    async def cancel_add_course(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        try:
            if callback.from_user.id in adding_ids:
                keyboard = im.items_keyboard(item.special_category, admin=True)
            else:
                keyboard = im.items_keyboard(item.special_category)
            sp_category = db.get_category(item.special_category)
            string = f"➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{sp_category.name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖"
            if sp_category.photo:
                await bot.send_message(text=string, chat_id=callback.from_user.id, reply_markup=keyboard)
                await callback.message.delete()
        except Exception as e:
            await callback.answer('Пусто')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nspecial_courses')
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains='add_item_', state="*")
    async def set_add_special_course(callback: types.CallbackQuery, state: FSMContext):
        ids = str(callback.data)[9:]
        if '-' in ids:
            await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_NAME)
            keyboard = am.cancel_add_course_keyboard()
            item = AddingSpecialItem()
            mess = await callback.message.answer('Напишите название товара.', reply_markup=keyboard)
            
            item.special_category = ids[1:]
            sp_cat = db.get_special_course(int(item.special_category))
            item.category_name = sp_cat.name
            await state.update_data(mess=mess, item=item)
        else:
            await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_NAME)
            keyboard = am.cancel_add_course_keyboard()
            item = AddingItem()
            mess = await callback.message.answer('Напишите название товара.', reply_markup=keyboard)
            
            item.precategory, item.category, item.subcategory, item.subject = ids.split(":")
            await state.update_data(mess=mess, item=item)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_NAME)
    async def add_special_course_name(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.name = message.text
        keyboard = am.cancel_add_course_keyboard()
        await mess.edit_text('Напишите описание для товара.', reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_DESCRIPTION)
        await message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_DESCRIPTION)
    async def add_special_course_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        keyboard = am.cancel_add_item_photo_keyboard()
        item.description = message.text
        await mess.edit_text('Отправьте фото для товара.', reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_PHOTO)
        await message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.callback_query(admins=adding_ids, text="skip_photo", state=EDIT_PANEL.ADD_SPECIAL_COURSE_PHOTO)
    async def skip_photo_sp(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        item.photo = None
        mess = data.get("mess")
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_PRICE)
        keyboard = am.cancel_add_course_keyboard()
        await mess.edit_text('Напишите цену товара.', reply_markup=keyboard)
        await state.update_data(mess=mess, item=item)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_PHOTO, content_types=['photo'])
    async def add_special_course_photo(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.photo = message.photo[0].file_id
        keyboard = am.cancel_add_course_keyboard()
        await mess.edit_text('Напишите цену товара.', reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_PRICE)
        await message.delete()
        await state.update_data(mess=mess, item=item)

    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_PHOTO, content_types=['text'])
    async def add_special_course_photo_text(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.photo = message.text
        keyboard = am.cancel_add_course_keyboard()
        await mess.edit_text('Напишите цену товара.', reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_PRICE)
        await message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_PRICE)
    async def add_special_price(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.price = int(message.text)
        keyboard = am.cancel_add_course_keyboard()
        await mess.edit_text('Напишите chat_id товара.', reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_CHAT_ID)
        await message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_CHAT_ID)
    async def add_special_course_is_coupon(message: types.Message, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.chat_id = message.text
        keyboard = am.choose_is_coupon_keyboard()
        await mess.edit_text("На товар действуют промокоды?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_IS_COUPON)
        await message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_IS_COUPON)
    async def add_special_course_is_ref(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.is_coupon = True if callback.data == "True" else False
        keyboard = am.choose_is_coupon_keyboard()
        await callback.answer()
        await mess.edit_text("Товар учавствует в реферальной системе?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_IS_REF)
        await state.update_data(mess=mess, item=item)


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.ADD_SPECIAL_COURSE_IS_REF)
    async def add_special_course_chat_id(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        mess = data.get("mess")
        item = data.get("item")
        item.is_ref = True if callback.data == "True" else False
        keyboard = am.confirm_adding_keyboard()

        if isinstance(item, AddingSpecialItem):
            string = f"<b>{item.category_name} | {item.name}</b>\n" \
                    f"Цена: <b>{item.price}₽</b>\n" \
                    f"chat_id: {item.chat_id}\n\nНа товар действуют промокоды: {item.is_coupon}\nТовар учавствует в реферальной системе: {item.is_ref}\n\n" \
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n" \

        else:

            string = f"<b>{item.name}</b>\n" \
                    f"Цена: <b>{item.price}₽</b>\n" \
                    f"chat_id: {item.chat_id}\n\nНа товар действуют промокоды: {item.is_coupon}\nТовар учавствует в реферальной системе: {item.is_ref}\n\n" \
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n" \

        if item.photo:
            await callback.message.answer_photo(photo=item.photo, caption=string, reply_markup=keyboard)
        else:
            await callback.message.answer(string, reply_markup=keyboard)
        mess = await callback.message.answer(f"<i>{item.description}</i>"\
                                             f"➖➖➖➖➖➖➖➖➖➖➖➖")

        await state.set_state(EDIT_PANEL.ADD_SPECIAL_COURSE_CONFIRM)

        await callback.message.delete()
        await state.update_data(mess=mess, item=item)


    @AdminRouter.callback_query(admins=adding_ids, text="confirm", state=EDIT_PANEL.ADD_SPECIAL_COURSE_CONFIRM)
    async def confirm_sp(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")

        if isinstance(item, AddingSpecialItem):
            try:
                db.s.add(SpecialItem(
                    category_name=item.special_category,
                    name=item.name,
                    description=item.description,
                    photo=item.photo,
                    price=item.price,
                    chat_id=item.chat_id
                ))
                db.s.commit()
                await callback.message.answer("Добавлено")
                await callback.message.delete()
                await state.clear()
            except:
                await callback.message.answer("Ошибка")

        else:
            try:
                db.s.add(Item(
                    precategory=item.precategory,
                    category=item.category,
                    subcategory=item.subcategory,
                    subject=item.subject,
                    name=item.name,
                    chat_id=item.chat_id,
                    description=item.description,
                    photo=item.photo,
                    price=item.price,
                    is_ref=item.is_ref,
                    is_coupon=item.is_coupon,
                ))
                db.s.commit()
                await callback.message.answer("Добавлено")
                await callback.message.delete()
                await state.clear()
            except:
                await callback.message.answer("Ошибка")
        await mess.delete()


    # Эдит курсов
    @AdminRouter.callback_query(admins=adding_ids, text_contains="cancel_", state=[EDIT_PANEL.EDIT_ITEM,
                                                                                    EDIT_PANEL.EDIT_ITEM_NAME,
                                                                                    EDIT_PANEL.EDIT_ITEM_DESCRIPTION,
                                                                                    EDIT_PANEL.EDIT_ITEM_CHAT_ID,
                                                                                    EDIT_PANEL.EDIT_ITEM_PRICE,
                                                                                    EDIT_PANEL.EDIT_ITEM_IMAGE])
    async def cancel_edit_course(callback: types.CallbackQuery, state: FSMContext):
        item_id = str(callback.data)[7:]
        if "-" not in str(item_id):
            item = db.get_item(int(item_id))
            data = await state.get_data()
            desc_mess = data.get("desc_mess")
            add_mess = data.get("add_mess")
            await add_mess.delete()
            # await desc_mess.delete()
            await state.clear()
            await show_item(callback, precategory=int(item.precategory), category=int(item.category), subcategory=int(item.subcategory), subject=int(item.subject), item=item.id)
        else:
            item = db.get_item(int(item_id))
            data = await state.get_data()
            desc_mess = data.get("desc_mess")
            add_mess = data.get("add_mess")
            await add_mess.delete()
            # await desc_mess.delete()
            await state.clear()
            await show_special_item(callback, item=str(item_id))



    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_item_")
    async def edit_course_callback(callback: types.CallbackQuery, state: FSMContext):
        id = str(callback.data)[10:]
        item = db.get_item(int(id))
        markup = am.edit_buy_course(int(id))
        chat_id = item.chat_id
        string = f"Название: <b>{item.name}</b>\n\n" \
                f"Цена: <b>{item.price}₽</b>\n\n"\
                f"Chat Id: <code>{chat_id}</code>\n\n"\
                f"Ссылка:\n<code>https://t.me/{bot_name}?start=item_{id}</code>"
        photo = item.photo
        if photo:
            add_mess = await callback.message.answer_photo(photo=photo, caption=string)
        else:
            add_mess = await callback.message.answer(text=string)
        desc_mess = await bot.send_message(callback.from_user.id, text=f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{item.description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n", reply_markup=markup)
        await callback.message.delete()
        await callback.answer()
        await state.update_data(desc_mess=desc_mess, add_mess=add_mess)
        await state.set_state(EDIT_PANEL.EDIT_ITEM)


    @AdminRouter.message(admins=top_up_ids, text="Отправить сообщение пользователю")
    async def set_send_message_user_id(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            mess = await message.answer('Введите user_id пользователя', reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_MESSAGE_USER_ID)
            await state.update_data(mess=mess)
        
        except Exception:
            await message.answer('Ошибка')

    @AdminRouter.message(admins=top_up_ids, state=OTHERS_STATES.GET_MESSAGE_USER_ID)
    async def set_send_message_text(message: types.Message, state: FSMContext):
        try:
            keyboard = am.cancel_keyboard()
            data = await state.get_data()
            mess = data.get("mess")
            await mess.edit_text('Введите текст сообщения', reply_markup=keyboard)
            await state.set_state(OTHERS_STATES.GET_MESSAGE_TEXT)
            await state.update_data(user_id=message.text)
        
        except Exception:
            await message.answer('Ошибка')


    @AdminRouter.message(admins=top_up_ids, state=OTHERS_STATES.GET_MESSAGE_TEXT)
    async def send_message_user(message: types.Message, state: FSMContext):
        try:
            try:
                data = await state.get_data()
                mess = data.get("mess")
                user_id, text = data.get("user_id"), message.html_text
                await bot.send_message(chat_id=user_id, text=text)
                await message.answer("Готово")
            except Exception:
                await message.answer('Ошибка')
        
        except Exception:
            await message.answer('Ошибка')

        await mess.delete()
        await state.clear()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_i_n_", state="*")
    async def edit_item_name_callback(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = db.get_item(int(str(callback.data)[9:]))
        await state.set_state(EDIT_PANEL.EDIT_ITEM_NAME)
        keyboard = am.cancel_edit_course_keyboard(item)
        mess = await callback.message.answer('Отправьте новое название.', reply_markup=keyboard)
        await callback.message.delete()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.EDIT_ITEM_NAME)
    async def edit_item_name(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        item.name = message.text
        db.s.commit()
        await mess.edit_text('Изменено', reply_markup=None)
        await state.clear()
        await message.delete()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_des_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_description_callback(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = int(str(callback.data)[9:])
        await state.set_state(EDIT_PANEL.EDIT_ITEM_DESCRIPTION)
        keyboard = am.cancel_edit_course_keyboard(item)
        mess = await callback.message.answer('Отправьте новое описание', reply_markup=keyboard)
        await callback.message.delete()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.EDIT_ITEM_DESCRIPTION)
    async def edit_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        description = message.text
        Item = db.get_item(item)
        Item.description = description
        db.s.commit()
        await mess.edit_text('Изменено', reply_markup=None)
        await state.clear()
        await message.delete()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_ph_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_photo_callback(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = int(str(callback.data)[8:])
        await state.set_state(EDIT_PANEL.EDIT_ITEM_IMAGE)
        keyboard = am.cancel_edit_course_keyboard(item)
        mess = await callback.message.answer('Отправьте новое фото', reply_markup=keyboard)
        await callback.message.delete()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.EDIT_ITEM_IMAGE, content_types=["photo"])
    async def edit_photo(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        photo = message.photo[0].file_id
        Item = db.get_item(item)
        Item.photo = photo
        db.s.commit()
        await mess.edit_text("Изменено", reply_markup=None)
        await state.clear()
        await message.delete()


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_pr_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_price_callback(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = int(str(callback.data)[8:])
        await state.set_state(EDIT_PANEL.EDIT_ITEM_PRICE)
        keyboard = am.cancel_edit_course_keyboard(item)
        mess = await callback.message.answer('Введите новую цену', reply_markup=keyboard)
        await callback.message.delete()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=adding_ids, state=EDIT_PANEL.EDIT_ITEM_PRICE)
    async def edit_price(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        service = db.get_service_object("current_rub/usd")
        Item = db.get_item(item)
        Item.price = int(message.text)
        db.s.commit()
        await mess.edit_text('Изменено', reply_markup=None)
        await state.clear()
        await message.delete()

    @AdminRouter.callback_query(admins=admins_id, text_contains="edit_chat_id_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_chat_id_callback(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = db.get_item(int(str(callback.data)[13:]))
        await state.set_state(EDIT_PANEL.EDIT_ITEM_CHAT_ID)
        keyboard = am.cancel_edit_course_keyboard(item.id)
        mess = await callback.message.answer('Отправьте новый chat_id', reply_markup=keyboard)
        await callback.message.delete()
        await state.update_data(item=item, mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_ITEM_CHAT_ID)
    async def edit_chat_id(message: types.Message, state: FSMContext):
        data = await state.get_data()
        item = data.get("item")
        mess = data.get("mess")
        chat_id = message.text
        item.chat_id = chat_id
        db.s.commit()
        await state.clear()
        await mess.edit_text('Изменено', reply_markup=None)


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_i_ref_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_is_ref(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = db.get_item(int(str(callback.data)[11:]))
        item.is_ref = False if item.is_ref else True
        db.s.commit()

        markup = am.edit_buy_course(item.id)
        string = f"Название: <b>{item.name}</b>\n\n" \
                f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{item.description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                f"Цена: <b>{item.price}₽</b>\n\n"

        photo = item.photo

        if photo:
            await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
        else:
            await callback.message.answer(text=string, reply_markup=markup)
        await callback.message.delete()
        await state.set_state(EDIT_PANEL.EDIT_ITEM)


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_i_coup_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_is_coupon(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = db.get_item(int(str(callback.data)[12:]))
        item.is_coupon = False if item.is_coupon else True
        db.s.commit()

        markup = am.edit_buy_course(item.id)
        string = f"Название: <b>{item.name}</b>\n\n" \
                f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{item.description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                f"Цена: <b>{item.price}₽</b>\n\n"

        photo = item.photo

        if photo:
            await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
        else:
            await callback.message.answer(text=string, reply_markup=markup)
        await callback.message.delete()
        await state.set_state(EDIT_PANEL.EDIT_ITEM)


    @AdminRouter.callback_query(admins=adding_ids, text_contains="edit_nai_", state=EDIT_PANEL.EDIT_ITEM)
    async def edit_nai(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        add_mess = data.get("add_mess")
        await add_mess.delete()
        item = db.get_item(int(str(callback.data)[9:]))
        item.need_additional_info = False if item.need_additional_info else True
        db.s.commit()

        markup = am.edit_buy_course(item.id)
        string = f"Название: <b>{item.name}</b>\n\n" \
                f"Описание: \n➖➖➖➖➖➖➖➖➖➖➖➖\n<i>\n{item.description}</i>\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                f"Цена: <b>{item.price}₽</b>\n\n"

        photo = item.photo

        if photo:
            await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
        else:
            await callback.message.answer(text=string, reply_markup=markup)
        await callback.message.delete()
        await state.set_state(EDIT_PANEL.EDIT_ITEM)


    @AdminRouter.callback_query(admins=adding_ids, text_contains="del_it_", state=EDIT_PANEL.EDIT_ITEM)
    async def del_course_callback(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.del_it_keyboard()
        await callback.message.answer("Вы уверены?", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.CONFIRM_DEL_IT)
        await state.update_data(callback=callback)


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.CONFIRM_DEL_IT, text="decline")
    async def decline_del_it(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.set_state(EDIT_PANEL.EDIT_ITEM)


    @AdminRouter.callback_query(admins=adding_ids, state=EDIT_PANEL.CONFIRM_DEL_IT, text="confirm")    
    async def del_course(callback1: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        callback = data.get("callback")
        
        item = int(str(callback.data)[7:])
        item = db.get_item(item)
        db.s.delete(item)
        db.s.commit()
        await menu(callback.message)
        await callback.answer("Удаленно")
        await callback1.message.delete()
        await state.clear()


    @dp.callback_query(text="just_cancel")
    async def just_cancel(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await state.clear()


    @AdminRouter.message(admins=admins_id, text="Админ")
    async def admin_menu(message: types.Message):
            keyboard = am.main_keyboard()
            await message.answer('Админ', reply_markup=keyboard)
            await message.delete()


    @AdminRouter.message(admins=admins_id, text="🏷️Купоны")
    async def coupon_menu(message: types.Message):
            keyboard = am.coupon_menu_keyboard()
            await message.answer('🏷️Купоны', reply_markup=keyboard)
            await message.delete()


    @AdminRouter.message(admins=admins_id, text="👤Пользователь")
    async def user_menu(message: types.Message):
            keyboard = am.user_keyboard()
            await message.answer('👤Пользователь', reply_markup=keyboard)
            await message.delete()


    @dp.message(text="Меню")
    async def menu(message: types.Message):
        try:
            user_id = message.from_user.id
            admin = False
            if user_id in admins_id:
                admin = True
            keyboard = markups.main_keyboard(admin=admin)
            await message.answer('Меню', reply_markup=keyboard)
            await message.delete()
        
        except Exception:
            await message.answer('Ошибка')

    # Приветствие
    @AdminRouter.message(admins=admins_id, text='Редактировать приветствие')
    async def set_edit_start_message(message: types.Message, state: FSMContext):
        await state.set_state(EDIT_PANEL.EDIT_START)
        keyboard = am.cancel_keyboard()
        await message.answer('Введите новое приветствие', reply_markup=keyboard)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_START)
    async def edit_start_message(message: types.Message, state: FSMContext):
        start_message = db.get_service_object("start_message")
        start_message.text = message.text
        db.s.commit()
        await message.answer('Приветствие изменено!')
        await state.clear()


    # Черный список
    @AdminRouter.message(admins=admins_id, text='Cписок забаненных пользователей')
    async def ban_list(message: types.Message):
        try:
            keyboard = am.blacklist_keyboard()
            blacklist = [f"<b>{i.user_id}</b>" for i in db.s.query(Banned_user).all()]

            if blacklist:
                await message.answer(' | '.join(blacklist), reply_markup=keyboard)
            else:
                await message.answer('Пусто', reply_markup=keyboard)
        except Exception as e:
            await message.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                            f'Пользователь: @{message.from_user.username}\n'
                                            f'Строка: _{error.line}_\n'
                                            f'Номер строки: {error.lineno}')

    @AdminRouter.message(admins=admins_id, text='Кикнуть пользователя из всех каналов')
    async def kick_user_set(message: types.Message, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await state.set_state(BLACKLIST_EDIT.KICK_USER)
        mess = await message.answer("Отправьте никнейм или id пользователя", reply_markup=keyboard)
        await state.update_data(mess=mess, main_mess=message)


    @AdminRouter.message(admins=admins_id, state=BLACKLIST_EDIT.KICK_USER)
    async def kick_user(message: types.Message, state: FSMContext):
        # try:
            data = await state.get_data()
            mess = data.get("mess")
            main_mess = data.get("main_mess")
            await mess.delete()

            if not message.text.isdigit():
                username = message.text.replace('@', '')
                user = db.s.query(User).filter(User.username == username).first()
                user_id = user.id
            else:
                user_id = message.text
                user = db.get_user(int(user_id))
            await message.answer("Обработка...")

            if user:
                k = 0
                try:
                    items = db.s.query(Item).all()
                    for item in items:
                        try:
                            await asyncio.sleep(0.1)
                            if (await chat.ban_user(chat_id=int(item.chat_id), user_id=int(user_id))):
                            # link = await chat.get_invite_link(item.chat_id, 1)
                            # await message.answer(link)
                            # await chat.ban_user(chat_id=-1001438253353, user_id=int(user_id))
                                k += 1  
                        except:
                            pass
                except:
                    pass
                await message.answer(f"Пользователь <code>{user_id}</code> забанен в <code>{k}</code> чатах")
            else:
                await message.answer("Пользователь не найден")
            await state.clear()


    @AdminRouter.callback_query(admins=admins_id, text_contains="get_ph_")
    async def get_ph(callback: types.CallbackQuery, state: FSMContext):
        try:
            user_id = callback.data[7:]
            user_purchases = db.get_user_purchases(user_id)
            count_page = len(user_purchases)
        except:
            await callback.answer('Ошибка')

        try:
            await callback.message.answer(text=f'Всего у Вас покупок: {count_page}')
            mess_wait = await callback.message.answer(text="Обработка...")
            if count_page > 0:
                pages = []
                strings = []
                for i in range(count_page):
                    ids = user_purchases[i].id
                    if "*" in user_purchases[i].item_id:
                        item = False
                    else:
                        item = db.get_item(user_purchases[i].item_id)
                    price = user_purchases[i].price
                    date_time = str(user_purchases[i].datetime)

                    if item:
                        if not isinstance(item, SpecialItem):
                            precategory_name = "2021-2022" if item.precategory == "1" else "2022-2023"
                            try:
                                category = db.get_category(item.category)
                                category_name = category.name
                            except:
                                category_name = "<i>(Категория удалена)</i>"

                            try:
                                subcategory = db.get_subcategory(item.subcategory)
                                subcategory_name = subcategory.name
                            except:
                                subcategory_name = "<i>(Подкатегория удалена)</i>"

                            subject = im.all_subjects[str(item.subject)]

                            item_name = f"{precategory_name}|{category_name}|{subcategory_name}|{subject}|{item.name}"
                        else:
                            try:
                                sp_category = db.get_special_course(item.category_name)
                                sp_category_name = sp_category.name
                            except:
                                sp_category_name = "(Спец.категория удалена)"

                            item_name = f"{sp_category_name}|{item.name}"
                    else:
                        item_name = "<i>(Товар удален)</i>"

                    strings.append(f'id: <code># {str(ids)}</code>\nАртикул: {str(user_purchases[i].item_id)}\nТовар: <b>{item_name}</b>\n\nЦена: <b>{price}₽</b>\nДата и время: <b>{date_time}</b>')
                    if i % 10 == 0:
                        pages.append(strings)
                        strings = []
                if strings:
                    pages.append(strings)
                await mess_wait.delete()
                for string in pages:
                    await callback.message.answer(text='\n\n'.join(string))
                    await asyncio.sleep(0.5)
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')


    @AdminRouter.callback_query(admins=admins_id, text_contains="get_htu_")
    async def get_htu(callback: types.CallbackQuery, state: FSMContext):
        try:
            user_id = callback.data[8:]
            user_payments = db.get_user_payments(user_id)
            count_page = len(user_payments)

            await callback.message.answer(text=f'Всего у Вас пополнений: {len(user_payments)}')
            if count_page > 0:
                strings = []
                for i in range(count_page):
                    if user_payments[i].status != "PAID":
                        continue
                    ids = user_payments[i].id
                    sm = user_payments[i].sum
                    date_time = str(user_payments[i].datetime)

                    strings.append(f'id: <code>{str(ids)}</code>\nСумма: <b>{str(sm)}</b>\nДата и время: {date_time}')
                await callback.message.answer(text='id    Сумма      Дата              Время')
                await callback.message.answer(text='\n\n'.join(strings))
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')


    @AdminRouter.callback_query(admins=admins_id, text='add_blacklist')
    async def set_add_blacklist(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await state.set_state(BLACKLIST_EDIT.ADD_BLACKLIST)
        mess = await callback.message.answer("Отправьте никнейм или id пользователя", reply_markup=keyboard)
        await state.update_data(mess=mess, main_mess=callback.message)


    @AdminRouter.message(admins=admins_id, state=BLACKLIST_EDIT.ADD_BLACKLIST)
    async def ban_user(message: types.Message, state: FSMContext):
        # try:
            data = await state.get_data()
            mess = data.get("mess")
            main_mess = data.get("main_mess")
            await mess.delete()

            if not message.text.isdigit():
                username = message.text.replace('@', '')
                user = db.s.query(User).filter(User.username == username).first()
                user_id = user.id
            else:
                user_id = message.text

            blacklist = [i.user_id for i in db.s.query(Banned_user).all()]

            if user_id not in blacklist:
                db.s.add(Banned_user(user_id=str(user_id)))
                blacklist.append(user_id)
                db.s.commit()
                
                await message.answer('Пользователь забанен')

                keyboard = am.blacklist_keyboard()
                blacklist = [f"<b>{i}</b>" for i in blacklist]
                if blacklist:
                    await main_mess.edit_text(' | '.join(blacklist), reply_markup=keyboard)
                else:
                    await main_mess.edit_text('Пусто', reply_markup=keyboard)

                k = 0
                try:
                    user_purchases = db.get_user_purchases(user_id)[::-1]
                    for purchase in user_purchases:
                        try:
                            item = db.get_item(int(purchase.item_id))
                            if item:
                                if (await chat.ban_user(chat_id=int(item.chat_id), user_id=int(user_id))):
                                # link = await chat.get_invite_link(item.chat_id, 1)
                                # await message.answer(link)
                                # await chat.ban_user(chat_id=-1001438253353, user_id=int(user_id))
                                    k += 1
                        except:
                            pass
                except:
                    pass
                await message.answer(f"Пользователь <code>{user_id}</code> удален из <code>{k}</code> чатов")
            else:
                await message.answer('Пользователь уже добавлен.')
        # except Exception as e:
        #     await message.answer('Ошибка')
        #     error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        #     await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
        #                                     f'Пользователь: @{message.from_user.username}\n'
        #                                     f'Строка: _{error.line}_\n'
        #                                     f'Номер строки: {error.lineno}')
        # await state.clear()


    @AdminRouter.callback_query(admins=admins_id, text='del_blacklist')
    async def set_del_blacklist(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await state.set_state(BLACKLIST_EDIT.DEL_BLACKLIST)
        mess = await callback.message.answer("Отправьте Id пользователя", reply_markup=keyboard)
        await state.update_data(mess=mess, main_mess=callback.message)


    @AdminRouter.message(admins=admins_id, state=BLACKLIST_EDIT.DEL_BLACKLIST)
    async def unban_user(message: types.Message, state: FSMContext):
        try:
            data = await state.get_data()
            mess = data.get("mess")
            main_mess = data.get("main_mess")
            await mess.delete()

            user_id = message.text
            user = db.s.query(Banned_user).filter(Banned_user.user_id == str(user_id)).first()
            db.s.delete(user)
            db.s.commit()
            await message.answer('Пользователь разбанен')

            keyboard = am.blacklist_keyboard()
            blacklist = [f"<b>{i.user_id}</b>" for i in db.s.query(Banned_user).all()]
            if blacklist:
                await main_mess.edit_text(' | '.join(blacklist), reply_markup=keyboard)
            else:
                await main_mess.edit_text('Пусто', reply_markup=keyboard)
        except Exception as e:
            await message.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                            f'Пользователь: @{message.from_user.username}\n'
                                            f'Строка: _{error.line}_\n'
                                            f'Номер строки: {error.lineno}')
        await state.clear()


    @AdminRouter.callback_query(admins=admins_id, text="edit_main_image")
    async def set_edit_main_image(callback: types.callback_query, state: FSMContext):
        await state.set_state(EDIT_PANEL.EDIT_MAIN_IMAGE)
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте картинку", reply_markup=keyboard)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_MAIN_IMAGE, content_types=["photo"])
    async def edit_main_image(message: types.Message, state: FSMContext):
        service = db.get_service_object("main_photo")
        service.text = message.photo[0].file_id
        db.s.commit()
        await message.answer("Готово!")


    @AdminRouter.callback_query(admins=admins_id, text="del_main_image")
    async def del_main_image(callback: types.callback_query, state: FSMContext):
        service = db.get_service_object("main_photo")
        service.text = None
        db.s.commit()
        await callback.message.answer("Готово!")


    @AdminRouter.message(admins=admins_id, text="Редактировать процент для рефералов")
    async def set_referal_procent_user_id(message: types.Message, state: FSMContext):
        keyboard = am.cancel_keyboard()
        mess = await message.answer("Введите user_id пользователя", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_REFERAL_PROCENT_USER_ID)
        await state.update_data(mess=mess)


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_REFERAL_PROCENT_USER_ID)
    async def set_referal_procent(message: types.Message, state: FSMContext):
        if message.text.isdigit():
            user = db.get_user(int(message.text))
            if user:
                keyboard = am.cancel_keyboard()
                mess = await message.answer(f"<b>Текущий процент: {user.ref_procent * 100} % </b>\nВведите новый.", reply_markup=keyboard)
                await state.set_state(EDIT_PANEL.EDIT_REFERAL_PROCENT)
                await state.update_data(user=user, mess=mess)
                await message.delete()
            else:
                await message.answer("Ошибка")
                await state.clear()
        else:
            await message.answer("Ошибка")
            await state.clear()

    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_REFERAL_PROCENT)
    async def referal_procent(message: types.Message, state: FSMContext):
        try:
            proc = int(message.text) / 100
            data = await state.get_data()
            user = data.get("user")
            mess = data.get("mess")
            user.ref_procent = proc
            db.s.commit()

            await mess.edit_text("Готово")

        except:
            await message.answer("Ошибка")
            await state.clear()
        # data = await state.get_data()
        # service = data.get("service")
        # mess = data.get("mess")
        # service.text = message.text
        # db.s.commit()
        # await message.delete()
        # await mess.edit_text('Изменено', reply_markup=None)

    # Кнопки
    @AdminRouter.message(admins=admins_id, text="Редактировать кнопки")
    async def edit_buttons(message: types.Message):
        keyboard = am.edit_buttons()
        await message.answer("Редактировать кнопки", reply_markup=keyboard)
        await message.delete()


    @AdminRouter.callback_query(admins=admins_id, text="edit_manager_btn")
    async def edit_manager_btn(callback: types.callback_query):
        keyboard = am.manager_keyboard()
        await callback.message.answer('Кнопка "Менеджер"', reply_markup=keyboard)
        await callback.message.delete()


    @AdminRouter.callback_query(admins=admins_id, text="edit_manager_btn_text")
    async def set_edit_manager_btn(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте новое название для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_MANEGER_BTN_TEXT)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_MANEGER_BTN_TEXT)
    async def edit_manager_btn(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("manager_btn")
        ServObj.text = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")


    @AdminRouter.callback_query(admins=admins_id, text="edit_manager_btn_link")
    async def set_edit_manager_btn_link(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте новую ссылку для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_MANEGER_BTN_LINK)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_MANEGER_BTN_LINK)
    async def edit_manager_link(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("manager_btn")
        ServObj.link = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")


    @AdminRouter.callback_query(admins=admins_id, text="edit_rekv_btn")
    async def edit_rekv_btn(callback: types.callback_query):
        keyboard = am.rekv_keyboard()
        await callback.message.answer('Кнопка "Отзывы"', reply_markup=keyboard)
        await callback.message.delete()


    @AdminRouter.callback_query(admins=admins_id, text="edit_rekv_btn_text")
    async def set_edit_rekv_btn(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте новое название для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_REKV_BTN_TEXT)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_REKV_BTN_TEXT)
    async def edit_rekv_btn(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("rekv_btn")
        ServObj.text = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")


    @AdminRouter.callback_query(admins=admins_id, text="edit_rekv_btn_link")
    async def set_edit_rekv_btn_link(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте новую ссылку для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_REKV_BTN_LINK)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_REKV_BTN_LINK)
    async def edit_manager_link(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("rekv_btn")
        ServObj.link = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")



    @AdminRouter.callback_query(admins=admins_id, text="edit_group_btn")
    async def edit_group_btn(callback: types.callback_query):
        keyboard = am.group_keyboard()
        await callback.message.answer('Кнопка "Общая группа"', reply_markup=keyboard)
        await callback.message.delete()


    @AdminRouter.callback_query(admins=admins_id, text="edit_group_btn_text")
    async def set_edit_group_btn(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.group_keyboard()
        await callback.message.answer("Отправьте новое название для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_GROUP_BTN_TEXT)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_GROUP_BTN_TEXT)
    async def edit_group_btn(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("group_btn")
        ServObj.text = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")


    @AdminRouter.callback_query(admins=admins_id, text="edit_group_btn_link")
    async def set_edit_group_btn_link(callback: types.CallbackQuery, state: FSMContext):
        keyboard = am.cancel_keyboard()
        await callback.message.answer("Отправьте новую ссылку для кнопки", reply_markup=keyboard)
        await state.set_state(EDIT_PANEL.EDIT_GROUP_BTN_LINK)
        await callback.message.delete()


    @AdminRouter.message(admins=admins_id, state=EDIT_PANEL.EDIT_GROUP_BTN_LINK)
    async def edit_group_link(message: types.Message, state: FSMContext):
        ServObj = db.get_service_object("group_btn")
        ServObj.link = message.text
        db.s.commit()
        await state.clear()
        await message.answer("Готово!")


    @dp.message(Command(commands=["free"]))
    async def command_free(message: CommandObject):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                await free_courses(message)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    @dp.message(Command(commands=["chat"]))
    async def command_chat(message: CommandObject):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                await chat_button(message)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    # Главная часть
    @dp.message(Command(commands=["start"]))
    async def start(message: CommandObject):
        try:
            user_id = message.from_user.id
            if not db.user_exists(user_id):
                user_name = message.from_user.username
                referal = message.text[7:]
                if not referal:
                    referal = None
                    service = db.get_service_object("referal_procent")
                    db.add_user(username=user_name, user_id=user_id, referal=referal, ref_procent=float(service.text))
                    referal = None
                else:
                    admin = False
                    if user_id in admins_id:
                        admin = True

                    keyboard1 = markups.start_keyboard()
                    keyboard2 = markups.main_keyboard(admin=admin)
                    start_message = db.get_service_object("start_message")
                    await message.answer(start_message.text, reply_markup=keyboard1)
                    await message.answer_sticker(r"CAACAgQAAxkBAAEDlslhzh2gDFsGYA_fk-W1Y3U1_H_gwwACExAAAqbxcR6cXQP7S0SN7SME", reply_markup=keyboard2)

                    if not referal.isdigit():
                        service = db.get_service_object("referal_procent")
                        db.add_user(username=user_name, user_id=user_id, referal=None, ref_procent=float(service.text))
                        if "_" in referal:
                            func, value = referal.split("_")
                            if func == "item":
                                item = db.get_item(int(value))
                                if item:
                                    if "-" in value:
                                        await show_special_item(callback=message, item=str(item.id))
                                    else:
                                        await show_item(callback=message, precategory=int(item.precategory), category=int(item.category), subcategory=int(item.subcategory), subject=int(item.subject), item=int(item.id))
                                else:
                                    await message.answer("Товар не найден")

                            elif func == "ctg":
                                category = db.get_category(int(value))
                                if category:
                                    await list_subcategories(callback=message, precategory=category.precategory, category=int(value))
                                else:
                                    await message.answer("Категория не найдена")

                            elif func == "sub":
                                category_id, subcategory_id = value.split("-")
                                category = db.get_category(int(category_id))
                                subcategory = db.get_subcategory(int(subcategory_id))
                                if subcategory:
                                    await list_subjects(callback=message, precategory=category.precategory, category=category.id, subcategory=int(subcategory_id))
                                else:
                                    await message.answer("Подкатегория не найдена")

                            elif func == "sj":
                                category_id, subcategory_id, subject_id = value.split("-")
                                category = db.get_category(int(category_id))
                                subcategory = db.get_subcategory(int(subcategory_id))
                                if subcategory:
                                    await list_items(callback=message, precategory=category.precategory, category=category.category, subcategory=subcategory.id, subject=int(subject_id))
                                else:
                                    await message.answer("Подкатегория не найдена")

                            elif func == "spctg":
                                await specials(callback=message, precategory=int(value))

                            elif func == "spsub":
                                sp_category = db.get_special_course(int(value))
                                if sp_category:
                                    await special_courses(callback=message, item=int(value))
                                else:
                                    await message.answer("Спец. Категория не найдена")

                        else:
                            res = db.get_link_coupon(referal)
                            if res:
                                if int(res.count) > 0:
                                    if res.date >= datetime.datetime.today():
                                        func, value = res.func.split("_")

                                        if func == "discount":
                                            user = db.get_user(user_id)
                                            user.discount = 1 - (value / 100)
                                            user.coupon_name = "-" + message.texft[7:]

                                            temp = res.used_users[::]
                                            temp.append(user.user_id)
                                            res.used_users = temp

                                            await message.answer(f'Купон актирован.\nВы получили скидку {value}%!')

                                        elif func == "balance":
                                            user = db.get_user(user_id)
                                            res.count = res.count - 1
                                            user.balance = user.balance + value

                                            temp = res.used_users[::]
                                            temp.append(user.user_id)
                                            res.used_users = temp
                                            
                                            db.s.commit()

                                            await message.answer(f'Баланс пополнен на <b>"{value}₽"</b>')
                                    else:

                                        await message.answer("Купон не найден")
                                else:

                                    await message.answer("Купон не найден")
                        referal = None
                    else:
                        service = db.get_service_object("referal_procent")
                        db.add_user(username=user_name, user_id=user_id, referal=referal, ref_procent=float(service.text))
                # отправка нового пользователя
                await new_user(user_name, user_id)
                if referal:
                    await bot.send_message(chat_id=referal, text=f"<b>У вас +1 реферал.</b>")
            else:
                
                referal = message.text[7:]
                if referal:
                    admin = False
                    if user_id in admins_id:
                        admin = True

                    keyboard1 = markups.start_keyboard()
                    keyboard2 = markups.main_keyboard(admin=admin)
                    start_message = db.get_service_object("start_message")
                    await message.answer(start_message.text, reply_markup=keyboard1)
                    await message.answer_sticker(r"CAACAgQAAxkBAAEDlslhzh2gDFsGYA_fk-W1Y3U1_H_gwwACExAAAqbxcR6cXQP7S0SN7SME", reply_markup=keyboard2)
                    
                    if "_" in referal:
                        func, value = referal.split("_")
                        if func == "item":
                            item = db.get_item(int(value))
                            if item:
                                if "-" in value:
                                    await show_special_item(callback=message, item=str(item.id))
                                else:
                                    await show_item(callback=message, precategory=int(item.precategory), category=int(item.category), subcategory=int(item.subcategory), subject=int(item.subject), item=int(item.id))
                            else:
                                await message.answer("Товар не найден")

                        elif func == "ctg":
                            category = db.get_category(int(value))
                            if category:
                                await list_subcategories(callback=message, precategory=category.precategory, category=int(value))
                            else:
                                await message.answer("Категория не найдена")

                        # elif func == "sub":
                        #     subcategory = db.get_subcategory(int(value))
                        #     if subcategory:
                        #         await list_items(callback=message, precategory=subcategory.precategory, category=subcategory.category, subcategory=subcategory.id)
                        #     else:
                        #         await message.answer("Подкатегория не найдена")

                        elif func == "sub":
                            category_id, subcategory_id = value.split("-")
                            category = db.get_category(int(category_id))
                            subcategory = db.get_subcategory(int(subcategory_id))
                            if subcategory:
                                await list_subjects(callback=message, precategory=category.precategory, category=category.id, subcategory=int(subcategory_id))
                            else:
                                await message.answer("Подкатегория не найдена")

                        elif func == "sj":
                            category_id, subcategory_id, subject_id = value.split("-")
                            category = db.get_category(int(category_id))
                            subcategory = db.get_subcategory(int(subcategory_id))
                            if subcategory:
                                await list_items(callback=message, precategory=category.precategory, category=category.id, subcategory=subcategory.id, subject=int(subject_id))
                            else:
                                await message.answer("Подкатегория не найдена")

                        elif func == "spctg":
                            try:
                                await specials(callback=message, precategory=int(value))
                            except:
                                await message.answer("Спец. курсы не найдены")

                        elif func == "spsub":
                            sp_category = db.get_special_course(int(value))
                            if sp_category:
                                await special_courses(callback=message, item=int(value))
                            else:
                                await message.answer("Спец. категория не найдена")

                    else:
                        res = db.get_link_coupon(referal)
                        if res:
                            if int(res.count) > 0:
                                if res.date >= datetime.datetime.today():
                                    if res.used_users.count(str(message.from_user.id)) < res.user_activates:
                                        func, value = res.func.split("_")

                                        value = int(value)

                                        if func == "discount":
                                            user = db.get_user(user_id)
                                            user.discount = 1 - (value / 100)
                                            user.coupon_name = "-" + message.text[7:]

                                            temp = res.used_users[::]
                                            temp.append(user.user_id)
                                            res.used_users = temp

                                            await message.answer(f'Купон актирован.\nВы получили скидку {value}%!')

                                        elif func == "balance":
                                            user = db.get_user(user_id)
                                            res.count = str(int(res.count) - 1)
                                            user.balance = user.balance + value

                                            temp = res.used_users[::]
                                            temp.append(user.user_id)
                                            res.used_users = temp
                                            
                                            db.s.commit()

                                            await message.answer(f'Баланс пополнен на <b>"{value}₽"</b>')
                                    
                                        else:
                                            await message.answer("Неопознанная команда")
                                    else:
                                        await message.answer("Вы уже использовали этот купон")
                                else:

                                    await message.answer("Купон не найден")
                            else:

                                await message.answer("Купон не найден")
                        else:
                            await message.answer("Неопознанная команда")
            if not referal:
                admin = False
                if user_id in admins_id:
                    admin = True

                keyboard1 = markups.start_keyboard()
                keyboard2 = markups.main_keyboard(admin=admin)
                start_message = db.get_service_object("start_message")
                await message.answer(start_message.text, reply_markup=keyboard1)
                await message.answer_sticker(r"CAACAgQAAxkBAAEDlslhzh2gDFsGYA_fk-W1Y3U1_H_gwwACExAAAqbxcR6cXQP7S0SN7SME", reply_markup=keyboard2)
            # await message.answer_sticker(r"CAACAgQAAxkBAAEDlslhzh2gDFsGYA_fk-W1Y3U1_H_gwwACExAAAqbxcR6cXQP7S0SN7SME")

        
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                            f'Пользователь: @{message.from_user.username}\n'
                                            f'Строка: _{error.line}_\n'
                                            f'Номер строки: {error.lineno}')



    
    @dp.message(text="Купить курсы")
    async def BuyMenu(message: types.Message):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                await list_precategory(message)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        

    @dp.callback_query(text="check_subscribe")
    async def check_subscribe_func(callback: types.CallbackQuery, state: FSMContext):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(callback.from_user.id)))]):
                await callback.message.answer("Вы подписаны!")
                await callback.message.delete()
            else:
                await callback.answer("Подпишись на канал по кнопке выше", show_alert=True)
        except:
            await callback.answer("Подпишись на канал по кнопке выше", show_alert=True)

    # @check_blacklis

    @dp.message(text="Пополнить баланс")
    async def get_money(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                try:
                    keyboard = markups.get_money_keyboard()
                    await bot.send_message(message.from_user.id, "Отправьте сумму пополнения или выберите готовую:",
                                        reply_markup=keyboard)
                    # state = dp.current_state(user=message.from_user.id)
                    # await state.set_state(States.PAYMENT_STATE)
                    await state.set_state(States.PAYMENT_STATE)
                except Exception as e:
                    await message.answer('Ошибка')
                    error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
                    await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                                    f'Пользователь: @{message.from_user.username} {message.from_user.id}\n'
                                                    f'Строка: _{error.line}_\n'
                                                    f'Номер строки: {error.lineno}\n\nПополнить баланс')
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)

        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        

    
    @dp.callback_query(text_contains="get_money_", state=States.PAYMENT_STATE)
    async def callback_payment(callback: types.CallbackQuery, state: FSMContext):
        await make_bill(callback, state)


    @dp.callback_query(text_contains='cancel_payment_')
    async def get_current_state(callback: types.CallbackQuery):
        bill_id = str(callback.data[15:])
        db.del_payment(bill_id)
        await callback.message.edit_text('Отменено', reply_markup=None)


    @dp.message(state=States.PAYMENT_STATE)
    async def make_bill(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        try:
            if isinstance(message, types.CallbackQuery):
                message_money = message.data[10:]
                if not message_money.isdigit():
                    await message.answer('Выберите сумму для пополнения.')
            elif isinstance(message, types.Message):

                message_money = message.text
                if not message_money.isdigit():
                    await bot.send_message(message.from_user.id, 'Значение должно быть числом')
                    await state.clear()
                    return

            good_wallets = db.get_good_wallets()
            user_id = message.from_user.id
            if good_wallets:
                k = 0
                gw_count = len(good_wallets)
                while k < gw_count:
                    
                    temp = [i.id for i in good_wallets]

                    x = random.choice(temp)
                    wallet = db.s.query(Wallet).filter(Wallet.id == x).first()
                    gw_wallet = wallet.number
                    if await isgood_qiwi_wallet(wallet.api_key):
                        break
                    else:
                        try:
                            await bot.send_message(chat_id=1800414712, text=f"<i>Кошелек <b>+{gw_wallet}</b> забанен. Он удален из списка кошелько для оплаты.</i>")
                            await bot.send_message(chat_id=416702541, text=f"<i>Кошелек <b>+{gw_wallet}</b> забанен. Он удален из списка кошелько для оплаты.</i>")
                            await bot.send_message(chat_id=618290811, text=f"<i>Кошелек <b>+{gw_wallet}</b> забанен. Он удален из списка кошелько для оплаты.</i>")
                        except:
                            pass
                        try:
                            good_wallets.pop(x)
                        except:
                            pass
                        k += 1

                else:
                    try:
                        await bot.send_message(chat_id=1800414712, text=f"<i>Все кошельки забанены. Пополнения приостановлены.</i>")
                        await bot.send_message(chat_id=416702541, text=f"<i>Все кошельки забанены. Пополнения приостановлены.</i>")
                        await bot.send_message(chat_id=618290811, text=f"<i>Все кошельки забанены. Пополнения приостановлены.</i>")
                    except:
                        pass
                    await bot.send_message(chat_id=message.from_user.id, text="<b>На данный момент пополнение баланса недоступно, попробуйте позже или обратитесь к менеджеру - @UmHelper </b>")
                    return
            else:
                await bot.send_message(chat_id=message.from_user.id, text="<b>На данный момент пополнение баланса недоступно, попробуйте позже или обратитесь к менеджеру - @UmHelper </b>")
                return
        
            p2p = QiwiP2P(auth_key=wallet.p2p_key)

            lifetime = 60
            payment_id = db.get_last_payment_id() + 1
            comment = f"{str(user_id)}_{payment_id}"

            bill = p2p.bill(amount=message_money, lifetime=lifetime, comment=comment)

            current_time = datetime.datetime.now()
            deadline_time = current_time + datetime.timedelta(hours=1)

            db.add_payment(user_id, bill.bill_id, message_money, current_time)
            keyboard = markups.payment_keyboard(url=bill.pay_url, bill_id=bill.bill_id, wallet_num=x)

            string = (f'➖➖➖➖ # {payment_id}➖➖➖➖\n👤 Покупатель ID: {user_id}\n'
                    f'💰 Сумма перевода: {message_money}\n'
                    f'💭 Обязательный комментарий: {comment}\n'
                    f' ВАЖНО Не трогайте автозаполнение бота. Если его нет, введите комментарий вручную.\n'
                    f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                    f'⏰ Время на оплату: {lifetime} минут\n'
                    f'🕜 Ваша попытка платежа автоматически отменится {deadline_time.strftime("%H:%M:%S")} МСК\n '
                    f'➖➖➖➖➖➖➖➖➖➖➖➖')
            try:
                await message.message.edit_text(string, reply_markup=keyboard)
            except Exception:
                await bot.send_message(message.from_user.id, string, reply_markup=keyboard)

            await state.clear()
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                            f'Пользователь: @{message.from_user.username} {message.from_user.id}\n\n'
                                            f'{tb.format_exc()}')


    @dp.callback_query(text_contains='_check_top_up_')
    async def check_top_up(callback: types.CallbackQuery):
        # ids = callback_data.get('id')
        global wallets
        bill_id = str(callback.data[callback.data.index("_check_top_up_") + 14:])
        item = db.get_payment(bill_id)
        user_id = item.user_id
        money = item.sum
        status = item.status
        x = int(callback.data.split("_")[0])
        wallet = db.s.query(Wallet).filter(Wallet.id == x).first()
        number = wallet.number
        item.wallet = number
        db.s.commit()

        if status == 'UNPAID':
            qiwi_request_headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {wallet.p2p_key}",
                    }

            post = requests.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
            headers=qiwi_request_headers)
            # new_status = str(p2p.check(bill_id=bill_id).status)

            new_status = post.json()["status"]["value"]
            # new_status = 'PAID'
            if new_status == 'PAID':
                user_money = db.get_user_balance(user_id=user_id)

                db.set_payment_status(bill_id=bill_id, status='PAID')
                db.set_money(user_id=user_id, money=user_money + money)

                await callback.message.edit_text('Баланс пополнен')
                await bot.send_message(admins_id[0],
                                    f'Username: @{callback.from_user.username}\nUser_id: {callback.from_user.id}\n{callback.from_user.full_name} пополнил баланс на "{money}₽" на номер +{number}')
            elif new_status == 'EXPIRED':
                await callback.answer('Счет просрочен.')
            else:
                await callback.answer('Счет не оплачен.')
        else:
            await callback.answer('Счет уже был оплачен')
        # else:
        #     await bot.send_message(user_id, 'Ошибка id')


    
    @dp.message(text="Личный кабинет")
    async def lc_button(message: types.Message):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                try:
                    user_id = message.from_user.id
                    pur_num, balance = db.get_user_pur_bal(user_id)

                    keyboard = markups.lc_keyboard(admin=user_id in admins_id)

                    string = f"❤️Пользователь: @{message.from_user.username}\n💸Количество покупок: <b>{pur_num}</b>\n🔑Личный ID: <b>{user_id}</b>\n💰Баланс: <b>{balance}₽</b>"

                    await message.answer(string, reply_markup=keyboard)
                except Exception:
                    await message.answer('Ошибка')
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)

        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    @dp.callback_query(text='personal_discount')
    
    async def personal_discount(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            purchases = db.get_price_purchases(user_id)
            count_purchases = len(purchases)
            sum_of_purchases = sum(purchases)
            user = db.get_user(user_id)
            level = user.level
            discount = discount_levels[level][1]

            string = 'Статистика аккаунта:\n' \
                    f'Всего покупок: {count_purchases}\n' \
                    f'Сумма покупок: {sum_of_purchases}\n' \
                    f'Текущий уровень персональной скидки: {level}\n' \
                    f'Персональная скидка: {discount} %\n\n\n' \
                    f'Уровни скидок, которые созданы в магазине:\n' \
                    f'Без скидок [скидка: 0 %] [Сумма от 0 ₽]\n' \
                    f'Школьник [скидка: 5 %] [Сумма от 850 ₽]\n' \
                    f'Студентик [скидка: 10 %] [Сумма от 1400 ₽]\n ' \
                    f'Магистр [скидка: 15 %] [Сумма от 1700 ₽]\n\n\n'

            await callback.message.edit_text(string)
        except Exception as e:
            await callback.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')

    @dp.callback_query(text="purchase_history")
    async def purchases_history(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            user_purchases = db.get_user_purchases(user_id)
            count_page = len(user_purchases)
        except:
            await callback.answer('Ошибка')

            # keyboard = markups.top_up_history_keyboard(current_page, count_page)
        try:
            await bot.send_message(user_id, text=f'Всего у Вас покупок: {count_page}')
            if count_page > 0:
                pages = []
                strings = []
                for i in range(count_page):
                    ids = user_purchases[i].id
                    item = user_purchases[i].item_id
                    price = user_purchases[i].price
                    date_time = str(user_purchases[i].datetime)

                    strings.append(f'id: <code># {str(ids)}</code>\nАртикул: <b>{str(item)}</b>\nЦена: <b>{price}₽</b>\nДата и время: <b>{date_time}</b>')
                    if i % 10 == 0:
                        pages.append(strings)
                        strings = []
                if strings:
                    pages.append(strings)
                    # if i == 18:
                    #     pages.append(f'')
                # await bot.send_message(user_id, text='id    Артикул:Цена      Дата              Время')
                for string in pages:
                    await bot.send_message(user_id, text='\n\n'.join(string))
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')


    @dp.callback_query(text="referal_system")
    async def referal_system(callback: types.CallbackQuery):
        # servObj = db.get_service_object("referal_procent")
        user_id = str(callback.from_user.id)
        user = db.get_user(int(user_id))
        keyboard = markups.referral_system_keyboard()
        referral_link = f'https://t.me/{bot_name}?start={user_id}'

        string = 'В боте включена реферальная система. Приглашайте друзей и зарабатывайте на этом!' \
                f' Вы будете получать: {user.ref_procent * 100} % с каждой покупки вашего реферала\n\n' \
                f'Ваша реферальная ссылка:\n<code>{referral_link}</code>'

        await callback.message.answer(string, reply_markup=keyboard, disable_web_page_preview=True)


    @dp.callback_query(text='referral_link')
    
    async def referral_link(callback: types.CallbackQuery):
        await callback.message.edit_text(f'<code>https://t.me/{bot_name}?start={str(callback.from_user.id)}</code>', disable_web_page_preview=True)


    @dp.callback_query(text='referral_list')
    
    async def referral_list(callback: types.CallbackQuery):
        try:
            user_id = callback.from_user.id
            referrals = db.get_referrals(user_id)
            count_referrals = len(referrals)


            if count_referrals > 0:
                messages = []
                temp = []
                for x in range(count_referrals):
                    temp.append(referrals[x])
                    if x % 100 == 0:
                        messages.append(", ".join(temp))
                        temp = []

                if temp:
                    messages.append(", ".join(temp))
                    temp = []
                string = f'Вы пригласили <b>{count_referrals}</b> пользователей: \n {messages[0]}'
            else:
                string = f'Вы пригласили <b>{count_referrals}</b> пользователей.'
            await callback.message.edit_text(string)
            if len(messages) > 1:
                for i in messages[1:]:
                    await callback.message.answer(i)
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')


    # 
    @dp.callback_query(text='top_up')
    async def callback_get_money(callback: types.CallbackQuery, state: FSMContext):
        await get_money(callback, state)


    @dp.callback_query(text="history_top_up")
    async def top_up_history(callback: types.CallbackQuery, current_page=0):
        try:
            user_id = callback.from_user.id
            user_payments = db.get_user_payments(user_id)
            count_page = len(user_payments)

            await bot.send_message(user_id, text=f'Всего у Вас пополнений: {len(user_payments)}')
            if count_page > 0:
                strings = []
                for i in range(count_page):
                    if user_payments[i].status != "PAID":
                        continue
                    ids = user_payments[i].id
                    sm = user_payments[i].sum
                    date_time = str(user_payments[i].datetime)

                    strings.append(f'id: <code>{str(ids)}</code>\nСумма: <b>{str(sm)}</b>\nДата и время: {date_time}')
                await bot.send_message(user_id, text='id    Сумма      Дата              Время')
                await bot.send_message(user_id, text='\n\n'.join(strings))
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')

    
    @dp.callback_query(text="coupon_activator")
    async def set_coupon_activator(callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(States.COUPONS_STATE)
        keyboard = am.cancel_keyboard()
        await callback.answer()
        await callback.message.answer('Введите промокод:', reply_markup=keyboard)


    @dp.message(state=States.COUPONS_STATE)
    async def coupon_activator(message: types.Message, state: FSMContext):
        try:
            user = db.get_user(message.from_user.id)
            coupon = db.get_coupon(message.text)
            if coupon:
                if int(coupon.count) > 0:
                    if coupon.date >= datetime.datetime.today():
                        user.discount = 1 - (coupon.proc / 100)
                        user.coupon_name = message.text
                        await message.answer(f'Промокод актирован.\nВы получили скидку {coupon.proc}%!')
                    else:
                        db.s.delete(coupon)
                        db.s.commit()

                        await message.answer("Промокод истек.")
                else:
                    db.s.delete(coupon)
                    db.s.commit()

                    await message.answer("Промокод кончился.")
            else:
                await message.answer('Промокод не найден.')
            await state.clear()
        
        except Exception as e:
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{message.from_user.username}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}')



    @dp.message(text="Бесплатные курсы")
    async def free_courses(message: types.Message):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                if message.from_user.id in admins_id:
                    keyboard = markups.free_course_keyboard(admin=True)
                else:
                    keyboard = markups.free_course_keyboard(admin=True)
                await bot.send_message(message.from_user.id, "Бесплатные курсы", reply_markup=keyboard)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)

        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    @dp.message(text="Помощь")
    async def help_button(message: types.Message):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                keyboard = markups.help_keyboard()
                await bot.send_message(message.from_user.id, "Для помощи", reply_markup=keyboard)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    @dp.message(text="Общая группа")
    async def chat_button(message: types.Message):
        try:
            if all([await check_subscribe(await bot.get_chat_member(chat_id=-1001729459717, user_id=int(message.from_user.id)))]):
                keyboard = markups.group_keyboard()
                await bot.send_message(message.from_user.id, "Спасибо за выбор нашей группы :)", reply_markup=keyboard)
            else:
                keyboard = markups.check_subscribe_keyboard()
                await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)
        except:
            keyboard = markups.check_subscribe_keyboard()
            await message.answer("Для дальнейшего пользования бота необходимо подписаться на наш основной канал с новостями/скидками\n\n*обязательно сохрани наш сайт, в случае блокировки он перенаправит вас на актуального бота - kurse.me", reply_markup=keyboard)


    @dp.callback_query(text_contains="halfyear_courses_", state="*")
    async def halfyear_courses(callback: types.CallbackQuery):
        try:
            x = int(callback.data[17:])
            # markup = await im.halfyear_courses_keyboard(precategory=x)
            markup = await im.special_items_keyboard(x, admin=callback.from_user.id in admins_id)
            if markup:
                await callback.message.answer_photo(
                    photo='AgACAgIAAxkBAAEFpCNjoPKxh3ccvOszZ-3WLirwM3QnxwACXMIxGyzwCEm9nGoCigMHIwEAAwIAA3MAAywE',
                    # photo='AgACAgIAAxkBAAICT2HSA5CQvujaCedqnM0hwH2rpcHgAAL5ujEbIRuRSpMB6ljQ08iTAQADAgADcwADIwQ',
                    caption='➖➖➖➖➖➖➖➖➖➖➖➖\n<b>Январь | Полугодовые ЕГЭ</b>\n➖➖➖➖➖➖➖➖➖➖➖➖', reply_markup=markup)
                await callback.message.delete()
            else:
                await callback.answer('Пусто')
        except Exception as e:
            await callback.answer('Пусто')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nhalfyear_courses')


    
    @dp.callback_query(text_contains="specials_", state="*")
    async def specials(callback: types.CallbackQuery, precategory=None):
        try:
            if not precategory:
                precategory = int(callback.data[9:])

            if callback.from_user.id in admins_id:
                keyboard = await im.specials_keyboard(admin=True, precategory=precategory)
            else:
                keyboard = await im.specials_keyboard(precategory=precategory)
            string = "<b>Специальные курсы</b>"
            photo = "AgACAgIAAxkBAAJyx2LTzu_JhNY85sriva865iio_nU3AAJ7uzEbjbOhSrGeA5Hl01VBAQADAgADcwADKQQ"
            if isinstance(callback, types.CallbackQuery):
                await callback.message.answer_photo(photo=photo, caption=string, reply_markup=keyboard)
                await callback.message.delete()
            else:
                await callback.answer_photo(photo=photo, caption=string, reply_markup=keyboard)
        except Exception as e:
            await callback.answer('Пусто')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nspecials')


    @dp.callback_query(text_contains="sp_cat_", state="*")
    
    async def special_courses(callback: types.CallbackQuery, item=None):
        try:
            if not item:
                ids = str(callback.data)[7:]
            else:
                ids = item

            sp = db.get_special_course(ids)
            sp_name, photo = sp.name, sp.photo

            if callback.from_user.id in admins_id:
                markup = await im.special_items_keyboard(int(ids), admin=True)
            else:
                markup = await im.special_items_keyboard(int(ids))
            string = f"<b>{sp_name}</b>"
            
            if isinstance(callback, types.CallbackQuery):
                if callback.message.photo:
                    if photo:
                        photo = InputMediaPhoto(media=photo)
                        await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                        await callback.message.edit_caption(string, reply_markup=markup)
                    else:
                        await callback.message.answer(string, reply_markup=markup)
                        await callback.message.delete()
                else:
                    if photo:
                        await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
                        await callback.message.delete()
                    else:
                        await callback.message.edit_text(string, reply_markup=markup)
            else:
                if photo:
                    await callback.answer_photo(photo=photo, caption=string, reply_markup=markup)
                else:
                    await callback.answer(string, reply_markup=markup)
        except Exception as e:
            await callback.answer('Пусто')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nspecial_courses')


    @dp.callback_query(text_contains="sp_itm_", state="*")
    async def show_special_item(callback: types.CallbackQuery, item=None):
        #try:
            user_id = callback.from_user.id
            user = db.get_user(user_id)
            if item:
                ids = item
            else:
                ids = str(callback.data)[7:]
            item = db.get_item("-" + ids)
            sp_name, name, description, photo, price = item.category_name, item.name, item.description, item.photo, item.price

            if user_id in adding_ids:
                admin = True
            else:
                admin = False

            markup = im.item_keyboard(item, user_id, admin)

            # 

            level = user.level
            start_price = price
            coupon_discount = user.discount
            try:
                if level != 'Без скидок':
                    price = int(((100 - discount_levels[level][1]) / 100) * price)
                if coupon_discount != 1.00:
                    coupon = db.get_coupon(user.coupon_name)
                    if coupon.date >= datetime.datetime.today():
                        price = int(price * coupon_discount)
                    else:
                        user.discount = 1
                        user.coupon_name = None
            except:
                pass

            if start_price != price:
                adding = f' <strike>({start_price}₽)</strike>\n' \
                    f'Скидка: <b>{round((1 - price / start_price)*100)}%</b>\n'
            else:
                adding = '\n'

            sp_name = db.get_special_course(sp_name)
            string = f'<b>{sp_name.name} | ' \
                    f"{name}</b>\n" \
                    f'💰 Цена: <b>{price}₽</b>{adding}'\
                    f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                    f'<i>{description}</i>\n' \
                    f'➖➖➖➖➖➖➖➖➖➖➖➖'


            if isinstance(callback, types.CallbackQuery):
                if callback.message.photo:
                    if photo:
                        photo = InputMediaPhoto(media=photo)
                        await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                        await callback.message.edit_caption(string, reply_markup=markup)
                    else:
                        await callback.message.answer(string, reply_markup=markup)
                        await callback.message.delete()
                else:
                    if photo:
                        await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
                        await callback.message.delete()
                    else:
                        await callback.message.edit_text(string, reply_markup=markup)
            else:
                if photo:
                    await callback.answer_photo(photo=photo, caption=string, reply_markup=markup)
                else:
                    await callback.answer(string, reply_markup=markup)
        # except Exception as e:
        #     await callback.answer('Пусто')
        #     error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        #     await bot.send_message(416702541, f'Ошибка: {e}\n\n'
        #                                     f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
        #                                     f'Строка: {error.line}\n'
        #                                     f'Номер строки: {error.lineno}\n\n{str([sp_name, name, callback.from_user.id])}')


    async def cancel_menu(callback: types.CallbackQuery, **kwargs):
            # await callback.message.edit_text('Отменено', reply_markup=None)
            await callback.message.delete()


    @dp.callback_query(text="menu")
    async def call_menu(callback: types.CallbackQuery):
        await list_precategory(callback)


    async def list_precategory(callback: Union[types.Message, types.CallbackQuery], **kwargs):
        try:
            markup = await im.precategory_keyboard(admin=callback.from_user.id in admins_id)

            string = "<b>➖➖➖➖➖➖➖➖➖➖➖➖\nВыберите категорию\n➖➖➖➖➖➖➖➖➖➖➖➖</b>"

            if isinstance(callback, types.Message):
                await callback.answer(text=string, reply_markup=markup)
            else:
                if callback.message.photo:
                    await callback.message.answer(text=string, reply_markup=markup)
                    await callback.message.delete()
                else:
                    await callback.message.edit_text(text=string, reply_markup=markup)
        except Exception as e:
            await callback.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nCategories')


    async def list_categories(callback: Union[types.Message, types.CallbackQuery], precategory, **kwargs):
        try:
            if precategory == "1":
                photo = "AgACAgIAAxkBAAJvkGLS4brtrgUeh3uHvbdt407eeCa6AAJ3vTEbjbOZSs0xxYUF3fBKAQADAgADcwADKQQ"
            else:
                photo = "AgACAgIAAxkBAAJvImLS2Y5ATiztG1P8J58_4rC8CzV3AAJ2vTEbjbOZSlXjr5-Sw9ERAQADAgADcwADKQQ"
            if callback.from_user.id in admins_id:
                markup = await im.category_keyboard(precategory=precategory, admin=True)
            else:
                markup = await im.category_keyboard(precategory=precategory)
            
            string = "<b>➖➖➖➖➖➖➖➖➖➖➖➖\nВыбери месяц\n➖➖➖➖➖➖➖➖➖➖➖➖</b>"

            service = db.get_service_object("main_photo")
            # try:
            #     photo = service.text
            # except:
            #     photo = None

            if isinstance(callback, types.Message):
                if photo:
                    await callback.answer_photo(photo=photo, caption=string, reply_markup=markup)
                else:
                    await callback.answer(text=string, reply_markup=markup)

            elif isinstance(callback, types.CallbackQuery):
                call = callback

                if photo:
                    if callback.message.photo:
                        photo = InputMediaPhoto(media=photo)
                        await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                        await call.message.edit_caption(caption=string, reply_markup=markup)
                    else:
                        await call.message.delete()
                        await call.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
                else:
                    if callback.message.photo:
                        await callback.message.answer(text=string, reply_markup=markup)
                        await callback.message.delete()
                    else:
                        await callback.message.edit_text(text=string, reply_markup=markup)
        
        except Exception as e:
            await callback.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\nCategories')


    async def list_subcategories(callback: Union[types.CallbackQuery, types.Message], precategory, category, **kwargs):
        try:
            category = db.get_category(category)
            name, photo = category.name, category.photo

            if callback.from_user.id in adding_ids:
                markup = await im.subcategory_keyboard(precategory, category.id, admin=True)
            else:
                markup = await im.subcategory_keyboard(precategory, category.id)
            
            if isinstance(callback, types.CallbackQuery):
                if photo:
                    if callback.message.photo:
                        photo = InputMediaPhoto(media=photo)
                        await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                        await callback.message.edit_caption(f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                            reply_markup=markup)
                    else:
                        await callback.message.answer_photo(photo=photo, caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                            reply_markup=markup)
                        await callback.message.delete()
                else:
                    if callback.message.photo:
                        await callback.message.delete()
                        await callback.message.answer(f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                        reply_markup=markup)
                    else:
                        await callback.message.edit_text(text=f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                            reply_markup=markup)
            else:
                if photo:
                    await callback.answer_photo(photo=photo, caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                        reply_markup=markup)
                else:
                    await callback.answer(f'➖➖➖➖➖➖➖➖➖➖➖➖\n<b>{name}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                                        reply_markup=markup)
        
        except Exception:
            await callback.answer('Ошибка')


    async def list_subjects(callback: types.CallbackQuery, precategory, category, subcategory, **kwargs):
        try:
            category = db.get_category(category)
            subcategory = db.get_subcategory(subcategory)
        
            if subcategory == '9':
                await list_items(callback, category, subcategory, subject='14')
            else:
                string = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                        f'<b>{category.name} | {subcategory.name}</b>' \
                        f'\n➖➖➖➖➖➖➖➖➖➖➖➖'
                
                photo = subcategory.photo
                markup = await im.subject_keyboard(precategory, category.id, subcategory.id, admin=callback.from_user.id in admins_id)

                if isinstance(callback, types.CallbackQuery):
                    if photo:
                        if callback.message.photo:
                            await bot.edit_message_media(media=InputMediaPhoto(media=photo), chat_id=callback.from_user.id, message_id=callback.message.message_id)
                            await callback.message.edit_caption(string, reply_markup=markup)
                        else:
                            await callback.message.answer_photo(photo=photo, caption=string,
                                                                reply_markup=markup)
                            await callback.message.delete()
                    else:
                        await callback.message.answer(string, reply_markup=markup)
                        await callback.message.delete()
                else:
                    if photo:
                        if callback.photo:
                            await bot.edit_message_media(media=InputMediaPhoto(media=photo), chat_id=callback.from_user.id, message_id=callback.message.message_id)
                            await callback.edit_caption(string, reply_markup=markup)
                        else:
                            await callback.answer_photo(photo=photo, caption=string,
                                                                reply_markup=markup)
                            await callback.delete()
                    else:
                        await callback.answer(string, reply_markup=markup)
                        await callback.delete()
        except Exception as e:
            await callback.answer('Пусто')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\n{str([category, subcategory])}')


    async def list_items(callback: Union[types.CallbackQuery, types.Message], precategory, category, subcategory, subject, **kwargs):
        try:    
            subjects = im.all_subjects

            if callback.from_user.id in adding_ids:
                markup = await im.items_keyboard(precategory, category, subcategory, subject, admin=True)
            else:
                markup = await im.items_keyboard(precategory, category, subcategory, subject)

            category = db.get_category(category)
            subcategory = db.get_subcategory(subcategory)

            string = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                    f'<b>{category.name} | {subcategory.name} | {subjects[str(subject)]}</b>\n➖➖➖➖➖➖➖➖➖➖➖➖'
            
            if not markup:
                raise ZeroDivisionError
                
            photo = subcategory.photo

            if isinstance(callback, types.CallbackQuery):
                if callback.message.photo:
                    if photo:
                        photo = InputMediaPhoto(media=photo)
                        await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                        await callback.message.edit_caption(string, reply_markup=markup)
                    else:
                        await callback.message.answer(string, reply_markup=markup)
                        await callback.message.delete()
                else:
                    if photo:
                        await callback.message.answer_photo(photo=photo, caption=string,
                                                            reply_markup=markup)
                        await callback.message.delete()
                    else:
                        await callback.message.edit_text(string, reply_markup=markup)
            else:
                if photo:
                    await callback.answer_photo(photo=photo, caption=string, reply_markup=markup)
                else:
                    await callback.answer(string, reply_markup=markup)
        except:
            await callback.answer('Пусто')


    async def show_item(callback: Union[types.CallbackQuery, types.Message], precategory, category, subcategory, subject, item, **kwargs):
        try:
            item = db.get_item(item)
            user_id = callback.from_user.id
            user = db.get_user(user_id)
        
            coupon_discount = user.discount
            if user_id in adding_ids:
                admin = True
            else:
                admin = False

            markup = im.item_keyboard(item, user_id, admin)

            photo = item.photo
            price = item.price
            start_price = price

            if item.is_coupon:
                try:
                    if user.level != 'Без скидок':
                        price = int(((100 - discount_levels[user.level][1]) / 100) * price)

                    if coupon_discount != 1.00:
                        coupon = db.get_coupon(user.coupon_name)
                        if coupon.date >= datetime.datetime.today():
                            price = int(price * coupon_discount)
                        else:
                            user.discount = 1
                            user.coupon_name = None
                except:
                    pass

            # if (subcategory == 2 and category == 10):
            #     subjects = im.subjects_flash
            # elif (subcategory == 2 and category == 11):
            #     subjects = im.subjects_flash
            # elif subcategory == 2 or subcategory == 8:
            #     subjects = im.subjects_oge
            # else:
            #     subjects = im.subjects

            subjects = im.all_subjects

            if start_price != price:
                adding = f' <strike>({start_price}₽)</strike>\n' \
                    f'Скидка: <b>{round((1 - price / start_price)*100)}%</b>'
            else:
                adding = ''

            category = db.get_category(category)
            subcategory = db.get_subcategory(subcategory)

            string = f'<b>{category.name} | ' \
                        f"{subcategory.name} | " \
                        f'{subjects[str(subject)]} | {item.name}</b>\n' \
                        f'💰 Цена: <b>{price}₽</b>{adding}\n' \
                        f'\n' \
                        f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                        f'<i>{item.description}</i>\n' \
                        f'➖➖➖➖➖➖➖➖➖➖➖➖'
            try:
                if isinstance(callback, types.CallbackQuery):
                    if callback.message.photo:
                        if photo:
                            photo = InputMediaPhoto(media=photo)
                            await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                            await callback.message.edit_caption(string, reply_markup=markup)
                        else:
                            await callback.message.answer(string, reply_markup=markup)
                            await callback.message.delete()
                    else:
                        if photo:
                            await callback.message.answer_photo(photo=photo, caption=string, reply_markup=markup)
                            await callback.message.delete()
                        else:
                            await callback.message.edit_text(string, reply_markup=markup)
                else:
                    if photo:
                        await callback.answer_photo(photo=photo, caption=string, reply_markup=markup)
                    else:
                        await callback.answer(string, reply_markup=markup)
            except:
                string1 = f'<b>{category.name} | ' \
                        f"{subcategory.name} | " \
                        f'{subjects[str(subject)]} | {item.name}</b>\n' \
                        f'💰 Цена: <b>{price}₽</b>{adding}\n' 

                string2 = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                        f'<i>{item.description}</i>\n' \
                        f'➖➖➖➖➖➖➖➖➖➖➖➖'

                if isinstance(callback, types.CallbackQuery):
                    if callback.message.photo:
                        if photo:
                            # photo = InputMediaPhoto(media=photo)
                            # await bot.edit_message_media(media=photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
                            await callback.message.edit_caption(string1)
                            await callback.message.answer(string2, reply_markup=markup)
                        else:
                            await callback.message.answer(string, reply_markup=markup)
                            await callback.message.delete()
                    else:
                        if photo:
                            await callback.message.answer_photo(photo=photo, caption=string1)
                            await callback.message.answer(caption=string2, reply_markup=markup)
                            await callback.message.delete()
                        else:
                            await callback.message.edit_text(string1 + "\n\n" + string2, reply_markup=markup)
                else:
                    if photo:
                        await callback.message.answer_photo(photo=photo, caption=string1)
                        await callback.message.answer(caption=string2, reply_markup=markup)
                    else:
                        await callback.answer(string1 + "\n\n" + string2, reply_markup=markup)  
        
        except Exception as e:
            await callback.answer('Пусто')
            # error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Параметры: {str([category.name, subcategory.name, item.name])}')

    @dp.callback_query(im.buy_item_cd.filter())
    async def but_item(callback: types.CallbackQuery, callback_data: dict):
        try:
            price = int(callback_data.price)
            user_id = callback_data.user_id

            user = db.get_user(int(user_id))
            coupon_discount = user.discount
            temp_coupon_discount = 0
            user_money = user.balance
            level = user.level
            try:
                if level != 'Без скидок':
                    price = int(((100 - discount_levels[level][1]) / 100) * price)

                if coupon_discount != 1.00:
                    coupon = db.get_coupon(user.coupon_name)
                    if coupon.date >= datetime.datetime.today():
                        price = int(price * coupon_discount)
                        temp_coupon_discount = coupon_discount * 100
                    else:
                        user.discount = 1
                        user.coupon_name = None
            except:
                pass

            if price <= user_money:
                item = db.get_item(callback_data.item_id)
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

                chat_id = item.chat_id

                link = await chat.get_invite_link(chat_id=chat_id, member_limit=1)
                purchase = db.add_purchase(user_id, str(item.id), price, date)
                purchase_id = purchase.id
                db.set_money(user_id=user_id, money=user_money - price)
                db.set_purchase(user_id=user_id)

                purchase_name = item.name
                if isinstance(item, Item):
                    category = db.get_category(item.category)
                    subcategory = db.get_subcategory(item.subcategory)

                    # if (subcategory == 2 and category == 10):
                    #     subjects = im.subjects_flash
                    # elif (subcategory == 2 and category == 11):
                    #     subjects = im.subjects_flash
                    # elif subcategory == 2 or subcategory == 8:
                    #     subjects = im.subjects_oge
                    # else:
                    #     subjects = im.subjects

                    subjects = im.all_subjects

                    discount_level = calculate_personal_discount(discount_levels, sum(db.get_price_purchases(user_id)))[0]

                    user.level = discount_level
                    try:
                        check = f'<b>{category.name} | ' \
                                f"{subcategory.name} | " \
                                f'{subjects[str(item.subject)]} | {item.name}</b>\n' \
                                "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                f"💡 Заказ <code>#{purchase_id}</code>\n" \
                                f"🕐 Время заказа: <b>{date}</b>\n" \
                                f"💸 Итоговая сумма: <b>{price}₽</b>\n" \
                                f"🏷️ Личная скидка: <b>{discount_levels[level][1]}%</b>\n" \
                                f"🏷️ Купон-скидка: <b>{temp_coupon_discount}%</b>\n" \
                                "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                "💳 Способ оплаты: <b>БАЛАНС</b>\n" \
                                f"👤 Покупатель ID: <code>{callback.from_user.id}</code>\n" \
                                f"👤 Покупатель: @{callback.from_user.username} ({callback.from_user.full_name})\n" \
                                "📃 Инструкция: <i>После оплаты перейдите по сcылке, которую вы видите ниже и подпишитесь на канал! Если вы после перехода потеряли канал, то просто введите в поиске ТГ название купленного предмета.</i> \n\n" \
                                "➖➖➖➖➖➖➖➖➖➖➖➖"
                        await bot.send_message(user_id, check)
                    except Exception as e:
                        pass
                else:
                    discount_level = calculate_personal_discount(discount_levels, sum(db.get_price_purchases(user_id)))[0]

                    category = db.get_special_course(int(item.category_name))

                    user.level = discount_level
                    try:
                        check = f'<b>{category.name} | ' \
                                f'{item.name}</b>\n' \
                                "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                f"💡 Заказ <code>#{purchase_id}</code>\n" \
                                f"🕐 Время заказа: <b>{date}</b>\n" \
                                f"💸 Итоговая сумма: <b>{price}₽</b> (Личная скидка {discount_levels[level][1]} %) \n" \
                                "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                "💳 Способ оплаты: <b>БАЛАНС</b>\n" \
                                f"👤 Покупатель ID: <code>{callback.from_user.id}</code>\n" \
                                f"👤 Покупатель: @{callback.from_user.username} ({callback.from_user.full_name})\n" \
                                "📃 Инструкция: <i>После оплаты перейдите по сcылке, которую вы видите ниже и подпишитесь на канал! Если вы после перехода потеряли канал, то просто введите в поиске ТГ название купленного предмета.</i> \n\n" \
                                "➖➖➖➖➖➖➖➖➖➖➖➖"
                        await bot.send_message(user_id, check)
                    except Exception as e:
                        pass

                string = f'➖➖➖➖➖ <code>#{purchase_id}</code> ➖➖➖➖➖\n<b>ССЫЛКА: {link}</b>'

                coupon_discount = 1
                await bot.send_message(user_id, string)
                await bot.send_message(admins_id[0], check)

                upreferral = user.referal
                if upreferral:
                    upreferral_money = (db.get_user(user_id=upreferral)).balance
                    upreferral_bonus = int(price * 0.2)
                    db.set_money(user_id=upreferral, money=upreferral_money + upreferral_bonus)
                    await bot.send_message(upreferral,
                                        f'Ваш реферал совершил покупку!\nНа ваш счет зачисленно {upreferral_bonus}₽')

                user.discount = 1
                user.coupon = None

                await asyncio.sleep(0.4)
            else:
                keyboard = markups.not_enough_balance()
                await callback.answer('Недостаточно средств', show_alert=True)
        except Exception as e:
            await callback.answer('Ошибка')
            error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
            await bot.send_message(416702541, f'Ошибка: {e}\n\n'
                                            f'Пользователь: @{callback.from_user.username} {callback.from_user.id} {callback.from_user.full_name}\n'
                                            f'Строка: {error.line}\n'
                                            f'Номер строки: {error.lineno}\n\n{str(callback_data)}')


    @dp.callback_query(im.menu_cd.filter(), state="*")
    async def navigate(callback: types.CallbackQuery, callback_data: dict):
        current_level = callback_data.lvl
        precategory = callback_data.p
        category = callback_data.c
        subcategory = callback_data.s
        subject = callback_data.j
        item = callback_data.i

        levels = {
            "-1": cancel_menu,
            "0": list_precategory,
            "1": list_categories,
            "2": list_subcategories,
            "3": list_subjects,
            "4": list_items,
            "5": show_item
        }

        current_level_function = levels[str(current_level)]

        await current_level_function(
            callback=callback,
            lvl=category,
            precategory=precategory,
            category=category,
            subcategory=subcategory,
            subject=subject,
            item=item
        )
        


    @AdminRouter.message(admins=admins_id, content_types=["photo"])
    async def image_id(message: types.Message):
        await message.answer(str(message.photo[0].file_id))


    @OtherRouter.message()
    async def another(message: types.Message):
       if message.chat.id > 0:
           await message.answer("К сожалению я не смог распознать Вашу команду.\nВоспользуйтесь кнопками в меню или отправьте /start")


    if __name__ == "__main__":
        GlobalRouter.run_polling(bot)


except TelegramAPIError:
    pass
except TelegramBadRequest:
    pass
except TelegramForbiddenError:
    pass
except TelegramNetworkError:
    pass