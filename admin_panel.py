import asyncio
import datetime
import logging
from pyqiwip2p import QiwiP2P
from db.db import Database
from config import *
import keyboards.admin_markups as am
import pandas as pd

from aiogram.types.input_file import FSInputFile
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types, F

from threading import Thread
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import markups
from utils.utils import EDIT_PANEL


db = Database()


OrderBot = Bot(token=ADMIN_TOKEN, parse_mode="HTML")
bot = Bot(token=TOKEN, parse_mode="HTML")

dp = Dispatcher()

throttled_rate = 2
p2p = ''


@dp.callback_query(text_contains="edit_cost_price_")
async def set_edit_cost_price(callback: types.CallbackQuery, state: FSMContext):
    keyboard = am.cancel_keyboard()
    mess = await callback.message.answer("Отправьте себестоимость заказа", reply_markup=keyboard)
    await state.set_state(EDIT_PANEL.EDIT_COST_PRICE)
    await state.update_data(callback=callback, mess=mess)


@dp.message(state=EDIT_PANEL.EDIT_COST_PRICE)
async def edit_cost_price(message: types.Message, state: FSMContext):
    try:
        cost_price = float(message.text)
    except:
        await message.answer("Значение должно быть числом")
        return

    data = await state.get_data()
    callback = data.get("callback")
    mess = data.get("mess")
    
    purchase = db.get_purchase(int(callback.data[16:]))

    purchase.cost_price = cost_price

    db.s.commit()
    keyboard = markups.wait_admin_keyboard(purchase.id)
    string = "\n".join(callback.message.html_text.split("\n")[:-1]) + f'\n<b>Себестоимость заказа: <i>{cost_price}</i>.</b>'

    if callback.message.photo:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_caption(chat_id=i[0], message_id=i[1], caption=string, reply_markup=keyboard)
            except:
                pass
    else:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_text(chat_id=i[0], message_id=i[1], text=string, reply_markup=keyboard)
            except:
                pass

    await mess.delete()

    await state.clear()

@dp.callback_query(text_contains='confirm_purchase_')
async def confirm_purchase(callback: types.CallbackQuery):
    purchase = db.get_purchase(int(callback.data[17:]))
    sub = db.get_item(int(purchase.item_id))
    string = callback.message.html_text + '\n\n<b>✅Выполнен</b>'

    if callback.message.photo:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_caption(chat_id=i[0], message_id=i[1], caption=string, reply_markup=None)
            except:
                print(i[0])
                await callback.message.answer("Ошибка с изменением сообщения у других менеджеров. Предупредите их и свяжитесь с админом.")
                await callback.message.edit_caption(caption=string, reply_markup=None)
    else:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_text(chat_id=i[0], message_id=i[1], text=string, reply_markup=None)
            except:
                await callback.message.answer("Ошибка с изменением сообщения у других менеджеров. Предупредите их и свяжитесь с админом.")
                await callback.message.edit_text(text=string, reply_markup=None)
    
    user = db.get_user(purchase.user_id)
    upreferral = user.referal
    if purchase.coupon:
        coupon = db.get_coupon(purchase.coupon)
        coupon.count = coupon.count - 1
        db.s.commit()

    if sub.is_ref:
        if upreferral:
            upreferral = db.get_user(int(upreferral))

            # upreferral_money = db.get_user_balance(user_id=upreferral)
            upreferral_money = upreferral.balance
            upreferral_procent = upreferral.ref_procent
            upreferral_bonus = int(purchase.price * upreferral_procent)
            db.set_money(user_id=upreferral.user_id, money=upreferral_money + upreferral_bonus)
            await bot.send_message(upreferral.user_id,
                                f'<b>Ваш реферал совершил покупку!\nНа ваш счет зачисленно {upreferral_bonus}₽</b>')

    await bot.send_message(chat_id=purchase.user_id, text=f"<b>✅Заказ <code>#{purchase.id}</code> выполнен.</b>\n\n<i>Спасибо за то что воспользовались услугами нашего магазина. Присоединяйтесь в чат клиентов, будете в курсе всех предстоящих скидок в будущем.</i>\nhttps://t.me/incognito_shop_chat")
    await OrderBot.send_message(chat_id=admins_id[0], text=f"<b>✅Заказ <code>#{purchase.id}</code> выполнен.</b>") 


