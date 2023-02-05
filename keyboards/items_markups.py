from ast import Call
from datetime import datetime
from unicodedata import category

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.callback_data import CallbackData
from db.db import Database
from db.objects import Item, SpecialCourse

db = Database()


subjects = {"1": "РУССКИЙ ЯЗЫК🖌️",
            "2": "ПРОФ🧮",
            "3": "БАЗА📐",
            "4": "ФИЗИКА🔭",
            "5": "ОБЩЕСТВОЗНАНИЕ⚖️",
            "6": "ИСТОРИЯ🏛️",
            "7": "БИОЛОГИЯ🧬",
            "8": "ХИМИЯ🧪",
            "9": "ЛИТЕРАТУРА📚",
            "10": "АНГЛИЙСКИЙ ЯЗЫК🖍",
            "11": "ИНФОРМАТИКА🖥",
            "12": "ГЕОГРАФИЯ🗺️"}

subjects_oge = {"1": "РУССКИЙ ЯЗЫК🖌️",
                "15": "МАТЕМАТИКА📐",
                "5": "ОБЩЕСТВОЗНАНИЕ⚖️",
                "7": "БИОЛОГИЯ🧬",
                "8": "ХИМИЯ🧪",
                "10": "АНГЛИЙСКИЙ ЯЗЫК🖍"}

subjects_flash = {"1": "РУССКИЙ ЯЗЫК🖌️",
                "15": "МАТЕМАТИКА📐",
                "8": "ХИМИЯ🧪",
                "10": "АНГЛИЙСКИЙ ЯЗЫК🖍"}

categories = {
                # "1": "Сентябрь",
              # "2": "Октябрь",
              # "3": "Ноябрь",
              "9": "Декабрь",
              "8": "Январь",
              "7": "Февраль",
              "6": "Март",
              "5": "Апрель"
              # "4": "Май"
              }

subcategories = {"1": "ЕГЭ",
                 "2": "ОГЭ"}

subcategories_january = {
    "5": "Годовые ЕГЭ",
    "4": "Полугодовые ЕГЭ",
    "2": "ОГЭ"
}

subcategories_february = {
    "1": "ЕГЭ",
    "7": "НЕО УМСКУЛ",
    "2": "ОГЭ"
}

all_subjects = {"1": "РУССКИЙ ЯЗЫК🖌️",
            "2": "ПРОФ🧮",
            "3": "БАЗА📐",
            "4": "ФИЗИКА🔭",
            "5": "ОБЩЕСТВОЗНАНИЕ⚖️",
            "6": "ИСТОРИЯ🏛️",
            "7": "БИОЛОГИЯ🧬",
            "8": "ХИМИЯ🧪",
            "9": "ЛИТЕРАТУРА📚",
            "10": "АНГЛИЙСКИЙ ЯЗЫК🖍",
            "11": "ИНФОРМАТИКА🖥",
            "12": "ГЕОГРАФИЯ🗺️",
            "15": "МАТЕМАТИКА📐"
}


class buy_item_cd(CallbackData, prefix="buy_item"):
    user_id: int
    item_id: int
    price: int


class menu_cd(CallbackData, prefix="Menu"):
    lvl: int # level
    p: int # precategory
    c: int # category
    s: int # subcategory
    j: int # subject
    i:int # item


def make_callback_data(level=1, precategory=0, category=0, subcategory=0, subject=0,  item=0):
    return menu_cd(lvl=level, p=precategory, c=category, s=subcategory, j=subject, i=item)


async def precategory_keyboard(admin=False):
    CURRENT_LEVEL = 0

    markup = [[
        InlineKeyboardButton(text='Курсы за 2022-2023', callback_data=make_callback_data(level=CURRENT_LEVEL + 1, precategory=2).pack()),
        InlineKeyboardButton(text='Курсы за 2021-2022', callback_data=make_callback_data(level=CURRENT_LEVEL + 1, precategory=1).pack())
    ]]

    # if admin:
    markup.append([InlineKeyboardButton(text='Кураторы', callback_data=f"sp_cat_10")])

    markup.append([InlineKeyboardButton(text="Закрыть🚫", callback_data=make_callback_data(level=CURRENT_LEVEL - 1).pack())])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=markup
    )

    return keyboard


