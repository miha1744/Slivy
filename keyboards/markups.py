from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.callback_data import CallbackData
from db.db import Database

db = Database()


def main_keyboard(admin=False, manager=False, editors=False):
    keyboard = []

    buy_btn = KeyboardButton(text="Купить курсы")
    top_up_balance_btn = KeyboardButton(text="Пополнить баланс")
    lc_btn = KeyboardButton(text="Личный кабинет")
    free_btn = KeyboardButton(text="Бесплатные курсы")
    help_btn = KeyboardButton(text="Помощь")
    group_btn = KeyboardButton(text="Общая группа")

    keyboard = keyboard + [[buy_btn, top_up_balance_btn], [lc_btn, free_btn], [help_btn, group_btn]]

    if admin:
        keyboard.append(
            [KeyboardButton(text="Админ")]
        )

    markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    return markup


def get_money_keyboard():
    btn_200 = InlineKeyboardButton(text="200₽", callback_data="get_money_200")
    btn_250 = InlineKeyboardButton(text="250₽", callback_data="get_money_250")
    btn_300 = InlineKeyboardButton(text="300₽", callback_data="get_money_300")
    btn_350 = InlineKeyboardButton(text="350₽", callback_data="get_money_350")
    btn_400 = InlineKeyboardButton(text="400₽", callback_data="get_money_400")
    btn_450 = InlineKeyboardButton(text="450₽", callback_data="get_money_450")
    btn_500 = InlineKeyboardButton(text="500₽", callback_data="get_money_500")
    btn_600 = InlineKeyboardButton(text="600₽", callback_data="get_money_600")
    btn_800 = InlineKeyboardButton(text="800₽", callback_data="get_money_800")

    cancel_btn = InlineKeyboardButton(text="Отмена", callback_data=f"just_cancel")

    markup = InlineKeyboardMarkup(
                inline_keyboard=[[btn_200, btn_250, btn_300],
                                 [btn_350, btn_400, btn_450],
                                 [btn_500, btn_600, btn_800],
                                 [cancel_btn]]
            )

    return markup



def free_course_keyboard(admin=False):
    markup = []

    # courses = db.get_free_courses()
    # for course in courses:
    #     name = course[1]
    #     link = course[2]
    #     markup.row(
    #         InlineKeyboardButton(text=name, url=link)
    #     )
    markup.append([InlineKeyboardButton(text="Бесплатные курсы", url="https://t.me/+MKLRbMqJiAM5YWJi")])

    # if admin:
    #     markup.row(InlineKeyboardButton(text='$ Добавить бесплатный курс $', callback_data='add_free_course')
    #                ).row(InlineKeyboardButton(text='$ Удалить бесплатный курс $', callback_data='del_free_course'))
    return InlineKeyboardMarkup(inline_keyboard=markup)

def start_keyboard():
    markup = [[InlineKeyboardButton(text="Инструкция к боту", url="https://telegra.ph/Instrukciya-k-botu-05-12"), InlineKeyboardButton(text="Соглашение", url="https://telegra.ph/Soglashenie-05-12-3")]]

    return InlineKeyboardMarkup(inline_keyboard=markup)


def payment_keyboard(isUrl=True, url='', bill_id="", wallet_num='0'):
    markup = []

    if isUrl:
        pay_btn = InlineKeyboardButton(text='💳 перейти к оплате', url=url)
        markup.append([pay_btn])
    check_payment_btn = InlineKeyboardButton(text='✅Я оплатил!', callback_data=f"{wallet_num}_check_top_up_{bill_id}")
    cancel_payment_btn = InlineKeyboardButton(text='❌Передумал оплачивать',
                                              callback_data=f"cancel_payment_{bill_id}")

    markup.append([check_payment_btn])
    markup.append([cancel_payment_btn])
    return InlineKeyboardMarkup(inline_keyboard=markup)

def check_subscribe_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал 🔑", url='https://t.me/+GfZ-BEPMxrhmZmIy')], 
                                                [InlineKeyboardButton(text="Проверить подписку ✅", callback_data='check_subscribe')]])
    


def lc_keyboard(admin=False):
    purchase_history_btn = InlineKeyboardButton(text="История заказов", callback_data="purchase_history")
    personal_discount_btn = InlineKeyboardButton(text="Личная скидка", callback_data="personal_discount")
    referral_system_btn = InlineKeyboardButton(text="Реферальная система", callback_data="referal_system")
    top_up_btn = InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up")
    top_up_history_btn = InlineKeyboardButton(text="История начислений", callback_data="history_top_up")
    coupon_activator_btn = InlineKeyboardButton(text="Активировать промокод", callback_data="coupon_activator")

    
    markup = InlineKeyboardMarkup(
    inline_keyboard=[[purchase_history_btn, top_up_history_btn],
                     [referral_system_btn, top_up_btn],
                     [coupon_activator_btn],
                     [personal_discount_btn]]
    )

    return markup


def referral_system_keyboard():

    referral_list_button = InlineKeyboardButton(text="Список рефералов", callback_data="referral_list")
    referral_link_button = InlineKeyboardButton(text="Получить ссылку отдельным сообщением", callback_data="referral_link")

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[referral_list_button, referral_link_button]]
    )

    return markup


def help_keyboard():

    manager = db.get_service_object("manager_btn")
    rekv = db.get_service_object("rekv_btn")

    admin_btn = InlineKeyboardButton(text=manager.text, url=manager.link)
    Reviews_Btn = InlineKeyboardButton(text=rekv.text, url=rekv.link)
    rekv_btn = InlineKeyboardButton(text='РЕКВИЗИТЫ', url='https://t.me/vipumskul/4')
    inst_btn = InlineKeyboardButton(text="Инструкция к боту", url="https://telegra.ph/Instrukciya-k-botu-05-12")
    agree_btn = InlineKeyboardButton(text="Соглашение", url="https://telegra.ph/Soglashenie-05-12-3")

    

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[admin_btn, Reviews_Btn, rekv_btn],
                         [inst_btn, agree_btn]]
    )

    return markup
    

def not_enough_balance():
    top_up_btn = InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up")

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[top_up_btn]]
    )

    return markup


def group_keyboard():
    group = db.get_service_object("group_btn")

    group_btn = InlineKeyboardButton(text=group.text, url=group.link)
    chat_btn = InlineKeyboardButton(text="Чат", url="https://t.me/+KLtDaGzr_JFkODcy")
    

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[group_btn, chat_btn]]
    )

    return markup