@dp.callback_query(text_contains='decline_purchase_')
async def decline_purchase(callback: types.CallbackQuery):
    purchase = db.get_purchase(int(callback.data[17:]))
    string = callback.message.html_text + '\n\n<b>❌Отменен</b>'

    if callback.message.photo:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_caption(chat_id=i[0], message_id=i[1], caption=string, reply_markup=None)
            except:
                await callback.message.answer("Ошибка с изменением сообщения у других менеджеров. Предупредите их и свяжитесь с админом.")
                await callback.message.edit_caption(caption=string, reply_markup=None)
    else:
        for i in [(managers[0], purchase.modder_message_id), (admins_id[0], purchase.admin_message_id), (others[0], purchase.others_message_id)]:
            try:
                await OrderBot.edit_message_text(chat_id=i[0], message_id=i[1], text=string, reply_markup=None)
            except:
                await callback.message.answer("Ошибка с изменением сообщения у других менеджеров. Предупредите их и свяжитесь с админом.")
                await callback.message.edit_text(text=string, reply_markup=None)
    
    user = db.get_user(purchase.user_id)
    user.balance = user.balance + purchase.price
    db.s.delete(purchase)
    db.s.commit()
    await bot.send_message(purchase.user_id, text=f"<b>❌Заказ <code>#{purchase.id}</code> отменен. Средства возвращены на баланс.</b>")
    await OrderBot.send_message(admins_id[0], text=f"<b>❌Заказ <code>#{purchase.id}</code> отменен. Средства возвращены на баланс.</b>")



async def anti_flood(*args, **kwargs):
    pass



async def new_top_up(username, user_id, full_name, money, item_type):
    await bot.send_message(admins_id[0],
                            f'Username: <b>@{username}</b>\nUser_id: <b>{user_id}</b>\n<i>{full_name}</i> пополнил баланс на <b>"{money}₽" на {item_type}</b>')
    await bot.send_message(managers[0],
                            f'Username: <b>@{username}</b>\nUser_id: <b>{user_id}</b>\n<i>{full_name}</i> пополнил баланс на <b>"{money}₽" на {item_type}</b>')
    await bot.send_message(others[0],
                            f'Username: <b>@{username}</b>\nUser_id: <b>{user_id}</b>\n<i>{full_name}</i> пополнил баланс на <b>"{money}₽" на {item_type}</b>')


@dp.message(commands=["start"])
async def start(message: types.Message):
    keyboard = am.start_admin_panel()
    await message.answer("Привет", reply_markup=keyboard)


async def check_purchases():
    service = db.get_service_object("manager_status")
    if service.text == "active":
        now = datetime.datetime.today()
        purchases = db.get_missed_purchases((now - datetime.timedelta(hours=2)))

        temp = []
        
        if purchases:
            for i in purchases:
                edited_time = ((now - i.datetime).seconds) // 60
                temp.append(f'Заказ <code>#{i.id}</code> - <i> прошло <b>"{edited_time // 60}:{edited_time % 60}"</b></i>')
            string = "Напоминание о невыполненных заказах:\n\n" + "\n".join(temp)
            for i in managers + admins_id:
                try:
                    await bot2.send_message(i, string)
                except:
                    pass

                
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    thread1 = Thread(target=dp.run_polling, args=(OrderBot,))
    thread1.start()
    scheduler = AsyncIOScheduler()

    job = scheduler.add_job(check_purchases, 'interval', hours=1)
    scheduler.start()

    asyncio.get_event_loop().run_forever()