async def category_keyboard(precategory, admin=False):
    CURRENT_LEVEL = 1
    markup = []

    k = 0
    temp = []
    
    categories = [i[1] for i in sorted([(i.id, i) for i in db.get_categories(precategory)], key=lambda x: x[0])]

    for i in categories:
        category_id, category_name = i.id, i.name
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=int(precategory), category=category_id)

        if category_id == 10 or category_id == 11:
            continue
        
        k += 1
        temp.append(
            InlineKeyboardButton(text=str(category_name), callback_data=callback_data.pack())
        )

        if k % 3 == 0:
            markup.append(temp)
            temp = []


    if temp:
        markup.append(temp)

    if precategory == 1:
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=11)
        markup.append([
            InlineKeyboardButton(text="ПРЕДБАННИК", callback_data=callback_data.pack())
        ])

    markup.append([
        InlineKeyboardButton(text="Специальные курсы", callback_data=f"specials_{precategory}")
    ])
    
    if admin:
        markup.append([InlineKeyboardButton(text="$ Создать категорию $", callback_data=f"create_category_{precategory}")])
        markup.append([InlineKeyboardButton(text="$ Редактировать главную картинку $", callback_data="edit_main_image")])
        markup.append([InlineKeyboardButton(text="$ Удалить главную картинку $", callback_data="del_main_image")])

    markup.append([InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1).pack())])
        
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=markup
    )

    return keyboard


async def subcategory_keyboard(precategory, category, admin=False):
    CURRENT_LEVEL = 2
    markup = []

    if category == 5:
        markup.append([
            InlineKeyboardButton(text="Годовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="5").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="Полугодовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="168").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="2").pack())
        ])

    elif category == 81:
        markup.append([
            InlineKeyboardButton(text="Годовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="5").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="Полугодовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="168").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="2").pack())
        ])

    elif category == 82:
        markup.append([
            InlineKeyboardButton(text="Годовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="5").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="Полугодовые ЕГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="168").pack())
        ])
        
        markup.append([
            InlineKeyboardButton(text="ОГЭ", callback_data=make_callback_data(level=CURRENT_LEVEL + 1,
                                                                                      precategory=precategory,
                                                                                      category=category,
                                                                                      subcategory="2").pack())
        ])

    else:
        for i in db.get_subcategories(precategory, category):
            subcategory_id, subcategory_name = i.id, i.name
            if subcategory_id in [5, 168]:
                continue
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory_id)

            markup.append(
                [InlineKeyboardButton(text=subcategory_name, callback_data=callback_data.pack())]
            )

    if admin:
        markup.append([
            InlineKeyboardButton(text="$ Добавить картинку $",
                                callback_data=f"add_category_photo_{category}")
       ])


        markup.append([
            InlineKeyboardButton(text="$ Изменить название категории $",
                                callback_data=f"rename_category_{category}")
       ])

        markup.append([
            InlineKeyboardButton(text="$ Получить ссылку на категорию $", callback_data=f"get_link_ctg_{category}")
        ])


        markup.append([
            InlineKeyboardButton(text="$ Удалить категорию $",
                                callback_data=f"del_category_{category}")
        ])

    if category == 10:
        markup.append(
        [InlineKeyboardButton(text="Вернуться◀️",
                                callback_data=f"specials_{precategory}")]
    )
    else:
        markup.append(
        [InlineKeyboardButton(text="Вернуться◀️",
                                callback_data=make_callback_data(level=CURRENT_LEVEL - 1, precategory=precategory, category=category).pack())]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=markup
    )

    return keyboard


async def subject_keyboard(precategory, category, subcategory, admin=False):
    CURRENT_LEVEL = 3
    markup = []
    global subjects_oge

    if subcategory == 2 and category == 10:
        global subjects_flash
        for subject_id, subject_name in subjects_flash.items():
            if subject_name == "АНГЛИЙСКИЙ ЯЗЫК📓":
                callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                                   subject=subject_id)

                markup.append([
                    InlineKeyboardButton(text=subject_name, callback_data=callback_data.pack())
                ])
    elif category == 13 and precategory == 2 and (subcategory == 2 or subcategory == 8):
        for subject_id, subject_name in subjects_oge.items():
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                               subject=subject_id)

            markup.append([
                InlineKeyboardButton(text=subject_name, callback_data=callback_data.pack())
            ])
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                            subject=10)

        markup.append([
                InlineKeyboardButton(text="АНГЛИЙСКИЙ ЯЗЫК📓", callback_data=callback_data.pack())
            ])
    elif subcategory == 2 or subcategory == 8:
        for subject_id, subject_name in subjects_oge.items():
            if (subject_name == "ХИМИЯ🧪" and category in [9]) or (category == 11 and subcategory == 2 and subject_id == 5) or (category == 15 and subject_id == 8):
                continue
            else:
                callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                                   subject=subject_id)

                markup.append([
                    InlineKeyboardButton(text=subject_name, callback_data=callback_data.pack())
                ])
        if category == 11:
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                                subject=5)

            markup.append([
                    InlineKeyboardButton(text="ОБЩЕСТВОЗНАНИЕ📒", callback_data=callback_data.pack())
                ])
        if category == 14 and subcategory == 2:
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                                   subject=10)

            markup.append([
                InlineKeyboardButton(text="АНГЛИЙСКИЙ ЯЗЫК📓", callback_data=callback_data.pack())
            ])


    else:
        global subjects
        for subject_id, subject_name in subjects.items():
            if (category == 1 and subcategory == 1 and subject_id == 12):
                continue
            callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory,
                                               subject=int(subject_id))

            markup.append([
                InlineKeyboardButton(text=subject_name, callback_data=callback_data.pack())
            ])

    if admin:
        markup.append([
            InlineKeyboardButton(text="$ Получить ссылку на подкатегорию $", callback_data=f"get_link_sub_{category}-{subcategory}")
        ])

    markup.append([
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=CURRENT_LEVEL - 1, precategory=precategory, category=category,
                                                              subcategory=subcategory).pack())
    ])
    return InlineKeyboardMarkup(inline_keyboard=markup)


