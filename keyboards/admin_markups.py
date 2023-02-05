from db.db import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


db = Database()


def main_keyboard():
    rollback_btn = KeyboardButton(text="Сделать роллбэк")
    edit_panel_btn = KeyboardButton(text="Редактировать приветствие")
    check_stats_btn = KeyboardButton(text="Редактировать кнопки")

    referal_btn = KeyboardButton(text="Редактировать процент для рефералов")
    all_referal_btn = KeyboardButton(text="Задать общий процент для рефералов")

    mass_message = KeyboardButton(text="Отправить рассылку")
    del_mass_message = KeyboardButton(text="Удалить последнюю рассылку")

    coupon_menu_btn = KeyboardButton(text="🏷️Купоны")

    user_btn = KeyboardButton(text="👤Пользователь")

    wallet_btn = KeyboardButton(text="👛Кошельки")

    MainMenu = ReplyKeyboardMarkup(keyboard=[[coupon_menu_btn, user_btn],
                                            [wallet_btn],
                                            [rollback_btn],
                                             [check_stats_btn],
                                             [mass_message, del_mass_message],
                                             [KeyboardButton(text="Меню")]], resize_keyboard=True)

    return MainMenu


def wallet_keyboard():
    add_wallet = KeyboardButton(text="Добавить кошелек")
    del_wallet = KeyboardButton(text="Удалить кошелек")
    check_wallet = KeyboardButton(text="Проверить все токены")

    return ReplyKeyboardMarkup(keyboard=[[add_wallet, check_wallet, del_wallet], [KeyboardButton(text="Меню")]], resize_keyboard=True)


def blacklist_keyboard():
    markup = []

    markup.append([
        InlineKeyboardButton(text='Добавить пользователя', callback_data='add_blacklist'),
        InlineKeyboardButton(text='Удалить пользователя', callback_data='del_blacklist')])

    return InlineKeyboardMarkup(inline_keyboard=markup)


def user_keyboard():
    del_btn = KeyboardButton(text="Кикнуть пользователя из всех каналов")
    blacklist_btn = KeyboardButton(text="Cписок забаненных пользователей")

    get_user_id = KeyboardButton(text="Узнать id пользователя по никнейму")
    get_user_lc = KeyboardButton(text="Получить данные о пользователе")

    users_count = KeyboardButton(text="Кол-во пользователей")
    users_list = KeyboardButton(text="Список всех пользователй")

    get_payment = KeyboardButton(text="Получить всю информацию о пополнении")

    top_up_user = KeyboardButton(text="Пополнить баланс пользователя")
    send_message_user_btn = KeyboardButton(text="Отправить сообщение пользователю")

    return ReplyKeyboardMarkup(keyboard=[[del_btn],
                                        [blacklist_btn],
                                        [send_message_user_btn],
                                        [get_user_id, get_user_lc],
                                        [top_up_user, get_payment],
                                        [users_count, users_list],
                                        [KeyboardButton(text="Меню")]], resize_keyboard=True)


def lc_keyboard(user_id):
    purchase_history_btn = InlineKeyboardButton(text="История заказов", callback_data=f"get_ph_{user_id}")
    referral_system_btn = InlineKeyboardButton(text="Реферальная система", callback_data=f"get_rs_{user_id}")
    top_up_history_btn = InlineKeyboardButton(text="История начислений", callback_data=f"get_htu_{user_id}")

    
    markup = InlineKeyboardMarkup(inline_keyboard=[[purchase_history_btn], [top_up_history_btn]])

    return markup


def coupon_menu_keyboard():
    add_coupon = KeyboardButton(text="Добавить промокод")
    del_coupon = KeyboardButton(text="Удалить промокод")

    add_linked_coupon = KeyboardButton(text="Создать ссылку с купоном")
    del_linked_coupon = KeyboardButton(text="Удалить ссылку с купоном")

    return ReplyKeyboardMarkup(keyboard=[[add_coupon, del_coupon],
                                        [add_linked_coupon, del_linked_coupon],
                                        [KeyboardButton(text="Меню")]], resize_keyboard=True)


def choose_is_coupon_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Верно", callback_data="True"), InlineKeyboardButton(text="Нет", callback_data="False")]])

    return markup


def delete_link_coupon():
    markup = []

    markup.append([
        InlineKeyboardButton(text='Список купонов', callback_data='link_coupon_list'),
        InlineKeyboardButton(text='Отмена', callback_data='just_cancel')])

    return InlineKeyboardMarkup(inline_keyboard=markup)
    

def choose_link_coupon_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Скидка", callback_data="discount"), InlineKeyboardButton(text="Пополнение баланса", callback_data="balance")]])

    return markup



def del_it_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нет, отменить удаление", callback_data="decline"), InlineKeyboardButton(text="Да, удалить!", callback_data="confirm")]])

    return markup


def start_admin_panel():
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Выгрузить базу данных в excel")]], resize_keyboard=True)

    return markup


def mass_message_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отзывы💌", url="https://t.me/umskulotzivi"),  InlineKeyboardButton(text="Менеджер🙍‍♂️", url="https://t.me/UmHelper")]])

    return markup


def choose_mm_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да,  посмотреть превью.", callback_data="preview"), InlineKeyboardButton(text="Нет, отправить рассылку сразу.", callback_data="send")], [InlineKeyboardButton(text="Назад", callback_data="just_cancel")]])

    return markup
