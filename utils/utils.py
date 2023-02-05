from aiogram.dispatcher.filters.state import State, StatesGroup
import aiohttp


discount_levels = {
    'Без скидок': [0, 0],
    'Школьник': [850, 5],
    'Студентик': [1400, 10],
    'Магистр': [1700, 15]
}


class States(StatesGroup):
    DEFAULT_STATE = State()
    PAYMENT_STATE = State()
    COUPONS_STATE = State()


class EDIT_PANEL(StatesGroup):
    DEL_WALLET = State()
    ADD_WALLET_NUM = State()
    ADD_WALLET_P2P = State()
    ADD_WALLET_API = State()
    CREATE_CATEGORY = State()
    CREATE_SUBCATEGORY = State()
    CREATE_SPECIAL = State()
    DEL_SPECIAL = State()

    RENAME_CATEGORY = State()
    RENAME_SUBCATEGORY = State()
    RENAME_SPECIAL = State()
    
    EDIT_START = State()

    EDIT_QIWI_TOKEN = State()
    EDIT_MAIN_IMAGE = State()
    EDIT_GOLD_PRICE = State()

    EDIT_REFERAL_PROCENT = State()
    EDIT_REFERAL_PROCENT_USER_ID = State()
    EDIT_ALL_REFERAL_PROCENT = State()

    ADD_CATEGORY_IMAGE = State()
    ADD_SUBCATEGORY_IMAGE = State()
    
    ADD_SUBCATEGORY = State()

    ADD_ITEM = State()
    ADD_ITEM_NAME = State()
    ADD_ITEM_DESCRIPTION = State()
    ADD_ITEM_PHOTO = State()
    ADD_ITEM_PRICE = State()
    ADD_ITEM_CHAT_ID = State()
    ADD_SPECIAL_COURSE_IS_ADD = State()
    EDIT_ITEM = State()
    EDIT_ITEM_NAME = State()
    EDIT_ITEM_DESCRIPTION = State()
    EDIT_ITEM_IMAGE = State()
    EDIT_ITEM_PRICE = State()
    EDIT_ITEM_CHAT_ID = State()
    DEL_ITEM = State()

    EDIT_REKV_BTN = State()
    EDIT_REKV_BTN_TEXT = State()
    EDIT_REKV_BTN_LINK = State()

    EDIT_GROUP_BTN = State()
    EDIT_GROUP_BTN_TEXT = State()
    EDIT_GROUP_BTN_LINK = State()

    ADD_COUPON_TEXT = State()
    ADD_COUPON_COUNT = State()
    ADD_COUPON_DATE = State()

    ADD_SPECIAL_COURSE_NAME = State()
    ADD_SPECIAL_COURSE_DESCRIPTION = State()
    ADD_SPECIAL_COURSE_PHOTO = State()
    ADD_SPECIAL_COURSE_PRICE = State()
    ADD_SPECIAL_IS_COUPON = State()
    ADD_SPECIAL_COURSE_IS_REF = State()
    ADD_SPECIAL_COURSE_CHAT_ID = State()
    ADD_SPECIAL_COURSE_CONFIRM = State()
    
    CREATE_SPECIAL_COURSE = State()
    ADD_SPECIAL_COURSE_IMAGE = State()
    DEL_SPECIAL_COURSE = State()

    EDIT_MANEGER_BTN = State()
    EDIT_MANEGER_BTN_LINK = State()
    EDIT_MANEGER_BTN_TEXT = State()

    EDIT_REVIEWS = State()
    EDIT_REVIEWS_TEXT = State()
    EDIT_REVIEWS_LINK = State()

    GET_USER_ID_FROM_USERNAME = State()
    EDIT_RUBUSD_COURSE = State()
    EDIT_COST_PRICE = State()

    EDIT_DEF_COST = State()

    DEL_CATEGORY = State()
    DEL_SUBCATEGORY = State()
    DEL_IT = State()

    CONFIRM_DEL_IT = State()
    SEND_MESSAGE_TO = State()

    ADD_MODDING_CHAT = State()
    DEL_MODDING_CHAT = State()

    ADD_SPAM_CHAT = State()
    DEL_SPAM_CHAT = State()
    EDIT_SPAM_MESSAGE = State()
    
class BLACKLIST_EDIT(StatesGroup):
    ADD_BLACKLIST = State()
    DEL_BLACKLIST = State()
    KICK_USER = State()


class COUPONS_EDIT(StatesGroup):
    ADD_COUPON_TEXT = State()
    ADD_COUPON_COUNT = State()
    ADD_COUPON_PROC = State()
    ADD_COUPON_TIME = State()
    DEL_COUPON = State()

    ADD_LINK_COUPON_USER_COUNT = State()
    ADD_LINK_COUPON_TEXT = State()
    ADD_LINK_COUPON_COUNT = State()
    ADD_LINK_COUPON_PROC = State()
    ADD_LINK_COUPON_TIME = State()
    ADD_LINK_COUPON_CHOOSE_TYPE = State()
    DEL_LINK_COUPON = State()


class MASS_MESSAGE(StatesGroup):
    SEND_MASS_MESSAGE_PHOTO = State()
    SEND_MASS_MESSAGE = State()
    DEL_MASS_MESSAGE = State()
    CHOOSE = State()


class OTHERS_STATES(StatesGroup):
    GET_NICKNAME = State()
    GET_NICKNAME_PHOTO = State()

    GET_PAYMENT_ID = State()
    GET_PAYMENT_BILL_ID = State()
    GET_USER_ID = State()
    GET_MONEY = State()

    GET_USER_LC = State()
    GET_MESSAGE_USER_ID = State()
    GET_MESSAGE_TEXT = State()

def calculate_personal_discount(discount_levels: dict, sum_of_purchases: int):
    last = []
    for x, y in discount_levels.items():
        if sum_of_purchases >= y[0]:
            last = [x, y[1]]
        else:
            return last
    return last


async def isgood_qiwi_wallet(token):
        profileUrl = 'https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true'

        headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    }

        async with aiohttp.ClientSession() as client:
            async with client.get(url=profileUrl, headers=headers) as response:
                if response.status != 200:
                    return False
                responseJson = await response.json()
                return not(responseJson['contractInfo']['blocked'])


async def get_qiwi_balance(number, token):
    balanceUrl = f'https://edge.qiwi.com/funding-sources/v2/persons/{number}/accounts'

    headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }

    async with aiohttp.ClientSession() as client:
        async with client.get(url=balanceUrl, headers=headers) as response:
            if response.status != 200:
                return(response.status)

            responseJson = await response.json()
            return(responseJson['accounts'][0]['balance']['amount'])