async def items_keyboard(precategory, category, subcategory, subject, admin=False):
    CURRENT_LEVEL = 4
    markup = []

    # items = [i[1] for i in sorted([(i.id, i) for i in db.get_items(precategory, category, subcategory, subject)], key=lambda x: x[0])]
    items = []
    for i in sorted([(i.id, i) for i in db.get_items(precategory, category, subcategory, subject)], key=lambda x: x[0]):
        if not("вебиум" in i[1].name.lower()):
            items.append(i[1])
        else:
            items.insert(1, i[1])


    if not items and not admin:
        return False

    for item in items:
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, precategory=precategory, category=category, subcategory=subcategory, subject=subject, item=item.id)
        markup.append([
            InlineKeyboardButton(text=f'{item.name}', callback_data=callback_data.pack())
        ])
    

    if admin:
        markup.append([
            InlineKeyboardButton(text="$ Добавить товар $", callback_data=f"add_item_{precategory}:{category}:{subcategory}:{subject}")
        ])

        markup.append([
            InlineKeyboardButton(text="$ Получить ссылку на предмет $", callback_data=f"get_link_sj_{category}-{subcategory}-{subject}")
        ])


    if subject == '14':
        markup.append([
        InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
            level=CURRENT_LEVEL - 2, precategory=precategory, category=str(category), subcategory=str(subcategory)).pack())
        ])
    else:
        markup.append([
        InlineKeyboardButton(text="Вернуться◀️", callback_data=make_callback_data(
            level=CURRENT_LEVEL - 1, precategory=precategory, category=str(category), subcategory=str(subcategory)).pack())
        ])

        markup.append([
                InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data="menu")
            ])
    


    return InlineKeyboardMarkup(inline_keyboard=markup)


def item_keyboard(item, user_id, admin=False):
    CURRENT_LEVEL = 5
    markup = []

    ids, price = item.id, item.price
    if not isinstance(item, Item):
        ids = -ids
    callback_data = buy_item_cd(user_id=user_id, item_id=ids, price=price)

    markup.append([
        InlineKeyboardButton(text=f'Купить', callback_data=callback_data.pack())
    ])

    if admin:
        markup.append(
                [InlineKeyboardButton(text=f'$ Редактировать $', callback_data=f"edit_item_{ids}")]
        )

    if isinstance(item, Item):
        markup.append([
            InlineKeyboardButton(text=f'Вернуться◀️', callback_data=make_callback_data(
                level=CURRENT_LEVEL - 1, precategory=item.precategory, category=item.category, subcategory=item.subcategory, subject=item.subject).pack())
        ])
    else:
        markup.append([
            InlineKeyboardButton(text=f'Вернуться◀️', callback_data=f"sp_cat_{item.category_name}")
        ])

    markup.append(
            [InlineKeyboardButton(text=f'Назад к категориям🚫', callback_data="menu")]
        )

    return InlineKeyboardMarkup(inline_keyboard=markup)