def edit_buttons():

    markup=[[
        InlineKeyboardButton(text='Кнопка "Менеджер"', callback_data="edit_manager_btn")
    ], [
        InlineKeyboardButton(text='Кнопка "Отзывы"', callback_data="edit_rekv_btn")
    ], [
        InlineKeyboardButton(text='Кнопка "Общая группа"', callback_data="edit_group_btn")
    ]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)

    return markup


def edit_buy_course(item):
    item = str(item)
    obj = db.get_item(item)
    markup = [
        [InlineKeyboardButton(text="Редактировать название", callback_data=f"edit_i_n_{str(item)}")],
        [InlineKeyboardButton(text="Редактировать описание", callback_data=f"edit_des_{str(item)}")],
        [InlineKeyboardButton(text="Редактировать фото", callback_data=f"edit_ph_{str(item)}")],
        [InlineKeyboardButton(text="Редактировать цену", callback_data=f"edit_pr_{str(item)}")],
        [InlineKeyboardButton(text="Редактировать chat id", callback_data=f"edit_chat_id_{str(item)}")],
        [InlineKeyboardButton(text=f"На товар действуют скидки: {obj.is_coupon}", callback_data=f"edit_i_coup_{item}")],
        [InlineKeyboardButton(text=f"Товар учавствует в реферальной системе: {obj.is_ref}", callback_data=f"edit_i_ref_{item}")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"del_it_{str(item)}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"cancel_{str(item)}")]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)

    return markup


def cancel_edit_course_keyboard(item):
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"cancel_{item}")]])
    return markup


def cancel_add_course_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="just_cancel")]])
    return markup


def cancel_add_item_photo_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Пропустить", callback_data="skip_photo")
    ],[
        InlineKeyboardButton(text="Назад", callback_data="just_cancel")
    ]])

    return markup


def delete_coupon():
    markup = []

    markup.append([
        InlineKeyboardButton(text='Список промокодов', callback_data='coupon_list'),
        InlineKeyboardButton(text='Отмена', callback_data='just_cancel')])

    return InlineKeyboardMarkup(inline_keyboard=markup)


def confirm_adding_keyboard():
    markup=[[
        InlineKeyboardButton(text="Подтвердить", callback_data="confirm")
    ], [
        InlineKeyboardButton(text="Отмена", callback_data="cancel_add_course")
    ]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)

    return markup


def lCabinet(user_id):
    markup = InlineKeyboardMarkup(row_width=2)

    purchase_history_btn = InlineKeyboardButton(text="История заказов", callback_data=f"purchase_history_{user_id}")
    personal_discount_btn = InlineKeyboardButton(text="Личная скидка", callback_data=f"personal_discount_{user_id}")
    referral_system_btn = InlineKeyboardButton(text="Реферальная система", callback_data=f"referral_system_{user_id}")
    top_up_history_btn = InlineKeyboardButton(text="История начислений", callback_data=f"top_up_history_{user_id}")

    markup=[purchase_history_btn], [personal_discount_btn], [referral_system_btn], [top_up_history_btn]

    return markup


def referral_system_keyboard(user_id):
    referral_list_button = InlineKeyboardButton(text="Список рефералов", callback_data=f"referral_list_{user_id}")

    markup = InlineKeyboardMarkup(inline_keyboard=[[referral_list_button]])

    return markup


def manager_keyboard():
    markup = [[
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_manager_btn_text')
    ,
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_manager_btn_link')
    ]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)
    return markup


def group_keyboard():
    markup = [[
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_group_btn_text')
    ,
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_group_btn_link')
    ]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)
    return markup


def rekv_keyboard():
    markup = [[
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_rekv_btn_text')
    ,
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_rekv_btn_link')
    ]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)
    return markup


def reviews_keyboard():
    markup = [[
        InlineKeyboardButton(text='Редактировать надпись', callback_data='edit_reviews_btn_text')
    ,
        InlineKeyboardButton(text='Редактировать ссылку', callback_data='edit_reviews_btn_link')
    ]]


    markup = InlineKeyboardMarkup(inline_keyboard=markup)
    return markup


def edit_buy_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)

    add_course = InlineKeyboardButton(text='$ Добавить курс $', callback_data='add_course')
    del_course = InlineKeyboardButton(text='$ Удалить курс $', callback_data='del_course')

    markup.row(add_course, del_course)

    return markup


def edit_help_keyboard():
    edit_admin_btn = InlineKeyboardButton(text='Редактировать кнопку "Админа"', callback_data='edit_admin_btn')
    edit_reviews_btn = InlineKeyboardButton(text='Редактировать кнопку "Отзывы"', callback_data='edit_reviews_btn')
    edit_group_btn = InlineKeyboardButton(text='Редактировать кнопку "Общая группа"', callback_data='edit_group_btn')

    markup = [[edit_admin_btn], [edit_reviews_btn], [edit_group_btn]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)
    return markup


def edit_chat_keyboard():
    edit_chat_btn = InlineKeyboardButton(text='Редактировать кнопку чата', callback_data='edit_chat_btn')
    edit_group_btn = InlineKeyboardButton(text='Редактировать кнопку группы', callback_data='edit_group_btn')

    markup = [[edit_chat_btn, edit_group_btn]]

    markup = InlineKeyboardMarkup(inline_keyboard=markup)

    return markup


def cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="just_cancel")]])