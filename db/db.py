# для настройки баз данных 
import secrets
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, desc, and_, or_, not_
from datetime import datetime
  
# для определения таблицы и модели 
from sqlalchemy.ext.declarative import declarative_base  
  
# для создания отношений между таблицами
from sqlalchemy.orm import relationship  
from sqlalchemy.orm import sessionmaker
  
# для настроек
from sqlalchemy import create_engine 
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from db.objects import *
  
# создание экземпляра declarative_base
Base = declarative_base() 
  
# здесь добавим классы 
  
# Подключение к серверу PostgreSQL на localhost с помощью psycopg2 DBAPI 
# Устанавливаем соединение с postgres
class Database:
    DATABASE_URI = 'postgresql://postgres:11111111@localhost:5432/SlivyKursov'
    engine = create_engine(DATABASE_URI)
    meta = MetaData(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    Base.metadata.create_all(engine)
    # def __init__(self, user="postgres", password="11111111"):
    #     # self.connection = psycopg2.connect(user=user, password=password)
    #     # self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #     # self.cursor = self.connection.cursor()
    #     # return self.cursor, self.connection
    #     DATABASE_URI = 'postgres+psycopg2://postgres:11111111@localhost:5432/Accounts'
    #     engine = create_engine(DATABASE_URI)
    #     Base.metadata.create_all(engine)
    #     Session = sessionmaker(bind=engine)
    #     s = Session()

    def init(self):
        DATABASE_URI = 'postgresql://postgres:11111111@localhost:5432/SlivyKursov'
        self.engine = create_engine(DATABASE_URI)
        self.meta = MetaData(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.s = self.Session()
        Base.self.metadata.create_all(self.engine)
        
    
    def user_exists(self, user_id):
        user = self.s.query(User).filter_by(user_id=user_id).all()
        return user

    def add_user(self, username, user_id, referal=None, ref_procent=0.1):
        user = User(
            username = username,
            user_id = user_id,
            referal = referal,
            ref_procent = ref_procent
            )

        self.s.add(user)
        self.s.commit()

    def get_user_pur_bal(self, user_id):
        user = self.s.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.purchases_num, round(user.balance, 2)
        else:
            return 0, 0

    def get_user(self, user_id):
        user = self.s.query(User).filter(User.user_id == user_id).first()

        return user


    def del_payment(self, bill_id):
            i = self.s.query(Payment).filter(Payment.bill_id == bill_id).one()
            self.s.delete(i)
            self.s.commit()

    def get_last_payment_id(self):
        paymnt = self.s.query(Payment).order_by(desc(Payment.id)).first()
        
        if not paymnt:
            return -1
        return paymnt.id

    def get_special_items(self, cat_id):
        items = self.s.query(SpecialItem).filter(SpecialItem.category_name == str(cat_id)).all()

        return items

    def add_payment(self, user_id, bill_id, message_money, datetime):
        paymnt = Payment(user_id=user_id, bill_id=bill_id, datetime=datetime, sum=message_money)

        self.s.add(paymnt)
        self.s.commit()

    def get_payment(self, bill_id):
        paymnt = self.s.query(Payment).filter(Payment.bill_id == bill_id).first()

        return paymnt

    def get_purchase(self, purchase_id):
        purchase = self.s.query(Purchase).filter(Purchase.id == purchase_id).first()

        return purchase

    def get_user_balance(self, user_id):
        user = self.s.query(User).filter(User.user_id == user_id).first()

        return user.balance

    def set_payment_status(self, bill_id, status):
        paymnt = self.s.query(Payment).filter(Payment.bill_id == bill_id).first()
        paymnt.status = status

    def set_money(self, user_id, money):
        user = self.s.query(User).filter(User.user_id == user_id).first()
        user.balance = round(money, 2)
        self.s.commit()

    def get_all_items(self):
        items = self.s.query(Item).all()

        return items

    def get_user_purchases(self, user_id):
        purchases = self.s.query(Purchase).filter(Purchase.user_id == user_id).all()

        return purchases

    def get_user_payments(self, user_id):
        payments = self.s.query(Payment).filter(Payment.user_id == user_id).all()

        return payments

    def get_categories(self, precategory):
        categories = self.s.query(Category).filter(Category.precategory == precategory).all()

        return categories

    
    def get_subcategories(self, precategory, category):
        subcategories = self.s.query(Subcategory).all()

        return subcategories

    def get_category(self, category_id):
        category = self.s.query(Category).filter(Category.id == int(category_id)).first()

        return category

    def add_subcategory(self, category, name):
        subcategory = Subcategory(
            category=category, name=name
        )

        self.s.add(subcategory)
        self.s.commit()

    def get_subcategory(self, subcategory_id):
        subcategory = self.s.query(Subcategory).filter(Subcategory.id == int(subcategory_id)).first()

        return subcategory

    def get_item(self, item_id):
        if int(item_id) <= 0:
            item  = self.s.query(SpecialItem).filter(SpecialItem.id == (-int(item_id))).first()
        else:
            item  = self.s.query(Item).filter(Item.id == int(item_id)).first()

        return item

    def add_purchase(self, user_id, item_id, price, date, coupon=None):
        purchase = Purchase(
            user_id = user_id,
            item_id = item_id,
            price = price,
            datetime = date
        )

        self.s.add(purchase)
        self.s.commit()

        return purchase

    def get_users(self):
        users = self.s.query(User).all()

        return users

    def get_mass_messages(self):
        messages = self.s.query(Mass_Message).all()

        return messages

    def get_purchases(self):
        purchases = self.s.query(Purchase).all()

        return purchases

    def get_payments(self):
        payments = self.s.query(Payment).all()

        return payments

    def set_purchase(self, user_id):
        user = self.s.query(User).filter(User.user_id == user_id).first()
        user.purchases_num = user.purchases_num + 1

        self.s.commit()

    def set_level(self, user_id, discount_level):
        user = self.s.query(User).filter(User.user_id == user_id).first()
        user.level = discount_level

    def get_referrals(self, user_id):
        referals = [f"{i.username}" for i in self.s.query(User).filter(User.referal == user_id).all()]

        return referals

    def get_referrals_user_id(self, user_id):
        referals = [f"{i.user_id}" for i in self.s.query(User).filter(User.referal == user_id).all()]

        return referals

    def check_coupon(self, coupon):
        coupon = self.s.query(Coupon).filter(Coupon.name == coupon).all()

        if coupon:
            self.s.delete(coupon)
            return True
        return False

    def get_price_purchases(self, user_id):
        purchases = [i.price for i in self.s.query(Purchase).filter(Purchase.user_id == user_id)]

        return purchases

    def get_payment_from_id(self, bill_id):
        paymnt = self.s.query(Payment).filter(Payment.id == bill_id).first()

        return paymnt

    def get_users_username(self):
        users = [i.username for i in self.s.query(User).all()]

        return users

    def get_service_object(self, codename):
        ServObj = self.s.query(ServiceObject).filter(ServiceObject.codename == codename).first()

        return ServObj

    def get_banned_users(self):
        users = [i.user_id for i in self.s.query(Banned_user).all()]

        return users

    def get_user_from_username(self, username):
        user = self.s.query(User).filter(User.username == username).first()

        return user

    def add_blacklist(self, user_id):
        banned = Banned_user(user_id=user_id)

        self.s.add(banned)
        self.s.commit()

    def del_blacklist(self, user_id):
        banned = self.s.query(Banned_user).filter(Banned_user.user_id == user_id).first()

        self.s.delete(banned)
        self.s.commit()

    def get_link_coupon(self, coupon_text):
        coupon = self.s.query(Linked_Coupon).filter(Linked_Coupon.text == coupon_text).first()

        return coupon

    def get_coupon(self, coupon_text):
        if "-" in coupon_text:
            coupon = self.s.query(Linked_Coupon).filter(Linked_Coupon.text == coupon_text[1:]).first()
        else:
            coupon = self.s.query(Coupon).filter(Coupon.text == coupon_text).first()

        return coupon

    def get_coupons(self):
        coupons = self.s.query(Coupon).all()

        return coupons


    def get_items(self, precategory, category, subcategory, subject):
        items = self.s.query(Item).filter(Item.category == str(category), Item.subcategory == str(subcategory), Item.precategory == str(precategory), Item.subject == str(subject)).all()

        return items

    def get_special_courses(self):
        courses = self.s.query(SpecialCourse).all()

        return courses

    def get_special_course(self, id):
        courses = self.s.query(SpecialCourse).filter(SpecialCourse.id == id).first()

        return courses

    def get_special_items(self, cat_id):
        items = self.s.query(SpecialItem).filter(SpecialItem.category_name == str(cat_id)).all()

        return items


    def get_special_items_id(self, id):
        items = self.s.query(SpecialItem).filter(SpecialItem.id == id).all()

        return items

    def get_link_coupons(self):
        coupons = self.s.query(Linked_Coupon).all()

        return coupons

    def get_wallets(self):
        wallets = self.s.query(Wallet).all()

        return wallets

    
    def get_wallet(self, num):
        wallet = self.s.query(Wallet).filter(Wallet.number == num).first()

        return wallet

    
    def get_good_wallets(self):
        wallet = self.s.query(Wallet).filter(Wallet.isgood == True).all()

        return wallet
        

    def get_hex(self):
        while True:
            text = secrets.token_hex(nbytes=16)
            items = self.s.query(Linked_Coupon).filter(Linked_Coupon.text == text).all()

            if not items:
                return text
            else:
                continue


if __name__ == "__main__":
    data = Database()
    data.get_items(category=1, subcategory=1)


    
    
        



    
  