async def specials_keyboard(admin=False, precategory=1):
    markup = []

    if precategory == 1:

        callback_data = make_callback_data(level=2, precategory=1, category=10)

        markup.append([
            InlineKeyboardButton(text="ФЛЭШ УМСКУЛ (45 ДНЕЙ)", callback_data=callback_data.pack())
        ])

        specials = [(1, "Рулетки Умскул"), (2, "ПОТНЫЙ МАРАФОН (90 дней)"), (3, "ФЛЭШ УМСКУЛ (45 ДНЕЙ)"), (6, "ВЕБИУМ ПРОКАЧКА (45 ДНЕЙ)")]

        for category_id, category_name in specials:
            if category_id == 3 or category_id == 7:
                continue

            markup.append([
                InlineKeyboardButton(text=category_name, callback_data=f"sp_cat_{category_id}")
            ])

        if admin:
            markup.append([
                    InlineKeyboardButton(text="$ Получить ссылку на Спец. категорию $", callback_data=f"get_link_spctg_{precategory}")
                ])

        markup.append([
            InlineKeyboardButton(text="Вернуться◀️",
                callback_data=make_callback_data(level=1, precategory=1).pack())
                    ])
    else:
        markup.append([
                InlineKeyboardButton(text="💯 100Бальный", callback_data=f"sp_cat_9")
            ])

        for i in db.get_special_courses():
            category_id, category_name = i.id, i.name
            if category_id in [1, 2, 3, 4, 5, 6, 9, 10]:
                continue

            markup.append([
                InlineKeyboardButton(text=category_name, callback_data=f"sp_cat_{category_id}")
            ])

        if admin:
            markup.append([
                InlineKeyboardButton(text="$ Добавить специальную категорию $", callback_data="create_speacial")
            ])

            markup.append([
                    InlineKeyboardButton(text="$ Получить ссылку на Спец. категорию $", callback_data=f"get_link_spctg_{precategory}")
                ])

        markup.append([
            InlineKeyboardButton(text="Вернуться◀️",
                                callback_data=make_callback_data(level=1, precategory=2).pack())
        ])

    return InlineKeyboardMarkup(inline_keyboard=markup)


async def special_items_keyboard(sp_ids, admin=False):
    markup = []

    for i in db.get_special_items(int(sp_ids)):

        ids, name, price = i.id, i.name, i.price
        # markup.append(
        #     InlineKeyboardButton(text=f"{name} | {price}", callback_data=f"sp_itm_{ids}")
        # )
        if ids in [61, 70]:
            markup.insert(0, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids in [62, 50]:
            markup.insert(1, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids in [63, 51]:
            markup.insert(2, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids in [64, 52]:
            markup.insert(3, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids in [65, 71]:
            markup.insert(4, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids == 66:
            markup.insert(5, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids == 67:
            markup.insert(6, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids == 68:
            markup.insert(7, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        elif ids == 69:
            markup.insert(8, [
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])
        else:
            markup.append([
                InlineKeyboardButton(text=f"{name}", callback_data=f"sp_itm_{ids}")
            ])

    if admin:
        markup.append([
            InlineKeyboardButton(text="$ Добавить курс $", callback_data=f"add_item_-{sp_ids}")
        ])
        
        markup.append([
            InlineKeyboardButton(text="$ Добавить изображение $", callback_data=f"add_special_course_image_{sp_ids}")
        ])

        markup.append([
                InlineKeyboardButton(text="$ Изменить название специальной категории $", callback_data=f"rename_special_{sp_ids}")
            ])

        markup.append([
                    InlineKeyboardButton(text="$ Получить ссылку на Спец. курс $", callback_data=f"get_link_spsub_{sp_ids}")
                ])

        markup.append([
            InlineKeyboardButton(text="$ Удалить специальную категорию $", callback_data=f"del_sp_{sp_ids}")
        ])

    if int(sp_ids)  in [1, 2, 3, 4, 5, 6]:
        precategory = 1
    else:
        precategory = 2


    if int(sp_ids) == 10:
        markup.append([
                    InlineKeyboardButton(text="Вернуться◀️",
                                         callback_data=make_callback_data(level=0).pack())
                ])
    elif int(sp_ids) in [4]:
        markup.append([
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=2, precategory=1, category=5).pack())
    ])
    elif int(sp_ids) in [5]:
        markup.append([
        InlineKeyboardButton(text="Вернуться◀️",
                             callback_data=make_callback_data(level=2, precategory=2, category=81).pack())
    ])
    else:
        markup.append([
            InlineKeyboardButton(text="Вернуться◀️",
                                 callback_data=f"specials_{precategory}")
        ])

    return InlineKeyboardMarkup(inline_keyboard=markup)


async def halfyear_courses_keyboard(precategory=4):
    CURRENT_LEVEL = 3
    markup = []
    courses = db.get_special_items(precategory)
    for i in courses:
        ids, name, price = i.id, i.name, i.price
        # markup.row(InlineKeyboardButton(text=f'{name} | {price}₽', callback_data=f"halfyear_course_{ids}"))
        markup.append([InlineKeyboardButton(text=f'{name}', callback_data=f"sp_itm_{ids}")])
    markup.append(
        [InlineKeyboardButton(text="Вернуться◀️",
                                     callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category="5" if precategory == 4 else 81).pack())]
    )



    return InlineKeyboardMarkup(inline_keyboard=markup)
