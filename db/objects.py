from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import REAL, BigInteger, create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects import postgresql
import datetime

DeclarativeBase = declarative_base()

class AddingSpecialItem:

    def __init__(self, id=None, special_category=None, category_name=None, name=None, description=None, photo=None, price=None):
        self.id = ''
        self.special_category = ''
        self.category_name = ''
        self.name = ''
        self.description = ''
        self.photo = ''
        self.price = ''
        self.chat_id = ''
        self.is_ref = ''
        self.is_coupon = ''


class AddingItem:

    def __init__(self, id=None, special_category=None, category_name=None, name=None, description=None, photo=None, price=None):
        id = ''
        precategory = ''
        category = ''
        subcategory = ''
        subject = ''
        name = ''
        description = ''
        photo = ''
        price = ''
        is_ref = True
        is_coupon = True



class AddingCoupon:
    text = ''
    proc = ''
    count = ''
    date = ''


class AddingLinkCoupon:
    user_activates = ""
    text = ''
    type = ''
    value = ""
    count = ''
    date = ''


class Banned_user(DeclarativeBase):
    __tablename__ = "banned_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)


class ServiceObject(DeclarativeBase):
    __tablename__ = "service"

    codename = Column(String)
    text = Column(String)
    link = Column(String)
    id = Column(Integer, primary_key=True)


class Purchase(DeclarativeBase):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    item_id = Column(String)
    price = Column(REAL)
    datetime = Column(DateTime)


class Mass_Message(DeclarativeBase):
    __tablename__ = "mass_message"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    message_id = Column(String)


class SpecialCourse(DeclarativeBase):
    __tablename__ = "special_course"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    photo = Column(String)


class SpecialItem(DeclarativeBase):
    __tablename__ = "special_items"

    id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default=False)
    photo = Column(String, default=None)
    price = Column(Integer, default=0)
    chat_id = Column(String)
    is_ref = Column(Boolean, default=True)
    is_coupon = Column(Boolean, default=True)


class Wallet(DeclarativeBase):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    number = Column(String)
    p2p_key = Column(String)
    api_key = Column(String)
    isgood = Column(Boolean, default=True)


class Item(DeclarativeBase):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    precategory = Column(String)
    category = Column(String, nullable=False)
    subcategory = Column(String,  nullable=False)
    subject = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default=False)
    photo = Column(String, default=None)
    price = Column(Integer, default=0)
    chat_id = Column(String, default=0)
    is_ref = Column(Boolean, default=True)
    is_coupon = Column(Boolean, default=True)


class User(DeclarativeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, default=None)
    user_id = Column(BigInteger,  nullable=False)
    purchases_num = Column(Integer, default=0)
    balance = Column(REAL, default=0)
    referal = Column(String, default=None)
    level = Column(String, default="Без скидок")
    discount = Column(String, default=1)
    coupon_name = Column(String)
    ref_procent = Column(REAL, default=0.2)


class Payment(DeclarativeBase):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger,  nullable=False)
    bill_id = Column(String, default="0")
    sum = Column(Integer, default=0)
    status = Column(String, nullable=False, default="UNPAID")
    datetime = Column(DateTime, nullable=False)
    wallet = Column(String)


class Category(DeclarativeBase):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    precategory = Column(Integer)
    name = Column(String)
    photo = Column(String)


class Subject(DeclarativeBase):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    photo = Column(String)

class Subcategory(DeclarativeBase):
    __tablename__ = "subcategory"

    id = Column(Integer, primary_key=True)
    precategory = Column(Integer)
    category = Column(ForeignKey('category.id'))
    name = Column(String)
    photo = Column(String)


class ItemsNameId(DeclarativeBase):
    __tablename__ = "items_name_id"

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String)


class FreeCourse(DeclarativeBase):
    __tablename__ = "free_course"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)


class Coupon(DeclarativeBase):
    __tablename__ = "coupon"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    proc = Column(Integer)
    count = Column(String)
    date = Column(DateTime)


class Linked_Coupon(DeclarativeBase):
    __tablename__ = "link_coupon"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    count = Column(String)
    date = Column(DateTime)
    func = Column(String)
    used_users = Column(postgresql.ARRAY(String))
    user_activates = Column(Integer, default=1)


if __name__ == "__main__":
    item = AddingSpecialItem()
    print(isinstance(item, AddingSpecialItem))