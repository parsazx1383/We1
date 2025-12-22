#==================== Import ======================#
from colorama import Fore
from pyrogram import Client, filters, idle, errors
from pyrogram.types import *
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import subprocess
import html
import zipfile
import pymysql
import shutil
import signal
import json
import re
import os
import time
#==================== Config =====================#
Admin = 8324661572 # Admin ID
Token = "8190810664:AAH6HIqmLr-_ReF2SWc4Zds8YfUWveFm-n4" # Bot Token
API_ID = 32723346 # API ID
API_HASH = "00b5473e6d13906442e223145510676e" # API HASH
DBName = "SELFSAZ" # Database Name
api_channel = "SHAH_SELF"  # یا از تنظیمات بخوانید
DBUser = "SELFSAZ" # Database User
DBPass = "Zxcvbnm1111" # Database Password
HelperDBName = "HELPER" # Helper Database Name
HelperDBUser = "HELPER" # Helper Database User
HelperDBPass = "Zxcvbnm1111" # Helper Database Password
CardNumber = "6037701213986919" # Card Number
CardName = "امیرعلی میرزایی" # Card Name
#==================== Create =====================#
if not os.path.isdir("sessions"):
    os.mkdir("sessions")
if not os.path.isdir("selfs"):
    os.mkdir("selfs")
if not os.path.isdir("cards"):
    os.mkdir("cards")
#===================== App =======================#
app = Client("Bot", api_id=API_ID, api_hash=API_HASH, bot_token=Token)

scheduler = AsyncIOScheduler()
scheduler.start()

temp_Client = {}
lock = asyncio.Lock()

#==================== Database Functions =====================#
def get_data(query):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchone()
        return result

def get_datas(query):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchall()
        return result

def update_data(query):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        connect.commit()

def helper_getdata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        result = db.fetchone()
        return result

def helper_updata(query):
    with pymysql.connect(host="localhost", database=HelperDBName, user=HelperDBUser, password=HelperDBPass) as connect:
        db = connect.cursor()
        db.execute(query)
        connect.commit()

def add_card(user_id, card_number, bank_name=None):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        if bank_name:
            db.execute(f"INSERT INTO cards(user_id, card_number, bank_name, verified) VALUES({user_id}, '{card_number}', '{bank_name}', 'pending')")
        else:
            db.execute(f"INSERT INTO cards(user_id, card_number, verified) VALUES({user_id}, '{card_number}', 'pending')")
        connect.commit()

def get_user_cards(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM cards WHERE user_id = '{user_id}' AND verified = 'verified' ORDER BY id DESC")
        result = db.fetchall()
        return result

def get_user_all_cards(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM cards WHERE user_id = '{user_id}' ORDER BY id DESC")
        result = db.fetchall()
        return result

def get_pending_cards():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute("SELECT * FROM cards WHERE verified = 'pending'")
        result = db.fetchall()
        return result

def update_card_status(card_id, status, bank_name=None):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        if bank_name:
            db.execute(f"UPDATE cards SET verified = '{status}', bank_name = '{bank_name}' WHERE id = '{card_id}'")
        else:
            db.execute(f"UPDATE cards SET verified = '{status}' WHERE id = '{card_id}'")
        connect.commit()

def delete_card(card_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"DELETE FROM cards WHERE id = '{card_id}'")
        connect.commit()

def get_card_by_number(user_id, card_number):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM cards WHERE user_id = '{user_id}' AND card_number = '{card_number}' LIMIT 1")
        result = db.fetchone()
        return result

def get_card_by_id(card_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM cards WHERE id = '{card_id}' LIMIT 1")
        result = db.fetchone()
        return result

def generate_random_code(length=16):
    import random
    import string
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_code(days):
    code = generate_random_code()
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"INSERT INTO codes(code, days) VALUES('{code}', '{days}')")
        connect.commit()
    return code

def get_code_by_value(code_value):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM codes WHERE code = '{code_value}' AND is_active = TRUE LIMIT 1")
        result = db.fetchone()
        return result

def use_code(code_value, user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"UPDATE codes SET used_by = '{user_id}', used_at = NOW(), is_active = FALSE WHERE code = '{code_value}'")
        connect.commit()

def get_active_codes():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute("SELECT * FROM codes WHERE is_active = TRUE ORDER BY created_at DESC")
        result = db.fetchall()
        return result

def get_all_codes():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute("SELECT * FROM codes ORDER BY created_at DESC")
        result = db.fetchall()
        return result

def delete_code(code_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"DELETE FROM codes WHERE id = '{code_id}'")
        connect.commit()

def cleanup_inactive_codes():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute("DELETE FROM codes WHERE is_active = FALSE")
        connect.commit()

def get_channels_by_type(channel_type=None):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        if channel_type:
            db.execute(f"SELECT * FROM channels WHERE channel_type = '{channel_type}' AND is_active = TRUE ORDER BY priority ASC")
        else:
            db.execute("SELECT * FROM channels WHERE is_active = TRUE ORDER BY channel_type, priority ASC")
        result = db.fetchall()
        return result

def get_channel(channel_type):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM channels WHERE channel_type = '{channel_type}' AND is_active = TRUE ORDER BY priority ASC LIMIT 1")
        result = db.fetchone()
        return result

def add_channel(channel_id, channel_type="extra", priority=None):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        if priority is None:
            db.execute(f"SELECT MAX(priority) as max_priority FROM channels WHERE channel_type = '{channel_type}'")
            result = db.fetchone()
            priority = (result[0] or 0) + 1
        
        db.execute(f"INSERT INTO channels(channel_id, channel_type, priority, is_active) VALUES('{channel_id}', '{channel_type}', {priority}, TRUE)")
        connect.commit()
        return True

def update_channel(channel_type, new_channel_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"UPDATE channels SET channel_id = '{new_channel_id}' WHERE channel_type = '{channel_type}' AND is_active = TRUE ORDER BY priority ASC LIMIT 1")
        connect.commit()
        return True

def delete_channel(channel_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"DELETE FROM channels WHERE channel_id = '{channel_id}'")
        connect.commit()
        return True

def get_all_channels():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute("SELECT * FROM channels ORDER BY channel_type, priority ASC")
        result = db.fetchall()
        return result

def deactivate_channel(channel_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"UPDATE channels SET is_active = FALSE WHERE channel_id = '{channel_id}'")
        connect.commit()
        return True

def activate_channel(channel_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"UPDATE channels SET is_active = TRUE WHERE channel_id = '{channel_id}'")
        connect.commit()
        return True

#==================== Admin Management Functions =====================#
def add_admin_role(user_id, role_type="sales"):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"INSERT INTO admin_roles(user_id, role_type) VALUES({user_id}, '{role_type}') ON DUPLICATE KEY UPDATE role_type = '{role_type}'")
        connect.commit()

def remove_admin_role(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"DELETE FROM admin_roles WHERE user_id = '{user_id}'")
        db.execute(f"DELETE FROM admin_permissions WHERE user_id = '{user_id}'")
        connect.commit()

def get_admin_role(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM admin_roles WHERE user_id = '{user_id}' LIMIT 1")
        result = db.fetchone()
        return result

def set_admin_permissions(user_id, can_sell=False, can_manage=False, can_transactions=False, can_support=False):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"""
            INSERT INTO admin_permissions(user_id, can_sell, can_manage, can_transactions, can_support) 
            VALUES({user_id}, {can_sell}, {can_manage}, {can_transactions}, {can_support})
            ON DUPLICATE KEY UPDATE 
            can_sell = {can_sell},
            can_manage = {can_manage},
            can_transactions = {can_transactions},
            can_support = {can_support}
        """)
        connect.commit()

def get_admin_permissions(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM admin_permissions WHERE user_id = '{user_id}' LIMIT 1")
        result = db.fetchone()
        return result

def get_sales_admin_balance(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM sales_admin_balance WHERE user_id = '{user_id}' LIMIT 1")
        result = db.fetchone()
        if not result:
            db.execute(f"INSERT INTO sales_admin_balance(user_id, balance) VALUES({user_id}, 0)")
            connect.commit()
            return {"user_id": user_id, "balance": 0}
        return result

def update_sales_admin_balance(user_id, amount):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"INSERT INTO sales_admin_balance(user_id, balance) VALUES({user_id}, {amount}) ON DUPLICATE KEY UPDATE balance = balance + {amount}")
        connect.commit()

def get_sales_admin_prices(user_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM sales_admin_prices WHERE user_id = '{user_id}' LIMIT 1")
        result = db.fetchone()
        if not result:
            # استفاده از قیمت‌های پیش‌فرض
            prices = get_prices()
            db.execute(f"""
                INSERT INTO sales_admin_prices(user_id, price_1month, price_2month, price_3month, price_4month, price_5month, price_6month) 
                VALUES({user_id}, {prices['1month']}, {prices['2month']}, {prices['3month']}, {prices['4month']}, {prices['5month']}, {prices['6month']})
            """)
            connect.commit()
            return {
                "user_id": user_id,
                "price_1month": int(prices['1month']),
                "price_2month": int(prices['2month']),
                "price_3month": int(prices['3month']),
                "price_4month": int(prices['4month']),
                "price_5month": int(prices['5month']),
                "price_6month": int(prices['6month'])
            }
        return result

def update_sales_admin_prices(user_id, prices_dict):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"""
            INSERT INTO sales_admin_prices(user_id, price_1month, price_2month, price_3month, price_4month, price_5month, price_6month) 
            VALUES({user_id}, {prices_dict['1month']}, {prices_dict['2month']}, {prices_dict['3month']}, {prices_dict['4month']}, {prices_dict['5month']}, {prices_dict['6month']})
            ON DUPLICATE KEY UPDATE 
            price_1month = {prices_dict['1month']},
            price_2month = {prices_dict['2month']},
            price_3month = {prices_dict['3month']},
            price_4month = {prices_dict['4month']},
            price_5month = {prices_dict['5month']},
            price_6month = {prices_dict['6month']}
        """)
        connect.commit()

def add_admin_customer(admin_id, customer_id, days_purchased=0, amount=0):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"""
            INSERT INTO admin_customers(admin_id, customer_id, total_days, total_purchased) 
            VALUES({admin_id}, {customer_id}, {days_purchased}, {amount})
            ON DUPLICATE KEY UPDATE 
            total_days = total_days + {days_purchased},
            total_purchased = total_purchased + {amount},
            status = 'active'
        """)
        connect.commit()

def remove_admin_customer(admin_id, customer_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass) as connect:
        db = connect.cursor()
        db.execute(f"UPDATE admin_customers SET status = 'removed' WHERE admin_id = {admin_id} AND customer_id = {customer_id}")
        connect.commit()

def get_admin_customers(admin_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM admin_customers WHERE admin_id = {admin_id} AND status = 'active'")
        result = db.fetchall()
        return result

def check_customer_assigned(customer_id):
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute(f"SELECT * FROM admin_customers WHERE customer_id = {customer_id} AND status = 'active' LIMIT 1")
        result = db.fetchone()
        return result

def is_sales_admin(user_id):
    role = get_admin_role(user_id)
    if role and role['role_type'] == 'sales':
        permissions = get_admin_permissions(user_id)
        if permissions and permissions['can_sell']:
            return True
    return False

def has_admin_permission(user_id, permission_type):
    permissions = get_admin_permissions(user_id)
    if not permissions:
        return False
    
    if permission_type == 'sell':
        return permissions['can_sell']
    elif permission_type == 'manage':
        return permissions['can_manage']
    elif permission_type == 'transactions':
        return permissions['can_transactions']
    elif permission_type == 'support':
        return permissions['can_support']
    return False

def get_all_admins():
    with pymysql.connect(host="localhost", database=DBName, user=DBUser, password=DBPass, cursorclass=pymysql.cursors.DictCursor) as connect:
        db = connect.cursor()
        db.execute("""
            SELECT ar.*, ap.*, u.phone 
            FROM admin_roles ar 
            LEFT JOIN admin_permissions ap ON ar.user_id = ap.user_id 
            LEFT JOIN user u ON ar.user_id = u.id 
            ORDER BY ar.created_at DESC
        """)
        result = db.fetchall()
        return result

def add_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is None:
        helper_updata(f"INSERT INTO adminlist(id) VALUES({user_id})")

def delete_admin(user_id):
    if helper_getdata(f"SELECT * FROM adminlist WHERE id = '{user_id}' LIMIT 1") is not None:
        helper_updata(f"DELETE FROM adminlist WHERE id = '{user_id}' LIMIT 1")

#==================== Database Initialization =====================#

update_data("""
CREATE TABLE IF NOT EXISTS bot(
status varchar(10) DEFAULT 'ON'
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS user(
id bigint PRIMARY KEY,
step varchar(150) DEFAULT 'none',
phone varchar(150) DEFAULT NULL,
api_id varchar(50) DEFAULT NULL,
api_hash varchar(100) DEFAULT NULL,
expir bigint DEFAULT '0',
account varchar(50) DEFAULT 'unverified',
self varchar(50) DEFAULT 'inactive',
pid bigint DEFAULT NULL,
last_language_change bigint DEFAULT NULL
) default charset=utf8mb4;
""")

# در بخش Database Initialization بعد از جداول موجود اضافه کنید:
update_data("""
CREATE TABLE IF NOT EXISTS admin_roles(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    role_type VARCHAR(50) NOT NULL DEFAULT 'sales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS admin_permissions(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    can_sell BOOLEAN DEFAULT FALSE,
    can_manage BOOLEAN DEFAULT FALSE,
    can_transactions BOOLEAN DEFAULT FALSE,
    can_support BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS sales_admin_balance(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    balance BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS sales_admin_prices(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    price_1month BIGINT DEFAULT 75000,
    price_2month BIGINT DEFAULT 150000,
    price_3month BIGINT DEFAULT 220000,
    price_4month BIGINT DEFAULT 275000,
    price_5month BIGINT DEFAULT 340000,
    price_6month BIGINT DEFAULT 390000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS admin_customers(
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    total_purchased BIGINT DEFAULT 0,
    total_days INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS channels(
id INT AUTO_INCREMENT PRIMARY KEY,
channel_id VARCHAR(100) NOT NULL,
channel_type VARCHAR(20) NOT NULL DEFAULT 'main',
priority INT DEFAULT 1,
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS codes(
id INT AUTO_INCREMENT PRIMARY KEY,
code VARCHAR(20) UNIQUE NOT NULL,
days INT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
used_by BIGINT DEFAULT NULL,
used_at TIMESTAMP NULL,
is_active BOOLEAN DEFAULT TRUE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS cards(
id INT AUTO_INCREMENT PRIMARY KEY,
user_id bigint NOT NULL,
card_number varchar(20) NOT NULL,
bank_name varchar(50) DEFAULT NULL,
verified varchar(10) DEFAULT 'pending',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS settings(
id INT AUTO_INCREMENT PRIMARY KEY,
setting_key VARCHAR(100) NOT NULL UNIQUE,
setting_value TEXT NOT NULL,
description VARCHAR(255) DEFAULT NULL,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) default charset=utf8mb4;
""")

update_data("""
CREATE TABLE IF NOT EXISTS block(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

helper_updata("""
CREATE TABLE IF NOT EXISTS ownerlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

helper_updata("""
CREATE TABLE IF NOT EXISTS adminlist(
id bigint PRIMARY KEY
) default charset=utf8mb4;
""")

bot = get_data("SELECT * FROM bot")
if bot is None:
    update_data("INSERT INTO bot() VALUES()")

OwnerUser = helper_getdata(f"SELECT * FROM ownerlist WHERE id = '{Admin}' LIMIT 1")
if OwnerUser is None:
    helper_updata(f"INSERT INTO ownerlist(id) VALUES({Admin})")

AdminUser = helper_getdata(f"SELECT * FROM adminlist WHERE id = '{Admin}' LIMIT 1")
if AdminUser is None:
    helper_updata(f"INSERT INTO adminlist(id) VALUES({Admin})")


default_settings = [
    ("start_message", "**\nسلام [ {user_link} ],  به ربات خرید دستیار تلگرام خوش آمدید.\n\nتوی این ربات میتونید از خرید، نصب دستیار بهره ببرید.\n\nلطفا اگر سوالی دارید از بخش پشتیبانی ، با پشتیبان ها در ارتباط باشید یا در گروه پشتیبانی ما عضو شوید.\n\n\n **", "پیام استارت ربات"),
    ("price_message", "**\nنرخ ربات دستیار عبارت است از :\n\n» 1 ماهه : ( `{price_1month}` تومان )\n\n» 2 ماهه : ( `{price_2month}` تومان )\n\n» 3 ماهه : ( `{price_3month}` تومان )\n\n» 4 ماهه : ( `{price_4month}` تومان )\n\n» 5 ماهه : ( `{price_5month}` تومان )\n\n» 6 ماهه : ( `{price_6month}` تومان )\n\n\n(⚠️) توجه داشته باشید که ربات دستیار روی شماره های ایران توصیه میشود و در صورت نصب روی شماره های خارج از کشور، ما مسئولیتی در مورد مسدود شدن اکانت نداریم.\n\n\nدر صورتی که میخواهید به صورت ارزی پرداخت کنید از پشتیبانی درخواست ولت کنید.\n‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌\n‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌‌\n**", "پیام نرخ‌ها"),
    ("whatself_message", "**\nسلف به رباتی گفته میشه که روی اکانت شما نصب میشه و امکانات خاصی رو در اختیارتون میزاره ، لازم به ذکر هست که نصب شدن بر روی اکانت شما به معنی وارد شدن ربات به اکانت شما هست ( به دلیل دستور گرفتن و انجام فعالیت ها )\nاز جمله امکاناتی که در اختیار شما قرار میدهد شامل موارد زیر است:\n\n❈ گذاشتن ساعت با فونت های مختلف بر روی بیو ، اسم\n❈ قابلیت تنظیم حالت خوانده شدن خودکار پیام ها\n❈ تنظیم حالت پاسخ خودکار\n❈ پیام انیمیشنی\n❈ منشی هوشمند\n❈ دریافت پنل و تنظیمات اکانت هوشمند\n❈ دو زبانه بودن دستورات و جواب ها\n❈ تغییر نام و کاور فایل ها\n❈ اعلان پیام ادیت و حذف شده در پیوی\n❈ ذخیره پروفایل های جدید و اعلان حذف پروفایل مخاطبین\n\nو امکاناتی دیگر که میتوانید با مراجعه به بخش راهنما آن ها را ببینید و مطالعه کنید!\n\n❈ لازم به ذکر است که امکاناتی که در بالا گفته شده تنها ذره ای از امکانات سلف میباشد .\n**", "پیام توضیح سلف"),
    ("price_1month", "75000", "قیمت 1 ماهه"),
    ("price_2month", "150000", "قیمت 2 ماهه"),
    ("price_3month", "220000", "قیمت 3 ماهه"),
    ("price_4month", "275000", "قیمت 4 ماهه"),
    ("price_5month", "340000", "قیمت 5 ماهه"),
    ("price_6month", "390000", "قیمت 6 ماهه"),
    ("card_number", CardNumber, "شماره کارت"),
    ("card_name", CardName, "نام صاحب کارت"),
    ("phone_restriction", "enabled", "محدودیت شماره (فقط ایران)"),
]

for key, value, description in default_settings:
    if get_data(f"SELECT * FROM settings WHERE setting_key = '{key}'") is None:
        update_data(f"INSERT INTO settings(setting_key, setting_value, description) VALUES('{key}', '{value}', '{description}')")


channels_data = [
    ("SHAH_SELF", "main", 1, True),
    ("SHAH_SELF", "help", 2, True),
    ("SHAH_SELF", "api", 3, True)
]

for channel_id, channel_type, priority, is_active in channels_data:
    existing = get_data(f"SELECT * FROM channels WHERE channel_type = '{channel_type}' LIMIT 1")
    if existing is None:
        update_data(f"INSERT INTO channels(channel_id, channel_type, priority, is_active) VALUES('{channel_id}', '{channel_type}', {priority}, {is_active})")




def checker(func):
    @wraps(func)
    async def wrapper(c, m, *args, **kwargs):
        chat_id = m.chat.id if hasattr(m, "chat") else m.from_user.id
        bot = get_data("SELECT * FROM bot")
        block = get_data(f"SELECT * FROM block WHERE id = '{chat_id}' LIMIT 1")

        if block is not None and chat_id != Admin:
            return
        
        not_joined_channels = await check_all_channels_membership(chat_id)
        
        if not_joined_channels:
            buttons = []
            for channel in not_joined_channels:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"( {channel['title'][:20]} )",
                        url=f"https://t.me/{channel['username']}"
                    )
                ])
            
            buttons.append([
                InlineKeyboardButton(text="عضو شدم (✔️)", callback_data="check_membership")
            ])
            
            channels_text = "، ".join([f"@{channel['username']}" for channel in not_joined_channels])
            await app.send_message(
                chat_id,
                f"**• برای استفاده از خدمات ما ابتدا باید در کانال زیر عضو باشید، پس از این که عضو شدید روی دکمه عضو شدم کلیک کنید.**",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

        if bot["status"] == "OFF" and chat_id != Admin:
            await app.send_message(chat_id, "**درحال حاظر ربات خاموش میباشد، بعدا مجدد اقدام نمایید.**")
            return
        
        return await func(c, m, *args, **kwargs)
    return wrapper


def get_main_channels():
    return get_channels_by_type('main')

def get_channel_username(channel_id):
    if channel_id.startswith('@'):
        return channel_id[1:]
    elif channel_id.startswith('https://t.me/'):
        return channel_id[13:]
    else:
        return channel_id

def get_channel_username_by_type(channel_type):
    channel = get_channel(channel_type)
    if channel:
        return get_channel_username(channel['channel_id'])
    return "SHAH_SELF"

async def check_all_channels_membership(user_id):
    channels = get_main_channels()
    not_joined_channels = []
    
    for channel in channels:
        try:
            try:
                chat = await app.get_chat(channel['channel_id'])
            except Exception as e:
                continue
            
            try:
                member = await app.get_chat_member(channel['channel_id'], user_id)
                if member.status in ["left", "kicked", "banned"]:
                    raise errors.UserNotParticipant
            except errors.UserNotParticipant:
                not_joined_channels.append({
                    'id': channel['channel_id'],
                    'username': get_channel_username(channel['channel_id']),
                    'title': chat.title if hasattr(chat, 'title') else channel['channel_id']
                })
            except Exception as e:
                not_joined_channels.append({
                    'id': channel['channel_id'],
                    'username': get_channel_username(channel['channel_id']),
                    'title': "کانال"
                })
                
        except Exception as e:
            not_joined_channels.append({
                'id': channel['channel_id'],
                'username': get_channel_username(channel['channel_id']),
                'title': "کانال"
            })
    
    return not_joined_channels

async def expirdec(user_id):
    user = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
    user_expir = user["expir"]
    if user_expir > 0:
        user_upexpir = user_expir - 1
        update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
    else:
        job = scheduler.get_job(str(user_id))
        if job:
            scheduler.remove_job(str(user_id))
        if user_id != Admin:
            delete_admin(user_id)
        if os.path.isdir(f"selfs/self-{user_id}"):
            pid = user["pid"]
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                pass
            await asyncio.sleep(1)
            try:
                shutil.rmtree(f"selfs/self-{user_id}")
            except:
                pass
        if os.path.isfile(f"sessions/{user_id}.session"):
            try:
                async with Client(f"sessions/{user_id}") as user_client:
                    await user_client.log_out()
            except:
                pass
            if os.path.isfile(f"sessions/{user_id}.session"):
                os.remove(f"sessions/{user_id}.session")
        if os.path.isfile(f"sessions/{user_id}.session-journal"):
            os.remove(f"sessions/{user_id}.session-journal")
        await app.send_message(user_id, "**انقضای سلف شما** به پایان رسید، شما میتوانید از بخش **خرید اشتراک**، **سلف خود را تمدید کنید.**")
        update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
        update_data(f"UPDATE user SET pid = NULL WHERE id = '{user_id}' LIMIT 1")

async def setscheduler(user_id):
    job = scheduler.get_job(str(user_id))
    if not job:
        scheduler.add_job(expirdec, "interval", hours=24, args=[user_id], id=str(user_id))


async def check_self_status(user_id):
    try:
        user_folder = f"selfs/self-{user_id}"
        if not os.path.isdir(user_folder):
            return {
                "status": "not_installed",
                "message": "سلف شما نصب نشده است.",
                "language": None
            }
        
        data_file = os.path.join(user_folder, "data.json")
        if not os.path.isfile(data_file):
            return {
                "status": "error",
                "message": "تنطیمات سلف نصب نشده است.",
                "language": None
            }
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        language = data.get("language", "fa")
        language_text = "فارسی" if language == "fa" else "انگلیسی"
        
        user_data = get_data(f"SELECT pid, self FROM user WHERE id = '{user_id}' LIMIT 1")
        if not user_data:
            return {
                "status": "error",
                "message": "اطلاعات ربات پیدا نشد.",
                "language": language_text
            }
        
        pid = user_data.get("pid")
        self_status = user_data.get("self", "inactive")
        
        if pid:
            try:
                os.kill(pid, 0)
                process_status = "running"
            except OSError:
                process_status = "stopped"
        else:
            process_status = "no_pid"
        
        if self_status == "active" and process_status == "running":
            return {
                "status": "healthy",
                "message": "`دستیار شما موردی نداره و روشن هست.`",
                "language": language_text
            }
        elif self_status == "active" and process_status == "stopped":
            return {
                "status": "problem",
                "message": "`دستیار شما با مشکل مواجه شده و نیاز به ورود مجدد است.`",
                "language": language_text
            }
        elif self_status == "inactive":
            return {
                "status": "inactive",
                "message": "`دستیار شما خاموش است.`",
                "language": language_text
            }
        else:
            return {
                "status": "unknown",
                "message": "`وضعیت دستیار شما نامشخص است`",
                "language": language_text
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"**سلف شما نصب نشده است، ابتدا دستیار خود را نصب کنید.**",
            "language": None
        }

async def change_self_language(user_id, target_language):
    try:
        user_folder = f"selfs/self-{user_id}"
        data_file = os.path.join(user_folder, "data.json")
        
        if not os.path.isfile(data_file):
            return False, "**تنظیمات ربات دستیار نصب نشده است.**"
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        old_language = data.get("language", "fa")
        
        data["language"] = target_language
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        current_time = int(time.time())
        update_data(f"UPDATE user SET last_language_change = '{current_time}' WHERE id = '{user_id}'")
        
        return True, old_language
        
    except Exception as e:
        return False, str(e)

def can_change_language(user_id):
    user_data = get_data(f"SELECT last_language_change FROM user WHERE id = '{user_id}' LIMIT 1")
    
    if not user_data or user_data.get("last_language_change") is None:
        return True, 0
    
    last_change = int(user_data.get("last_language_change", 0))
    current_time = int(time.time())
    time_passed = current_time - last_change
    
    if time_passed >= 1800:
        return True, 0
    
    remaining_seconds = 1800 - time_passed
    remaining_minutes = (remaining_seconds + 59) // 60
    
    return False, remaining_minutes

def get_current_language(user_id):
    try:
        user_folder = f"selfs/self-{user_id}"
        data_file = os.path.join(user_folder, "data.json")
        
        if not os.path.isfile(data_file):
            return "fa"
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("language", "fa")
    except:
        return "fa"


async def extract_self_files(user_id, language="fa"):
    try:
        user_folder = f"selfs/self-{user_id}"
        
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
        
        os.makedirs(user_folder, exist_ok=True)
        
        data_file = os.path.join(user_folder, "data.json")
        default_data = {
            "language": language,
            "user_id": user_id,
            "bot_language": language
        }
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        
        zip_path = "source/Self.zip"
        
        if not os.path.isfile(zip_path):
            await app.send_message(user_id, f"**• فایل Self.zip در مسیر {zip_path} یافت نشد.**")
            return False
        
        file_size = os.path.getsize(zip_path)
        if file_size == 0:
            await app.send_message(user_id, "**• فایل Self.zip خالی یا آسیب دیده است.**")
            return False
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if zip_ref.testzip() is not None:
                    await app.send_message(user_id, "**• فایل Self.zip آسیب دیده است.**")
                    return False
                
                file_list = zip_ref.namelist()
                
                if not file_list:
                    await app.send_message(user_id, "**• فایل Self.zip خالی است.**")
                    return False
                
                zip_ref.extractall(user_folder)
                
                if "self.py" not in file_list:
                    await app.send_message(user_id, f"**• فایل self.py در آرشیو یافت نشد. فایل‌های موجود: {file_list}**")
                    return False
                
                if not os.path.exists(data_file):
                    default_data = {
                        "language": language,
                        "user_id": user_id,
                        "bot_language": language
                    }
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, ensure_ascii=False, indent=2)
                return True
                
        except zipfile.BadZipFile:
            await app.send_message(user_id, "**• فایل Self.zip معتبر نیست.**")
            return False
            
    except PermissionError as e:
        await app.send_message(user_id, "**• خطای دسترسی: امکان نوشتن در پوشه وجود ندارد.**")
        return False
    except Exception as e:
        error_msg = f"**• خطا در استخراج فایل:**\n```\n{str(e)}\n```"
        await app.send_message(user_id, error_msg)
        return False

def validate_phone_number(phone_number):
    restriction = get_setting("phone_restriction", "disabled")
    
    if restriction == "disabled":
        return True, None
    
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"
    
    if phone_number.startswith("+98"):
        return True, None
    else:
        return False, "**تا اطلاع ثانوی، نصب یا خرید ربات سلف روی اکانت مجازی غیرمجاز میباشد.**"

async def safe_edit_message(chat_id, message_id, new_text):
    try:
        try:
            current_msg = await app.get_messages(chat_id, message_id)
            if current_msg.text == new_text:
                return current_msg, False
        except:
            pass
        
        await app.edit_message_text(chat_id, message_id, new_text)
        
        edited_msg = await app.get_messages(chat_id, message_id)
        return edited_msg, True
    except errors.MessageNotModified:
        try:
            current_msg = await app.get_messages(chat_id, message_id)
            return current_msg, False
        except:
            return None, False
    except Exception as e:
        print(f"Error in safe_edit_message: {e}")
        return None, False

async def start_self_installation(user_id, phone, api_id, api_hash, message_id=None, language="fa"):
    try:
        is_valid, error_message = validate_phone_number(phone)
        if not is_valid:
            if message_id:
                await safe_edit_message(user_id, message_id, "**• نصب ربات سلف روی اکانت مجازی غیرمجاز است.**")
            else:
                await app.send_message(user_id, "**• نصب ربات سلف روی اکانت مجازی غیرمجاز است.**")
            return False
        
        if message_id:
            msg, edited = await safe_edit_message(user_id, message_id, "**• درحال ساخت سلف، لطفا صبور باشید.**")
            if not msg:
                msg = await app.get_messages(user_id, message_id)
        else:
            msg = await app.send_message(user_id, "**• درحال ساخت سلف، لطفا صبور باشید.**")
        
        success = await extract_self_files(user_id, language)
        
        if not success:
            await safe_edit_message(user_id, msg.id, "**استخراج فایل ربات با خطا مواجه شد، با پشتیبانی در ارتباط باشید.**")
            return False
        
        client = Client(
            f"sessions/{user_id}",
            api_id=int(api_id),
            api_hash=api_hash
        )
        
        await client.connect()
        
        sent_code = await client.send_code(phone)
        
        temp_Client[user_id] = {
            "client": client,
            "phone_code_hash": sent_code.phone_code_hash,
            "phone": phone,
            "api_id": api_id,
            "api_hash": api_hash,
            "language": language
        }
        
        caption = "**• با توجه به ویدئو، کدی که از سمت تلگرام برای شما ارسال شده را با استفاده از دکمه زیر به اشتراک بگذارید.**"
        await app.send_animation(
            chat_id=user_id,
            animation="training.gif",
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="اشتراک گذاری کد", 
                    switch_inline_query_current_chat=""
                )
            ]
        ]))
        
        update_data(f"UPDATE user SET step = 'install_code-{phone}-{api_id}-{api_hash}-{language}' WHERE id = '{user_id}'")
        
        return True
        
    except errors.PhoneNumberInvalid:
        if message_id:
            await safe_edit_message(user_id, message_id, "**• شماره تلفن نامعتبر است.**")
        return False
    except errors.PhoneNumberBanned:
        if message_id:
            await safe_edit_message(user_id, message_id, "**• شماره تلفن مسدود شده است.**")
        return False
    except errors.PhoneNumberFlood:
        if message_id:
            await safe_edit_message(user_id, message_id, "**• درحالت انتضار هستید، منتظر بمانید.**")
        return False
    except Exception as e:
        error_msg = f"**• خطا در نصب سلف:**\n```\n{str(e)[:200]}\n```"
        if message_id:
            await safe_edit_message(user_id, message_id, error_msg)
        else:
            await app.send_message(user_id, error_msg)
        return False

async def verify_code_and_login(user_id, phone, api_id, api_hash, code, language="fa"):
    try:
        if user_id not in temp_Client:
            await app.send_message(user_id, "**• عملیات منقضی شده، مجدد مراحل نصب را انجام دهید.**")
            return
        
        client_data = temp_Client[user_id]
        client = client_data["client"]
        phone_code_hash = client_data["phone_code_hash"]
        stored_language = client_data.get("language", "fa")
        
        try:
            await client.sign_in(
                phone_number=phone,
                phone_code_hash=phone_code_hash,
                phone_code=code
            )
            
        except errors.SessionPasswordNeeded:
            await app.send_message(user_id,
                "**• لطفا رمز دومرحله ای اکانت را بدون هیچ کلمه یا کاراکتر اضافه ای ارسال کنید :**")
            
            update_data(f"UPDATE user SET step = 'install_2fa-{phone}-{api_id}-{api_hash}-{stored_language}' WHERE id = '{user_id}'")
            return
        
        await app.send_message(user_id, "**• ورود به اکانت با موفقیت انجام شد، درحال نصب نهایی سلف، لطفا صبور باشید.**")
        
        try:
            if client.is_connected:
                await client.disconnect()
        except:
            pass
        
        if user_id in temp_Client:
            del temp_Client[user_id]
        
        await asyncio.sleep(3)
        
        await start_self_bot(user_id, api_id, api_hash, None, stored_language)
        
    except errors.PhoneCodeInvalid:
        await app.send_message(user_id, "**• کد وارد شده نامعتبر است، مجدد کد را وارد کنید.**")
    except errors.PhoneCodeExpired:
        await app.send_message(user_id, "**• کد موردنظر باطل شده بود، مجدد عملیات رو آغاز کنید.**")
    except Exception as e:
        await app.send_message(user_id, f"**• خطا در تایید کد، با پشتیبانی در ارتباط باشید.**")

async def verify_2fa_password(user_id, phone, api_id, api_hash, password, language="fa"):
    try:
        
        client = Client(
            f"sessions/{user_id}",
            api_id=int(api_id),
            api_hash=api_hash
        )
        
        await client.connect()
        
        await client.check_password(password)
        
        await app.edit_message_text(user_id, "**• ورود به اکانت با موفقیت انجام شد، درحال نصب نهایی سلف، لطفا صبور باشید.**")
        
        await start_self_bot(user_id, api_id, api_hash, None, language)
        
        await client.disconnect()
        
    except Exception as e:
        await app.send_message(user_id, "**• خطا در تایید رمز، با پشتیانی در ارتباط باشید.**")

async def start_self_bot(user_id, api_id, api_hash, message_id=None, language="fa"):
    try:
        user_folder = f"selfs/self-{user_id}"
        
        async with lock:
            if user_id in temp_Client:
                try:
                    client_data = temp_Client[user_id]
                    if client_data["client"].is_connected:
                        await client_data["client"].disconnect()
                except:
                    pass
                finally:
                    if user_id in temp_Client:
                        del temp_Client[user_id]
        
        user_info = get_data(f"SELECT expir, phone FROM user WHERE id = '{user_id}' LIMIT 1")
        if not user_info:
            if message_id:
                await app.edit_message_text(user_id, message_id, "**• اطلاعات کاربر یافت نشد.**")
            else:
                await app.send_message(user_id, "**• اطلاعات کاربر یافت نشد.**")
            return False

        expir_days = user_info.get("expir", 0)
        phone_number = user_info.get("phone", "ندارد")

        try:
            tg_user = await app.get_users(user_id)
            first_name = html.escape(tg_user.first_name or "ندارد")
            last_name = html.escape(tg_user.last_name or "ندارد")
            username = f"@{tg_user.username}" if tg_user.username else "ندارد"
            user_link = f'<a href="tg://user?id={user_id}">{first_name} {last_name}</a>'
        except:
            first_name = "نامشخص"
            last_name = ""
            username = "ندارد"
            user_link = f"آیدی: {user_id}"
        
        def cleanup_locked_files():
            base_path = f"/home/amyeyenn/public_html/sessions/{user_id}"
            files_to_remove = [
                f"{base_path}.session-journal",
                f"{base_path}.session-wal", 
                f"{base_path}.session-shm",
                f"sessions/{user_id}.session-journal",
                f"sessions/{user_id}.session-wal",
                f"sessions/{user_id}.session-shm"
            ]
            
            removed = []
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        removed.append(os.path.basename(file_path))
                    except Exception as e:
                        pass
            
            return removed
        
        await asyncio.sleep(3)
        
        if not os.path.isdir(user_folder):
            if message_id:
                await app.edit_message_text(user_id, message_id, "**• عملیات دچار مشکل شد!**")
            else:
                await app.send_message(user_id, "**• عملیات دچار مشکل شد!**")
            return False
        
        self_py_path = os.path.join(user_folder, "self.py")
        if not os.path.exists(self_py_path):
            if message_id:
                await app.edit_message_text(user_id, message_id, "**• فایل پیدا نشد، با پشتیبانی در ارتباط باشید.**")
            else:
                await app.send_message(user_id, "**• فایل پیدا نشد، با پشتیبانی در ارتباط باشید.**")
            return False
        
        log_file = os.path.join(user_folder, f"self_{user_id}_{int(time.time())}.log")
        
        process = subprocess.Popen(
            ["python3", "self.py", str(user_id), str(api_id), api_hash, Helper_ID],
            cwd=user_folder,
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT,
            text=True
        )
        
        await asyncio.sleep(5)
        
        return_code = process.poll()
        
        if return_code is not None:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                if message_id:
                    await app.edit_message_text(user_id, message_id, "**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**")
                else:
                    await app.send_message(user_id, "**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**")
                
                await app.send_message(Admin,
                    f"**• عملیات نصب سلف برای کاربر [ {user_id} ] با خطا مواجه شد :** ```\n{log_content[:1500]}\n```")
                
            else:
                await app.send_message(Admin, f"**• خطا در نصب ربات کاربر [ {user_id} ]\n• لاگ نصب ثبت نشده است.**")
            
            return False
        
        await asyncio.sleep(10)
        
        return_code = process.poll()
        
        if return_code is None:
            pid = process.pid
            
            update_data(f"UPDATE user SET self = 'active' WHERE id = '{user_id}'")
            update_data(f"UPDATE user SET pid = '{pid}' WHERE id = '{user_id}'")
            
            add_admin(user_id)
            
            await setscheduler(user_id)
            
            if language == "fa":
                help_command = "راهنما"
            else:
                help_command = "HELP"
            
            success_message = f"""**• سلف شما نصب و روشن شد.
با دستور [ {help_command} ] میتونید راهنمای سلف رو دریافت کنید.

لطفا بعد نصب سلف حتما اگر رمز دومرحله ای فعال دارید اون رو عوض کنید و یا اکر رمز دومرحله ای روی اکانتتون فعال ندارید، فعال کنید و حواستون باشه فراموشش نکنید.

در صورتی که جوابی دریافت نمیکنید یک دقیقه صبر کنید و بعد دستور بدید، و اکر باز هم جوابی نگرفتید از منوی اصلی به بخش پشتیبانی مراجعه کنید و موضوع رو اطلاع بدید.**"""
            
            if message_id:
                await app.edit_message_text(user_id, message_id, success_message)
            else:
                await app.send_message(user_id, success_message)
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) > 10 else lines
                    log_preview = "".join(last_lines)
              
            await app.send_message(Admin, f"**• خرید #اشتراک :\n• نام : [ {first_name} ]\n• یوزرنیم : [ {username} ]\n• آیدی عددی : [ `{user_id}` ]\n• شماره : [ `{phone_number}` ]\n• انقضا : [ `{expir_days}` ]\n• PID : [ `{pid}` ]\n• Api ID : [ `{api_id}` ]\n• Api Hash : [ `{api_hash}` ]\n• زبان : [ `{language}` ]\n ‌ ‌ ‌‌‌‌‌‌‌\n ‌ ‌ ‌**")
            
            await asyncio.sleep(15)
            
            return True
        else:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                if message_id:
                    await app.edit_message_text(user_id, message_id, "**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**")
                else:
                    await app.send_message(user_id, "**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**")
                return False
            
    except subprocess.TimeoutExpired:
        if message_id:
            await app.edit_message_text(user_id, message_id, "**• خطا، با پشتیبانی در ارتباط باشید.**")
        else:
            await app.send_message(user_id, "**• خطا، با پشتیبانی در ارتباط باشید.**")
        return False
        
    except Exception as e:
        error_msg = f"**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**"
        if message_id:
            await app.edit_message_text(user_id, message_id, error_msg)
        else:
            await app.send_message(user_id, error_msg)
        return False
				
def detect_bank(card_number):
    prefix = card_number[:6]
    
    if prefix == "627412":
        return "اقتصاد نوین"
    elif prefix == "207177":
        return "توسعه صادرات ایران"
    elif prefix == "627381":
        return "انصار"
    elif prefix == "502229":
        return "پاسارگاد"
    elif prefix == "505785":
        return "ایران زمین"
    elif prefix == "502806":
        return "شهر"
    elif prefix == "622106":
        return "پارسیان"
    elif prefix == "502908":
        return "توسعه تعاون"
    elif prefix == "639194":
        return "پارسیان"
    elif prefix == "502910":
        return "کارآفرین"
    elif prefix == "627884":
        return "پارسیان"
    elif prefix == "502938":
        return "دی"
    elif prefix == "639347":
        return "پاسارگاد"
    elif prefix == "505416":
        return "گردشگری"
    elif prefix == "502229":
        return "پاسارگاد"
    elif prefix == "505785":
        return "ایران زمین"
    elif prefix == "636214":
        return "آینده"
    elif prefix == "505801":
        return "موسسه اعتباری کوثر (سپه)"
    elif prefix == "627353":
        return "تجارت"
    elif prefix == "589210":
        return "سپه"
    elif prefix == "502908":
        return "توسعه تعاون"
    elif prefix == "589463":
        return "رفاه کارگران"
    elif prefix == "627648":
        return "توسعه صادرات ایران"
    elif prefix == "603769":
        return "صادرات ایران"
    elif prefix == "207177":
        return "توسعه صادرات ایران"
    elif prefix == "603770":
        return "کشاورزی"
    elif prefix == "636949":
        return "حکمت ایرانیان (سپه)"
    elif prefix == "603799":
        return "ملی ایران"
    elif prefix == "502938":
        return "دی"
    elif prefix == "606373":
        return "قرض الحسنه مهر ایران"
    elif prefix == "589463":
        return "رفاه کارگران"
    elif prefix == "610433":
        return "ملت"
    elif prefix == "621986":
        return "سامان"
    elif prefix == "621986":
        return "سامان"
    elif prefix == "589210":
        return "سپه"
    elif prefix == "622106":
        return "پارسیان"
    elif prefix == "639607":
        return "سرمایه"
    elif prefix == "627353":
        return "تجارت"
    elif prefix == "639346":
        return "سینا"
    elif prefix == "627381":
        return "انصار (سپه)"
    elif prefix == "502806":
        return "شهر"
    elif prefix == "627412":
        return "اقتصاد نوین"
    elif prefix == "603769":
        return "صادرات ایران"
    elif prefix == "627488":
        return "کارآفرین"
    elif prefix == "627961":
        return "صنعت و معدن"
    elif prefix == "627648":
        return "توسعه صادرات ایران"
    elif prefix == "606373":
        return "قرض الحسنه مهر ایران"
    elif prefix == "627760":
        return "پست ایران"
    elif prefix == "639599":
        return "قوامین"
    elif prefix == "627884":
        return "پارسیان"
    elif prefix == "627488":
        return "کارآفرین"
    elif prefix == "627961":
        return "صنعت و معدن"
    elif prefix == "502910":
        return "کارآفرین"
    elif prefix == "628023":
        return "مسکن"
    elif prefix == "603770":
        return "کشاورزی"
    elif prefix == "628157":
        return "موسسه اعتباری توسعه"
    elif prefix == "639217":
        return "کشاورزی"
    elif prefix == "636214":
        return "آینده"
    elif prefix == "505416":
        return "گردشگری"
    elif prefix == "636795":
        return "مرکزی"
    elif prefix == "636795":
        return "مرکزی"
    elif prefix == "636949":
        return "حکمت ایرانیان (سپه)"
    elif prefix == "628023":
        return "مسکن"
    elif prefix == "639194":
        return "پارسیان"
    elif prefix == "610433":
        return "ملت"
    elif prefix == "639217":
        return "کشاورزی"
    elif prefix == "991975":
        return "ملت"
    elif prefix == "639346":
        return "سینا"
    elif prefix == "603799":
        return "ملی ایران"
    elif prefix == "639347":
        return "پاسارگاد"
    elif prefix == "639370":
        return "مهر اقتصاد (سپه)"
    elif prefix == "639370":
        return "مهر اقتصاد (سپه)"
    elif prefix == "627760":
        return "پست ایران"
    elif prefix == "639599":
        return "قوامین (سپه)"
    elif prefix == "628157":
        return "موسسه اعتباری توسعه"
    elif prefix == "639607":
        return "سرمایه"
    elif prefix == "505801":
        return "موسسه اعتباری کوثر (سپه)"
    else:
        return "نامشخص"


def get_setting(key, default=None):
    result = get_data(f"SELECT setting_value FROM settings WHERE setting_key = '{key}'")
    return result["setting_value"] if result else default

def update_setting(key, value):
    update_data(f"UPDATE settings SET setting_value = '{value}' WHERE setting_key = '{key}'")

def get_all_settings():
    return get_datas("SELECT * FROM settings ORDER BY id")

def get_prices():
    return {
        "1month": get_setting("price_1month", "75000"),
        "2month": get_setting("price_2month", "150000"),
        "3month": get_setting("price_3month", "220000"),
        "4month": get_setting("price_4month", "275000"),
        "5month": get_setting("price_5month", "340000"),
        "6month": get_setting("price_6month", "390000"),
    }

def get_main_keyboard(user_id):
    user = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
    expir = user["expir"] if user else 0
    
    # گرفتن کانال‌ها از دیتابیس
    help_channel = get_channel('help')
    main_channel = get_channel('main')
    
    help_channel_username = get_channel_username(help_channel['channel_id']) if help_channel else "SHAH_SELF"
    main_channel_username = get_channel_username(main_channel['channel_id']) if main_channel else "SHAH_SELF"
    
    keyboard = [
        [InlineKeyboardButton(text="پشتیبانی 👨‍💻", callback_data="Support")],
        [InlineKeyboardButton(text="راهنما 🗒️", url=f"https://t.me/{help_channel_username}"),
         InlineKeyboardButton(text="دستیار چیست؟ 🧐", callback_data="WhatSelf")],
        [InlineKeyboardButton(text=f"انقضا : ( {expir} روز )", callback_data="ExpiryStatus")],
        [InlineKeyboardButton(text="خرید اشتراک 💵", callback_data="BuySub"),
         InlineKeyboardButton(text="احراز هویت ✔️", callback_data="AccVerify")]
    ]
    
    if expir > 0:
        keyboard.append(
            [InlineKeyboardButton(text="تمدید با کد 💶", callback_data="BuyCode")]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton(text="خرید با کد 💶", callback_data="BuyCode")]
        )
    
    if str(user_id) == str(Admin):
        keyboard.append(
            [InlineKeyboardButton(text="مدیریت 🎈", callback_data="AdminPanel")]
        )
    elif is_sales_admin(user_id):
        keyboard.append(
            [InlineKeyboardButton(text="پنل ادمین فروش 🛒", callback_data="SalesAdminPanel")]
        )
    
    keyboard.append(
        [InlineKeyboardButton(text="نرخ 💎", callback_data="Price")]
    )
    
    if expir > 0:
        user_folder = f"selfs/self-{user_id}"
        if os.path.isdir(user_folder):
            current_lang = get_current_language(user_id)
            lang_display = "فارسی 🇮🇷" if current_lang == "fa" else "انگلیسی 🇬🇧"
            
            keyboard.extend([
                [InlineKeyboardButton(text="ورود / نصب ⏏️", callback_data="InstallSelf"),
                 InlineKeyboardButton(text="تغییر زبان 🇬🇧", callback_data="ChangeLang")],
                [InlineKeyboardButton(text="وضعیت ⚙️", callback_data="SelfStatus")],
                [InlineKeyboardButton(text=f"زبان : ( {lang_display} )", callback_data="text")]
            ])
        else:
            keyboard.extend([
                [InlineKeyboardButton(text="ورود / نصب ⏏️", callback_data="InstallSelf"),
                InlineKeyboardButton(text="تغییر زبان 🇬🇧", callback_data="ChangeLang")],
                [InlineKeyboardButton(text="وضعیت ⚙️", callback_data="SelfStatus")]
            ])
    
    keyboard.append(
        [InlineKeyboardButton(text="کانال ما 📢", url=f"https://t.me/{main_channel_username}")]
    )
    
    return InlineKeyboardMarkup(keyboard)

AdminPanelKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="آمار 📊", callback_data="AdminStats")],
        [InlineKeyboardButton(text="ارسال همگانی", callback_data="AdminBroadcast"),
         InlineKeyboardButton(text="فوروارد همگانی ✉️", callback_data="AdminForward")],
        [InlineKeyboardButton(text="مدیریت ادمین‌ها 👥", callback_data="AdminManagement")],  # اضافه شده
        [InlineKeyboardButton(text="بلاک کاربر 🚫", callback_data="AdminBlock"),
         InlineKeyboardButton(text="آنبلاک کاربر ✅️", callback_data="AdminUnblock")],
        [InlineKeyboardButton(text="افزودن انقضا ➕", callback_data="AdminAddExpiry"),
         InlineKeyboardButton(text="کسر انقضا ➖", callback_data="AdminDeductExpiry")],
        [InlineKeyboardButton(text="فعال کردن سلف 🔵", callback_data="AdminActivateSelf"),
         InlineKeyboardButton(text="غیرفعال کردن سلف 🔴", callback_data="AdminDeactivateSelf")],
        [InlineKeyboardButton(text="ساخت کد 🔑", callback_data="AdminCreateCode"),
         InlineKeyboardButton(text="لیست کدها 📋", callback_data="AdminListCodes")],
        [InlineKeyboardButton(text="حذف کد ❌", callback_data="AdminDeleteCode")],
        [InlineKeyboardButton(text="روشن کردن ربات 🔵", callback_data="AdminTurnOn"),
         InlineKeyboardButton(text="خاموش کردن ربات 🔴", callback_data="AdminTurnOff")],
        [InlineKeyboardButton(text="تنظیمات ⚙️", callback_data="AdminSettings")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
    ]
)

# اضافه کردن به AdminSettingsKeyboard
AdminSettingsKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="تغییر متن استارت 📝", callback_data="EditStartMessage")],
        [InlineKeyboardButton(text="تغییر متن نرخ 💰", callback_data="EditPriceMessage")],
        [InlineKeyboardButton(text="تغییر متن سلف 🤖", callback_data="EditSelfMessage")],
        [InlineKeyboardButton(text="تغییر قیمت‌ها 📊", callback_data="EditPrices")],
        [InlineKeyboardButton(text="تغییر اطلاعات کارت 💳", callback_data="EditCardInfo")],
        [InlineKeyboardButton(text="محدودیت شماره 📱", callback_data="PhoneRestriction")],
        [InlineKeyboardButton(text="مدیریت کانال‌ها 📢", callback_data="ManageChannels")],
        [InlineKeyboardButton(text="مشاهده تنظیمات 👁️", callback_data="ViewSettings")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
    ]
)

# اضافه کردن کیبورد مدیریت کانال‌ها
ChannelManagementKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="کانال اصلی جوین اجباری", callback_data="EditMainChannel")],
        [InlineKeyboardButton(text="کانال راهنما", callback_data="EditHelpChannel")],
        [InlineKeyboardButton(text="کانال API", callback_data="EditApiChannel")],
        [InlineKeyboardButton(text="افزودن کانال جدید ➕", callback_data="AddExtraChannel")],
        [InlineKeyboardButton(text="حذف کانال ➖", callback_data="RemoveChannel")],
        [InlineKeyboardButton(text="لیست کانال‌ها 📋", callback_data="ListChannels")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
    ]
)

# کیبورد مدیریت ادمین‌ها
AdminManagementKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="افزودن ادمین ➕", callback_data="AddAdmin")],
        [InlineKeyboardButton(text="حذف ادمین ➖", callback_data="RemoveAdmin")],
        [InlineKeyboardButton(text="لیست ادمین‌ها 📋", callback_data="ListAdmins")],
        [InlineKeyboardButton(text="تنظیم دسترسی ادمین ⚙️", callback_data="SetAdminPermissions")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
    ]
)

# کیبورد تنظیم دسترسی ادمین
AdminPermissionsKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="فروش", callback_data="PermSales")],
        [InlineKeyboardButton(text="مدیریت کامل", callback_data="PermFull")],
        [InlineKeyboardButton(text="مدیریت تراکنش‌ها", callback_data="PermTransactions")],
        [InlineKeyboardButton(text="پشتیبانی", callback_data="PermSupport")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
    ]
)

# کیبورد پنل ادمین فروش
SalesAdminPanelKeyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="خرید/تمدید اشتراک 💰", callback_data="SalesBuySub")],
        [InlineKeyboardButton(text="حذف مشتری ❌", callback_data="SalesRemoveCustomer")],
        [InlineKeyboardButton(text="مشتریان من 👥", callback_data="SalesMyCustomers")],
        [InlineKeyboardButton(text="وضعیت سلف مشتری ⚙️", callback_data="SalesCustomerStatus")],
        [InlineKeyboardButton(text="تغییر زبان مشتری 🌐", callback_data="SalesChangeLang")],
        [InlineKeyboardButton(text="ورود/نصب سلف مشتری ⏏️", callback_data="SalesInstallSelf")],
        [InlineKeyboardButton(text="افزایش موجودی 💳", callback_data="SalesAddBalance")],
        [InlineKeyboardButton(text="تعیین نرخ خود 📊", callback_data="SalesSetPrices")],
        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
    ]
)

@app.on_message(filters.private, group=-1)
async def update(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    if user is None:
        update_data(f"INSERT INTO user(id) VALUES({m.chat.id})")

@app.on_inline_query()
async def inline_code_handler(client, inline_query):
    query = inline_query.query.strip()
    user_id = inline_query.from_user.id
    
    user = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
    
    if user and user["step"].startswith("install_code-"):
        if not query:
            return
        
        if not query.isdigit():
            return
        
        if len(query) < 5:
            return
        
        code = query[:5]
        
        if len(code) == 5:
            step_parts = user["step"].split("-")
            if len(step_parts) >= 4:
                phone = step_parts[1]
                api_id = step_parts[2]
                api_hash = step_parts[3]
                
                results = [
                    InlineQueryResultArticle(
                        title="دریافت کد",
                        description=f"کد وارد شده شما : ( {code} )",
                        id="1",
                        input_message_content=InputTextMessageContent(
                            message_text=f"**تنظیم شد.**")
                        )]
                
                await inline_query.answer(
                    results=results,
                    cache_time=0,
                    is_personal=True
                )
                
                await asyncio.sleep(0.5)
                
                try:
                    success = await verify_code_and_login(user_id, phone, api_id, api_hash, code)
                    
                    if success:
                        await app.send_message(
                            user_id,
                            "**• ورود به اکانت با موفقیت انجام شد، درحال نصب نهایی سلف، لطفا صلور باشید.**"
                        )
                    else:
                        pass
                        
                except Exception as e:
                    await app.send_message(
                        user_id,
                        "**خطا، با پشتیبانی در ارتباط باشید.**"
                    )

@app.on_message(filters.private&filters.command("start"))
@checker
async def start_handler(c, m):
    keyboard = get_main_keyboard(m.chat.id)
    user_link = f'<a href="tg://user?id={m.chat.id}">{html.escape(m.chat.first_name)}</a>'
    start_message = get_setting("start_message").format(user_link=user_link)
    await app.send_message(m.chat.id, start_message, reply_markup=keyboard)
    update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
    
    async with lock:
        if m.chat.id in temp_Client:
            try:
                await temp_Client[m.chat.id]["client"].disconnect()
            except:
                pass
            del temp_Client[m.chat.id]
    
    journal_file = f"sessions/{m.chat.id}.session-journal"
    if os.path.isfile(journal_file):
        os.remove(journal_file)

@app.on_callback_query()
@checker
async def callback_handler(c, call):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{call.from_user.id}' LIMIT 1")
    phone_number = user["phone"] if user else None
    expir = user["expir"] if user else 0
    chat_id = call.from_user.id
    m_id = call.message.id
    data = call.data
    username = f"@{call.from_user.username}" if call.from_user.username else "وجود ندارد"

    if data == "BuySub" or data == "Back2":
        if user["phone"] is None:
            await app.delete_messages(chat_id, m_id)
            await app.send_message(chat_id, "**لطفا با استفاده از دکمه زیر شماره موبایل خود را به اشتراک بگذارید.**", reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(text="اشتراک گذاری شماره", request_contact=True)
                    ]
                ],resize_keyboard=True
            ))
            update_data(f"UPDATE user SET step = 'contact' WHERE id = '{call.from_user.id}' LIMIT 1")
        else:
            user_cards = get_user_cards(call.from_user.id)
            if user_cards:
                keyboard_buttons = []
                for card in user_cards:
                    card_number = card["card_number"]
                    bank_name = card["bank_name"] if card["bank_name"] else "نامشخص"
                    masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
                    keyboard_buttons.append([
                        InlineKeyboardButton(text=masked_card, callback_data=f"SelectCardForPayment-{card['id']}")
                    ])
                keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")])
                
                await app.edit_message_text(chat_id, m_id,
                                           "**• لطفا انتخاب کنید برای پرداخت از کدام کارت احراز شده ی خود میخواهید استفاده کنید.**",
                                           reply_markup=InlineKeyboardMarkup(keyboard_buttons))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
            else:
                await app.edit_message_text(chat_id, m_id,
                                           "**• برای خرید باید ابتدا احراز هویت کنید.**",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="احراز هویت ✔️", callback_data="AccVerify")]
                                           ]))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data.startswith("SelectCardForPayment-"):
        card_id = data.split("-")[1]
        card = get_card_by_id(card_id)
        if card:
            update_data(f"UPDATE user SET step = 'select_subscription-{card_id}' WHERE id = '{call.from_user.id}' LIMIT 1")
        
            prices = get_prices()
        
            await app.edit_message_text(chat_id, m_id,
                                   "**• لطفا از گزینه های زیر انتخاب کنید میخواهید دستیار را برای چند ماه خریداری کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text=f"(1) ماه معادل {prices['1month']} تومان", callback_data=f"Sub-30-{prices['1month']}")],
                                       [InlineKeyboardButton(text=f"(2) ماه معادل {prices['2month']} تومان", callback_data=f"Sub-60-{prices['2month']}")],
                                       [InlineKeyboardButton(text=f"(3) ماه معادل {prices['3month']} تومان", callback_data=f"Sub-90-{prices['3month']}")],
                                       [InlineKeyboardButton(text=f"(4) ماه معادل {prices['4month']} تومان", callback_data=f"Sub-120-{prices['4month']}")],
                                       [InlineKeyboardButton(text=f"(5) ماه معادل {prices['5month']} تومان", callback_data=f"Sub-150-{prices['5month']}")],
                                       [InlineKeyboardButton(text=f"(6) ماه معادل {prices['6month']} تومان", callback_data=f"Sub-180-{prices['6month']}")],
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="BuySub")]
                                   ]))

    elif data.startswith("Sub-"):
        params = data.split("-")
        expir_count = params[1]
        cost = params[2]
        card_id = user["step"].split("-")[1]
        card = get_card_by_id(card_id)
    
        if card:
            card_number = card["card_number"]
            masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
        
            bot_card_number = get_setting("card_number")
            bot_card_name = get_setting("card_name")
        
            await app.edit_message_text(chat_id, m_id, f"**• لطفا مبلغ ( `{cost}` تومان ) رو با کارتی که احراز هویت و انتخاب کردید یعنی [ `{card_number}` ] به کارت زیر واریز کنید و فیش واریز خود را همینجا ارسال کنید.\n\n[ `{bot_card_number}` ]\nبه نام : {bot_card_name}\n\n• ربات آماده دریافت فیش واریزی شماست :**")
        
            update_data(f"UPDATE user SET step = 'payment_receipt-{expir_count}-{cost}-{card_id}' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Price":
        prices = get_prices()
        price_message = get_setting("price_message").format(
            price_1month=prices["1month"],
            price_2month=prices["2month"],
            price_3month=prices["3month"],
            price_4month=prices["4month"],
            price_5month=prices["5month"],
            price_6month=prices["6month"]
        )
        await app.edit_message_text(chat_id, m_id, price_message, 
                       reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                               ]))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "AccVerify":
        user_cards = get_user_cards(call.from_user.id)
    
        if user_cards:
            cards_text = "**• به منوی احراز هویت خوش آمدید:\n\nکارت های احراز شده شما :\n**"
            for idx, card in enumerate(user_cards, 1):
                card_number = card["card_number"]
                bank_name = card["bank_name"] if card["bank_name"] else "نامشخص"
                masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
                cards_text += f"**{idx} - {bank_name} [ `{card_number}` ] \n‌‌‌‌‌ ‌‌‌‌‌‌‌‌ ‌ ‌ ‌‌‌‌‌‌‌‌ ‌‌‌‌‌‌‌‌‌ ‌‌‌‌‌‌‌\n**"
        
            keyboard_buttons = []
            keyboard_buttons.append(
                [InlineKeyboardButton(text="کارت جدید ➕", callback_data="AddNewCard"),
                InlineKeyboardButton(text="حذف کارت ➖", callback_data="DeleteCard")])
            keyboard_buttons.append(
                [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")])
        
            await app.edit_message_text(chat_id, m_id, cards_text, 
                                   reply_markup=InlineKeyboardMarkup(keyboard_buttons))
        else:
            await app.edit_message_text(chat_id, m_id, 
                                   "**• به منوی احراز هویت خوش آمدید ، لطفا انتخاب کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="➕ کارت جدید", callback_data="AddNewCard"),
                                       InlineKeyboardButton(text="حذف کارت ➖", callback_data="DeleteCard")],
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                                   ]))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "AddNewCard":
        await app.edit_message_text(chat_id, m_id, """**• به بخش احراز هویت خوش آمدید.  برای احراز هویت از کارت خود ( حتما کارتی که با آن میخواهید پرداخت انجام دهید ) عکس بگیرید و ارسال کنید.  
• اسم و فامیل شما روی کارت باید کاملا مشخص باشد و عکس کارت داخل برنامه قابل قبول نمیباشد...

• نکات :
1) شماره کارت و نام صاحب کارت کاملا مشخص باشد.
2) لطفا تاریخ اعتبار و Cvv2 کارت خود را بپوشانید!
3) فقط با کارتی که احراز هویت میکنید میتوانید خرید انجام بدید و اگر با کارت دیگری اقدام کنید تراکنش ناموفق میشود و هزینه از سمت خودِ بانک به شما بازگشت داده میشود.
4) در صورتی که توانایی ارسال عکس از کارت را ندارید تنها راه حل ارسال عکس از کارت ملی یا شناسنامه صاحب کارت است.

لطفا عکس از کارتی که میخواهید با آن خرید انجام دهید ارسال کنید...**""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AccVerify")]
        ]))
        update_data(f"UPDATE user SET step = 'card_photo' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "DeleteCard":
        user_cards = get_user_all_cards(call.from_user.id)
    
        verified_cards = [card for card in user_cards if card["verified"] == "verified"]
    
        if verified_cards:
            keyboard_buttons = []
            for card in verified_cards:
                card_number = card["card_number"]
                masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
                keyboard_buttons.append([
                    InlineKeyboardButton(text=masked_card, callback_data=f"SelectCard-{card['id']}")
                ])
            keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AccVerify")])
        
            await app.edit_message_text(chat_id, m_id,
                                   "**• لطفا انتخاب کنید میخواهید کدام کارت خود را حذف کنید.**",
                                   reply_markup=InlineKeyboardMarkup(keyboard_buttons))
        else:
            await app.answer_callback_query(call.id, text="• هیچ کارت احراز هویت شده ای برای حذف ندارید •", show_alert=True)

    elif data.startswith("SelectCard-"):
        card_id = data.split("-")[1]
        card = get_card_by_id(card_id)
        if card:
            card_number = card["card_number"]
            masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
            await app.edit_message_text(chat_id, m_id,
                                       f"**• آیا مطمئن هستید که میخواهید کارت [ `{masked_card}` ] را حذف کنید؟**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="بله", callback_data=f"ConfirmDelete-{card_id}"),
                                            InlineKeyboardButton(text="خیر", callback_data="AccVerify")]
                                       ]))

    elif data.startswith("ConfirmDelete-"):
        card_id = data.split("-")[1]
        card = get_card_by_id(card_id)
        if card:
            card_number = card["card_number"]
            bank_name = card["bank_name"] if card["bank_name"] else "نامشخص"
            masked_card = f"{card_number[:4]} - - - - - - {card_number[-4:]}"
            delete_card(card_id)
            await app.edit_message_text(chat_id, m_id,
                                       f"**• کارت ( `{bank_name}` - `{card_number}` ) با موفقیت حذف شد.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AccVerify")]
                                       ]))
    
    elif data.startswith("AdminApproveBalance-"):
        params = data.split("-")
        admin_id = int(params[1])
        amount = int(params[2])
        transaction_id = params[3]
        
        # افزایش موجودی ادمین
        update_sales_admin_balance(admin_id, amount)
        
        await app.edit_message_text(Admin, m_id,
                                   f"**✅ موجودی ادمین افزایش یافت.**\n\n"
                                   f"**آیدی ادمین:** `{admin_id}`\n"
                                   f"**مبلغ:** `{amount:,}` تومان\n"
                                   f"**شناسه تراکنش:** `{transaction_id}`\n"
                                   f"**موجودی جدید:** `{get_sales_admin_balance(admin_id)['balance']:,}` تومان")
        
        # اطلاع به ادمین
        await app.send_message(admin_id,
                             f"**✅ موجودی شما افزایش یافت!**\n\n"
                             f"**مبلغ:** `{amount:,}` تومان\n"
                             f"**شناسه تراکنش:** `{transaction_id}`\n"
                             f"**موجودی جدید:** `{get_sales_admin_balance(admin_id)['balance']:,}` تومان")

    elif data.startswith("AdminRejectBalance-"):
        params = data.split("-")
        admin_id = int(params[1])
        transaction_id = params[2]
        
        await app.edit_message_text(Admin, m_id,
                                   f"**❌ درخواست افزایش موجودی رد شد.**\n\n"
                                   f"**آیدی ادمین:** `{admin_id}`\n"
                                   f"**شناسه تراکنش:** `{transaction_id}`")
        
        # اطلاع به ادمین
        await app.send_message(admin_id,
                             f"**❌ درخواست افزایش موجودی شما رد شد.**\n\n"
                             f"**شناسه تراکنش:** `{transaction_id}`\n"
                             f"**لطفا با مالک در ارتباط باشید.**")
    
    elif data == "WhatSelf":
        whatself_message = get_setting("whatself_message")
        await app.edit_message_text(chat_id, m_id, whatself_message, 
                               reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                               ]))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")

    elif data == "Support":
        await app.edit_message_text(chat_id, m_id, "**• شما با موفقیت به پشتیبانی متصل شدید!\nلطفا دقت کنید که توی پشتیبانی اسپم ندید و از دستورات سلف توی پشتیبانی استفاده نکنید، اکنون میتوانید پیام خود را ارسال کنید.**", reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="لغو اتصال 💥", callback_data="Back")
                ]
            ]
        ))
        update_data(f"UPDATE user SET step = 'support' WHERE id = '{call.from_user.id}' LIMIT 1")
    
    elif data == "AdminManagement":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, 
                                       "**مدیر گرامی، به بخش مدیریت ادمین‌ها خوش آمدید.**",
                                       reply_markup=AdminManagementKeyboard)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "AddAdmin":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا آیدی عددی کاربر را برای اضافه کردن به ادمین‌ها ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                       ]))
            update_data(f"UPDATE user SET step = 'add_admin' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "RemoveAdmin":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            admins = get_all_admins()
            if admins:
                keyboard_buttons = []
                for admin in admins:
                    try:
                        user_info = await app.get_users(admin['user_id'])
                        name = html.escape(user_info.first_name or "نامشخص")
                        username = f"@{user_info.username}" if user_info.username else "ندارد"
                        display = f"{name} ({username})"
                    except:
                        display = f"آیدی: {admin['user_id']}"
                    
                    keyboard_buttons.append([
                        InlineKeyboardButton(text=display, callback_data=f"SelectAdmin-{admin['user_id']}")
                    ])
                keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")])
                
                await app.edit_message_text(chat_id, m_id,
                                           "**لطفا ادمینی که می‌خواهید حذف کنید را انتخاب کنید:**",
                                           reply_markup=InlineKeyboardMarkup(keyboard_buttons))
            else:
                await app.answer_callback_query(call.id, text="• هیچ ادمینی وجود ندارد •", show_alert=True)

    elif data.startswith("SelectAdmin-"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            admin_id = int(data.split("-")[1])
            try:
                user_info = await app.get_users(admin_id)
                name = html.escape(user_info.first_name or "نامشخص")
                username = f"@{user_info.username}" if user_info.username else "ندارد"
                
                await app.edit_message_text(chat_id, m_id,
                                           f"**آیا مطمئن هستید که می‌خواهید ادمین {name} ({username}) را حذف کنید؟**",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmRemoveAdmin-{admin_id}"),
                                                InlineKeyboardButton(text="خیر ✖️", callback_data="AdminManagement")]
                                           ]))
            except:
                await app.edit_message_text(chat_id, m_id,
                                           f"**آیا مطمئن هستید که می‌خواهید ادمین با آیدی {admin_id} را حذف کنید؟**",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmRemoveAdmin-{admin_id}"),
                                                InlineKeyboardButton(text="خیر ✖️", callback_data="AdminManagement")]
                                           ]))

    elif data.startswith("ConfirmRemoveAdmin-"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            admin_id = int(data.split("-")[1])
            remove_admin_role(admin_id)
            delete_admin(admin_id)
            
            await app.edit_message_text(chat_id, m_id,
                                       f"**✅ ادمین با آیدی {admin_id} با موفقیت حذف شد.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                       ]))

    elif data == "ListAdmins":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            admins = get_all_admins()
            if admins:
                admins_text = "**لیست ادمین‌ها:**\n\n"
                for idx, admin in enumerate(admins, 1):
                    try:
                        user_info = await app.get_users(admin['user_id'])
                        name = html.escape(user_info.first_name or "نامشخص")
                        username = f"@{user_info.username}" if user_info.username else "ندارد"
                    except:
                        name = "نامشخص"
                        username = "ندارد"
                    
                    role_text = {
                        'sales': 'فروش',
                        'full': 'کامل',
                        'transactions': 'تراکنش',
                        'support': 'پشتیبانی'
                    }.get(admin['role_type'], admin['role_type'])
                    
                    permissions = []
                    if admin.get('can_sell'):
                        permissions.append("فروش")
                    if admin.get('can_manage'):
                        permissions.append("مدیریت")
                    if admin.get('can_transactions'):
                        permissions.append("تراکنش")
                    if admin.get('can_support'):
                        permissions.append("پشتیبانی")
                    
                    permissions_text = "، ".join(permissions) if permissions else "بدون دسترسی"
                    
                    admins_text += f"**{idx}. {name} ({username})**\n"
                    admins_text += f"**آیدی:** `{admin['user_id']}`\n"
                    admins_text += f"**نقش:** {role_text}\n"
                    admins_text += f"**دسترسی‌ها:** {permissions_text}\n"
                    admins_text += f"**تاریخ اضافه شدن:** {admin['created_at']}\n"
                    admins_text += "─" * 20 + "\n"
                
                await app.edit_message_text(chat_id, m_id, admins_text,
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                           ]))
            else:
                await app.edit_message_text(chat_id, m_id,
                                           "**هیچ ادمینی وجود ندارد.**",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                           ]))

    elif data == "SetAdminPermissions":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا نوع دسترسی را انتخاب کنید:**",
                                       reply_markup=AdminPermissionsKeyboard)
            update_data(f"UPDATE user SET step = 'select_admin_for_permission' WHERE id = '{chat_id}' LIMIT 1")

    elif data.startswith("Perm"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            perm_type = data.replace("Perm", "").lower()
            await app.edit_message_text(chat_id, m_id,
                                       f"**لطفا آیدی عددی ادمین را برای تنظیم دسترسی {perm_type} ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SetAdminPermissions")]
                                       ]))
            update_data(f"UPDATE user SET step = f'set_{perm_type}_permission' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data.startswith("SalesConfirmInstall-"):
        customer_id = int(data.split("-")[1])
        
        await app.edit_message_text(chat_id, m_id,
                                   f"**در حال نصب سلف برای مشتری...**")
        
        # اینجا باید منطق نصب سلف برای مشتری پیاده‌سازی شود
        # (نیاز به اطلاعات API و شماره مشتری دارد)
        
        await app.edit_message_text(chat_id, m_id,
                                   f"**✅ دستور نصب سلف برای مشتری ارسال شد.**\n\n"
                                   f"**لطفا به مشتری اطلاع دهید که برای نصب سلف باید به ربات اصلی مراجعه کند.**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                   ]))
    
    elif data.startswith("SalesConfirmLang-"):
        params = data.split("-")
        customer_id = int(params[1])
        target_lang = params[2]
        
        success, result = await change_self_language(customer_id, target_lang)
        
        if success:
            new_lang_display = "فارسی 🇮🇷" if target_lang == "fa" else "انگلیسی 🇬🇧"
            
            await app.edit_message_text(chat_id, m_id,
                                       f"**✅ زبان سلف مشتری به {new_lang_display} تغییر یافت.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            
            # ریستارت کردن سلف مشتری
            user_data = get_data(f"SELECT pid FROM user WHERE id = '{customer_id}' LIMIT 1")
            pid = user_data.get("pid") if user_data else None
            
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    await asyncio.sleep(3)
                    
                    try:
                        os.kill(pid, 0)
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
                except Exception as e:
                    pass
        else:
            await app.edit_message_text(chat_id, m_id,
                                       f"**❌ خطا در تغییر زبان: {result}**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
                                       
    elif data.startswith("SalesSub-"):
        params = data.split("-")
        days = int(params[1])
        price = int(params[2])
        customer_id = int(params[3])
        
        # بررسی موجودی ادمین
        balance_info = get_sales_admin_balance(chat_id)
        if balance_info['balance'] < price:
            await app.edit_message_text(chat_id, m_id,
                                       f"**موجودی شما کافی نیست!**\n\n"
                                       f"**موجودی شما:** `{balance_info['balance']:,}` تومان\n"
                                       f"**قیمت اشتراک:** `{price:,}` تومان\n"
                                       f"**کمبود:** `{price - balance_info['balance']:,}` تومان\n\n"
                                       f"**لطفا ابتدا موجودی خود را افزایش دهید.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="افزایش موجودی", callback_data="SalesAddBalance")],
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            return
        
        # کسر از موجودی ادمین
        update_sales_admin_balance(chat_id, -price)
        
        # افزودن روز به کاربر
        customer_data = get_data(f"SELECT expir FROM user WHERE id = '{customer_id}' LIMIT 1")
        old_expir = customer_data['expir'] if customer_data else 0
        new_expir = old_expir + days
        
        update_data(f"UPDATE user SET expir = '{new_expir}' WHERE id = '{customer_id}' LIMIT 1")
        
        # ثبت مشتری برای ادمین
        add_admin_customer(chat_id, customer_id, days, price)
        
        # ارسال پیام به مشتری
        try:
            user_info = await app.get_users(customer_id)
            await app.send_message(customer_id,
                                 f"**اشتراک جدید برای شما خریداری شد!**\n\n"
                                 f"**توسط ادمین:** {html.escape(call.from_user.first_name)}\n"
                                 f"**مدت اشتراک:** {days} روز\n"
                                 f"**انقضای قبلی:** {old_expir} روز\n"
                                 f"**انقضای جدید:** {new_expir} روز\n\n"
                                 f"**می‌توانید از بخش نصب سلف، ربات را نصب کنید.**")
        except:
            pass
        
        # ارسال پیام به ادمین
        await app.edit_message_text(chat_id, m_id,
                                   f"**✅ اشتراک با موفقیت برای مشتری خریداری شد!**\n\n"
                                   f"**آیدی مشتری:** `{customer_id}`\n"
                                   f"**مدت اشتراک:** {days} روز\n"
                                   f"**مبلغ پرداختی:** `{price:,}` تومان\n"
                                   f"**موجودی جدید شما:** `{get_sales_admin_balance(chat_id)['balance']:,}` تومان\n"
                                   f"**انقضای جدید مشتری:** {new_expir} روز",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                   ]))
    
    elif is_sales_admin(chat_id):
        if data == "SalesAdminPanel":
            balance_info = get_sales_admin_balance(chat_id)
            await app.edit_message_text(chat_id, m_id,
                                       f"**سلام ادمین فروش گرامی 👋\n\nموجودی شما: `{balance_info['balance']:,}` تومان**",
                                       reply_markup=SalesAdminPanelKeyboard)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesBuySub":
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا آیدی عددی کاربر را برای خرید اشتراک ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_select_customer' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesRemoveCustomer":
            customers = get_admin_customers(chat_id)
            if customers:
                keyboard_buttons = []
                for customer in customers:
                    try:
                        user_info = await app.get_users(customer['customer_id'])
                        name = html.escape(user_info.first_name or "نامشخص")
                        username = f"@{user_info.username}" if user_info.username else "ندارد"
                        display = f"{name} ({username})"
                    except:
                        display = f"آیدی: {customer['customer_id']}"
                    
                    keyboard_buttons.append([
                        InlineKeyboardButton(text=display, callback_data=f"SelectCustomer-{customer['customer_id']}")
                    ])
                keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")])
                
                await app.edit_message_text(chat_id, m_id,
                                           "**لطفا مشتری که می‌خواهید حذف کنید را انتخاب کنید:**",
                                           reply_markup=InlineKeyboardMarkup(keyboard_buttons))
            else:
                await app.answer_callback_query(call.id, text="• هیچ مشتری ندارید •", show_alert=True)
        
        elif data.startswith("SelectCustomer-"):
            customer_id = int(data.split("-")[1])
            customer_check = check_customer_assigned(customer_id)
            
            if customer_check and customer_check['admin_id'] == chat_id:
                try:
                    user_info = await app.get_users(customer_id)
                    name = html.escape(user_info.first_name or "نامشخص")
                    username = f"@{user_info.username}" if user_info.username else "ندارد"
                    
                    # محاسبه هزینه بازگشتی
                    user_data = get_data(f"SELECT expir FROM user WHERE id = '{customer_id}' LIMIT 1")
                    remaining_days = user_data['expir'] if user_data else 0
                    
                    # قیمت‌های اصلی ربات
                    main_prices = get_prices()
                    price_per_day = int(main_prices['1month']) / 30  # قیمت روزانه
                    
                    # روزهای استفاده شده (فرض: 30 روز اول خرید)
                    used_days = 30 - remaining_days if remaining_days < 30 else 0
                    used_amount = used_days * price_per_day
                    
                    # مبلغ بازگشتی به ادمین
                    refund_amount = customer_check['total_purchased'] - used_amount
                    
                    await app.edit_message_text(chat_id, m_id,
                                               f"**مشتری: {name} ({username})**\n"
                                               f"**آیدی:** `{customer_id}`\n"
                                               f"**مجموع خریدها:** `{customer_check['total_purchased']:,}` تومان\n"
                                               f"**انقضای باقی‌مانده:** `{remaining_days}` روز\n"
                                               f"**مبلغ بازگشتی به شما:** `{max(0, int(refund_amount)):,}` تومان\n\n"
                                               f"**آیا مطمئن هستید که می‌خواهید این مشتری را حذف کنید؟**",
                                               reply_markup=InlineKeyboardMarkup([
                                                   [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmRemoveCustomer-{customer_id}"),
                                                    InlineKeyboardButton(text="خیر ✖️", callback_data="SalesAdminPanel")]
                                               ]))
                except:
                    await app.edit_message_text(chat_id, m_id,
                                               f"**آیا مطمئن هستید که می‌خواهید مشتری با آیدی {customer_id} را حذف کنید؟**",
                                               reply_markup=InlineKeyboardMarkup([
                                                   [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmRemoveCustomer-{customer_id}"),
                                                    InlineKeyboardButton(text="خیر ✖️", callback_data="SalesAdminPanel")]
                                               ]))
        
        elif data.startswith("ConfirmRemoveCustomer-"):
            customer_id = int(data.split("-")[1])
            customer_check = check_customer_assigned(customer_id)
            
            if customer_check and customer_check['admin_id'] == chat_id:
                # محاسبه هزینه بازگشتی
                user_data = get_data(f"SELECT expir FROM user WHERE id = '{customer_id}' LIMIT 1")
                remaining_days = user_data['expir'] if user_data else 0
                
                # قیمت‌های اصلی ربات
                main_prices = get_prices()
                price_per_day = int(main_prices['1month']) / 30
                
                # روزهای استفاده شده
                used_days = 30 - remaining_days if remaining_days < 30 else 0
                used_amount = used_days * price_per_day
                
                # مبلغ بازگشتی
                refund_amount = max(0, customer_check['total_purchased'] - used_amount)
                
                # بازگرداندن پول به ادمین
                update_sales_admin_balance(chat_id, int(refund_amount))
                
                # حذف مشتری
                remove_admin_customer(chat_id, customer_id)
                
                # غیرفعال کردن سلف مشتری
                update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{customer_id}' LIMIT 1")
                if os.path.isdir(f"selfs/self-{customer_id}"):
                    shutil.rmtree(f"selfs/self-{customer_id}")
                
                await app.edit_message_text(chat_id, m_id,
                                           f"**✅ مشتری با آیدی {customer_id} حذف شد.**\n"
                                           f"**مبلغ بازگشتی:** `{int(refund_amount):,}` تومان\n"
                                           f"**موجودی جدید شما:** `{get_sales_admin_balance(chat_id)['balance']:,}` تومان",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                           ]))
        
        elif data == "SalesMyCustomers":
            customers = get_admin_customers(chat_id)
            if customers:
                customers_text = "**مشتریان شما:**\n\n"
                for idx, customer in enumerate(customers, 1):
                    try:
                        user_info = await app.get_users(customer['customer_id'])
                        name = html.escape(user_info.first_name or "نامشخص")
                        username = f"@{user_info.username}" if user_info.username else "ندارد"
                    except:
                        name = "نامشخص"
                        username = "ندارد"
                    
                    # بررسی وضعیت سلف
                    user_data = get_data(f"SELECT self, expir FROM user WHERE id = '{customer['customer_id']}' LIMIT 1")
                    status = "فعال ✅" if user_data and user_data['self'] == 'active' else "غیرفعال ❌"
                    
                    customers_text += f"**{idx}. {name} ({username})**\n"
                    customers_text += f"**آیدی:** `{customer['customer_id']}`\n"
                    customers_text += f"**وضعیت سلف:** {status}\n"
                    customers_text += f"**مجموع خرید:** `{customer['total_purchased']:,}` تومان\n"
                    customers_text += f"**مجموع روزها:** `{customer['total_days']}` روز\n"
                    customers_text += f"**تاریخ اضافه شدن:** {customer['created_at']}\n"
                    customers_text += "─" * 20 + "\n"
                
                await app.edit_message_text(chat_id, m_id, customers_text,
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                           ]))
            else:
                await app.edit_message_text(chat_id, m_id,
                                           "**شما هنوز مشتری ندارید.**",
                                           reply_markup=InlineKeyboardMarkup([
                                               [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                           ]))
        
        elif data == "SalesCustomerStatus":
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا آیدی عددی مشتری را برای بررسی وضعیت سلف ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_customer_status' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesChangeLang":
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا آیدی عددی مشتری را برای تغییر زبان ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_change_lang' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesInstallSelf":
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا آیدی عددی مشتری را برای نصب سلف ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_install_self' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesAddBalance":
            await app.edit_message_text(chat_id, m_id,
                                       "**لطفا مبلغ مورد نظر برای افزایش موجودی را به تومان ارسال کنید:**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_add_balance' WHERE id = '{chat_id}' LIMIT 1")
        
        elif data == "SalesSetPrices":
            sales_prices = get_sales_admin_prices(chat_id)
            await app.edit_message_text(chat_id, m_id,
                                       f"**قیمت‌های فعلی شما:**\n\n"
                                       f"**1 ماهه:** `{sales_prices['price_1month']:,}` تومان\n"
                                       f"**2 ماهه:** `{sales_prices['price_2month']:,}` تومان\n"
                                       f"**3 ماهه:** `{sales_prices['price_3month']:,}` تومان\n"
                                       f"**4 ماهه:** `{sales_prices['price_4month']:,}` تومان\n"
                                       f"**5 ماهه:** `{sales_prices['price_5month']:,}` تومان\n"
                                       f"**6 ماهه:** `{sales_prices['price_6month']:,}` تومان\n\n"
                                       f"**لطفا قیمت‌های جدید را به صورت زیر ارسال کنید:**\n"
                                       f"```\nقیمت_1ماهه\nقیمت_2ماهه\nقیمت_3ماهه\nقیمت_4ماهه\nقیمت_5ماهه\nقیمت_6ماهه\n```",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                       ]))
            update_data(f"UPDATE user SET step = 'sales_set_prices' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "ManageChannels":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                   "**مدیر گرامی، به بخش مدیریت کانال‌های جوین اجباری خوش آمدید.**",
                                   reply_markup=ChannelManagementKeyboard)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "EditMainChannel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_channel = get_channel('main')
            current_text = f"@{get_channel_username(current_channel['channel_id'])}" if current_channel else "تنظیم نشده"
            await app.edit_message_text(chat_id, m_id,
                                   f"**کانال اصلی فعلی: {current_text}\n\nلطفا آیدی کانال جدید را ارسال کنید ( مثال: @channel یا channel ):**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_main_channel' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "EditHelpChannel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_channel = get_channel('help')
            current_text = f"@{get_channel_username(current_channel['channel_id'])}" if current_channel else "تنظیم نشده"
            await app.edit_message_text(chat_id, m_id,
                                   f"**کانال راهنمای فعلی: {current_text}\n\nلطفا آیدی کانال جدید را ارسال کنید (مثال: @channel یا channel):**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_help_channel' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "EditApiChannel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_channel = get_channel('api')
            current_text = f"@{get_channel_username(current_channel['channel_id'])}" if current_channel else "تنظیم نشده"
            await app.edit_message_text(chat_id, m_id,
                                   f"**کانال API فعلی: {current_text}\n\nلطفا آیدی کانال جدید را ارسال کنید (مثال: @channel یا channel):**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_api_channel' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AddExtraChannel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                   "**لطفا آیدی کانال جدید برای جوین اجباری را ارسال کنید (مثال: @channel یا channel):**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                   ]))
            update_data(f"UPDATE user SET step = 'add_extra_channel' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "RemoveChannel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            channels = get_all_channels()
            if channels:
                keyboard_buttons = []
                for channel in channels:
                    channel_type_text = {
                        'main': 'اصلی',
                        'help': 'راهنما',
                        'api': 'API',
                        'extra': 'اضافی'
                    }.get(channel['channel_type'], 'نامشخص')
                    
                    status = "فعال ✔️" if channel['is_active'] else "غیرفعال ✖️"
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            text=f"{channel_type_text}: @{get_channel_username(channel['channel_id'])} {status}",
                            callback_data=f"SelectChannel-{channel['id']}"
                        )
                    ])
                keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")])
                
                await app.edit_message_text(chat_id, m_id,
                                       "**لطفا کانالی که می‌خواهید حذف کنید را انتخاب کنید:**",
                                       reply_markup=InlineKeyboardMarkup(keyboard_buttons))
            else:
                await app.answer_callback_query(call.id, text="• هیچ کانالی ثبت نشده است •", show_alert=True)
    
    elif data.startswith("SelectChannel-"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            channel_id = data.split("-")[1]
            channel_data = get_data(f"SELECT * FROM channels WHERE id = '{channel_id}' LIMIT 1")
            if channel_data:
                channel_type_text = {
                    'main': 'اصلی',
                    'help': 'راهنما',
                    'api': 'API',
                    'extra': 'اضافی'
                }.get(channel_data['channel_type'], 'نامشخص')
                
                await app.edit_message_text(chat_id, m_id,
                                       f"**آیا مطمئن هستید که می‌خواهید کانال {channel_type_text} با آیدی @{get_channel_username(channel_data['channel_id'])} را حذف کنید؟**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmDeleteChannel-{channel_id}"),
                                            InlineKeyboardButton(text="خیر ✖️", callback_data="ManageChannels")]
                                       ]))
    
    elif data.startswith("ConfirmDeleteChannel-"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            channel_id = data.split("-")[1]
            channel_data = get_data(f"SELECT * FROM channels WHERE id = '{channel_id}' LIMIT 1")
            if channel_data:
                channel_username = get_channel_username(channel_data['channel_id'])
                delete_channel(channel_data['channel_id'])
                await app.edit_message_text(chat_id, m_id,
                                       f"**✔️ کانال @{channel_username} با موفقیت حذف شد.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                       ]))
    
    elif data == "ListChannels":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            channels = get_all_channels()
            if channels:
                channels_text = "**• لیست کانال ها :**\n\n"
                for channel in channels:
                    channel_type_text = {
                        'main': 'اصلی',
                        'help': 'راهنما',
                        'api': 'API',
                        'extra': 'اضافی'
                    }.get(channel['channel_type'], 'نامشخص')
                    
                    status = "فعال ✔️" if channel['is_active'] else "غیرفعال ✖️"
                    channels_text += f"**• نوع : ( {channel_type_text} )**\n"
                    channels_text += f"**• آیدی : ( @{get_channel_username(channel['channel_id'])} )**\n"
                    channels_text += f"**• اولویت : ( {channel['priority']} )**\n"
                    channels_text += f"**• وضعیت : ( {status}**\n"
                    channels_text += f"**• تاریخ ایجاد : ( {channel['created_at']} )**\n"
                    channels_text += "─" * 20 + "\n"
                
                await app.edit_message_text(chat_id, m_id, channels_text,
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                       ]))
            else:
                await app.edit_message_text(chat_id, m_id,
                                       "**هیچ کانالی ثبت نشده است.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                       ]))
    
    elif data == "check_membership":
        not_joined_channels = await check_all_channels_membership(chat_id)
    
        if not not_joined_channels:
            keyboard = get_main_keyboard(call.from_user.id)
            user_link = f'<a href="tg://user?id={call.from_user.id}">{html.escape(call.from_user.first_name)}</a>'
            start_message = get_setting("start_message").format(user_link=user_link)
        
            await app.edit_message_text(chat_id, m_id, start_message, reply_markup=keyboard)
        
            try:
                pass
            except:
                pass
            
            await app.answer_callback_query(call.id, text="• به ربات خوش آمدید •", show_alert=False)
        else:
            await app.answer_callback_query(call.id,
                                  text="• شما هنوز عضو کانال نشده اید •",
                                  show_alert=True)
    
    elif data == "PhoneRestriction":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
                current_status = get_setting("phone_restriction", "enabled")
                status_text = "فعال ✔️" if current_status == "enabled" else "غیرفعال ✖️"
        
                await app.edit_message_text(chat_id, m_id,
                    f"**• محدودیت شماره مجازی\n• وضعیت فعلی : ( {status_text} )\n\nدر صورت فعال بودن این بخش، فقط کاربران ایرانی میتوانند احراز هویت و سلف نصب کنند.**",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("فعال (✔️)", callback_data="EnablePhoneRestriction"),
                            InlineKeyboardButton("غیرفعال (✖️)", callback_data="DisablePhoneRestriction")
                        ],
                        [InlineKeyboardButton("(🔙) بازگشت", callback_data="AdminSettings")]
                    ]))

    elif data == "EnablePhoneRestriction":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            update_setting("phone_restriction", "enabled")
            await app.edit_message_text(chat_id, m_id,
                "**• قفل شماره مجازی قعال شد✔️**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("(🔙) بازگشت", callback_data="PhoneRestriction")]
                ]))

    elif data == "DisablePhoneRestriction":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            update_setting("phone_restriction", "disabled")
            await app.edit_message_text(chat_id, m_id,
                "**• قفل شماره مجازی غیرفعال شد✔️**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("(🔙) بازگشت", callback_data="PhoneRestriction")]
                ]))
    
    elif data == "SelfStatus":
        if expir > 0:
            user_folder = f"selfs/self-{chat_id}"
            if not os.path.isdir(user_folder):
                await app.edit_message_text(chat_id, m_id,
                    "**• ربات دستیار شما نصب نشده است، ابتدا ربات را نصب کرده و در صورت ایجاد مشکل به این بخش مراجعه کنید.**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="نصب سلف", callback_data="InstallSelf")],
                        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                    ]))
                return
            
            await app.edit_message_text(chat_id, m_id, 
                "**• درخواست شما به سرور ارسال شد، لطفا کمی صبر کنید.**")
            
            await asyncio.sleep(3.5)
            
            status_info = await check_self_status(chat_id)
            
            if status_info["status"] == "not_installed":
                await app.edit_message_text(chat_id, m_id,
                    "**• ربات دستیار شما نصب نشده است، ابتدا ربات را نصب کرده و در صورت ایجاد مشکل به این بخش مراجعه کنید.**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="نصب سلف", callback_data="InstallSelf")],
                        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                    ]))
                return
            elif status_info["status"] == "error":
                await app.edit_message_text(chat_id, m_id,
                    "**• خطا در بررسی وضعیت سلف.**\n\n"
                    f"{status_info['message']}\n\n"
                    "لطفا با پشتیبانی در ارتباط باشید یا مجدداً سلف را نصب کنید.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                    ]))
                return
            elif status_info["status"] == "inactive":
                await app.edit_message_text(chat_id, m_id,
                    "**• ربات دستیار شما نصب نشده است، ابتدا ربات را نصب کرده و در صورت ایجاد مشکل به این بخش مراجعه کنید.**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="نصب سلف", callback_data="InstallSelf")],
                        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                    ]))
                return
            else:
                status_message = (
                    f"**درخواست شما با موفقیت انجام شد.**\n\n"
                    f"**نتیجه:** {status_info['message']}\n\n"
                )
                
                if status_info["language"]:
                    status_message += f"**توجه: دستیار شما روی زبان {status_info['language']} تنظیم شده و فقط به دستورات با این زبان پاسخ خواهد داد.**"
                
                await app.edit_message_text(chat_id, m_id, status_message,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                    ]))
        else:
            await app.answer_callback_query(call.id, text="• شما انقضا ندارید •", show_alert=True)
    
    elif data == "ChangeLang":
        if expir > 0:
            can_change, remaining = can_change_language(chat_id)
            
            if not can_change:
                await app.edit_message_text(call.from_user.id, m_id, 
                    f"**• تغییر زبان دستیار شما تا {remaining} دقیقه دیگر امکان پذیر نیست.**")
                return
            
            current_lang = get_current_language(chat_id)
            
            next_lang = "en" if current_lang == "fa" else "fa"
            next_lang_display = "انگلیسی 🇬🇧" if next_lang == "en" else "فارسی 🇮🇷"
            current_lang_display = "فارسی 🇮🇷" if current_lang == "fa" else "انگلیسی 🇬🇧"
            
            await app.edit_message_text(chat_id, m_id,
                f"**• آیا میخواهید زبان دستیار شما از ( {current_lang_display} ) به ( {next_lang_display} ) تنظیم شود؟**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="بله ✔️", callback_data=f"ConfirmLangChange-{next_lang}"),
                     InlineKeyboardButton(text="خیر ✖️", callback_data="Back")]
                ]))
        else:
            await app.answer_callback_query(call.id, text="• شما انقضا ندارید •", show_alert=True)
    
    elif data.startswith("ConfirmLangChange-"):
        target_lang = data.split("-")[1]
        
        success, result = await change_self_language(chat_id, target_lang)
        
        if success:
            new_lang_display = "فارسی 🇮🇷" if target_lang == "fa" else "انگلیسی 🇬🇧"
            
            await app.edit_message_text(chat_id, m_id,
                f"**• زبان دستیار شما روی ( {new_lang_display} ) تنظیم شد.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                ]))
            
            user_data = get_data(f"SELECT pid FROM user WHERE id = '{chat_id}' LIMIT 1")
            pid = user_data.get("pid") if user_data else None
            
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    await asyncio.sleep(3)
                    
                    try:
                        os.kill(pid, 0)
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
                        
                except Exception as e:
                    pass
        else:
            await app.edit_message_text(chat_id, m_id,
                f"**• عملیات کنسل شد، با پشتیبانی در ارتباط باشید.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                ]))
    
    elif data == "AdminCreateCode":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                   "**لطفا تعداد روز انقضای کد را وارد کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
                                   ]))
            update_data(f"UPDATE user SET step = 'admin_create_code_days' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "AdminListCodes":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            cleanup_inactive_codes()
            
            codes = get_active_codes()
            
            if codes:
                codes_text = "**• لیست کدهای فعال :\n\n"
                for idx, code in enumerate(codes, 1):
                    codes_text += f"**{idx} - کد : ( `{code['code']}` )**\n"
                    codes_text += f"**• روزهای انقضا : ( {code['days']} روز )**\n"
                    codes_text += f"**• تاریخ ایجاد : ( {code['created_at']} )**\n\n"
                
                await app.edit_message_text(chat_id, m_id, codes_text,
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
                                       ]))
            else:
                await app.edit_message_text(chat_id, m_id,
                                       "**هیچ کد فعالی وجود ندارد.**",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
                                       ]))

    elif data == "AdminDeleteCode":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            codes = get_active_codes()
            
            if codes:
                keyboard_buttons = []
                for code in codes:
                    keyboard_buttons.append([
                        InlineKeyboardButton(text=f"• {code['code']}", callback_data=f"DeleteCode-{code['id']}")
                    ])
                keyboard_buttons.append([InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")])
                
                await app.edit_message_text(chat_id, m_id,
                                       "**لطفا کدی که می خواهید حذف کنید را انتخاب کنید:**",
                                       reply_markup=InlineKeyboardMarkup(keyboard_buttons))
            else:
                await app.answer_callback_query(call.id, text="• کد فعالی وجود ندارد •", show_alert=True)

    elif data.startswith("DeleteCode-"):
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            code_id = data.split("-")[1]
            delete_code(code_id)
            await app.edit_message_text(chat_id, m_id,
                                   "**کد با موفقیت حذف شد.**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="DeleteCode-")]
                                   ]))
    
    elif data == "BuyCode":
        await app.edit_message_text(chat_id, m_id,
                               "**• لطفا کد انقضای خریداری شده خود را ارسال کنید:**",
                               reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="Back")]
                               ]))
        update_data(f"UPDATE user SET step = 'use_code' WHERE id = '{call.from_user.id}' LIMIT 1")
        
    elif data == "AdminSettings":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id,
                                   "**مدیر گرامی، به بخش تنظیمات خوش آمدید.\nلطفا گزینه مورد نظر را انتخاب کنید:**",
                                   reply_markup=AdminSettingsKeyboard)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditStartMessage":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_message = get_setting("start_message")
            await app.edit_message_text(chat_id, m_id,
                                   f"**متن فعلی پیام استارت:**\n\n{current_message}\n\n**لطفا متن جدید را ارسال کنید:**\n\n**نکته:** برای نمایش نام کاربر میتوانید از `{{user_link}}` استفاده کنید.",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_start_message' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditPriceMessage":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_message = get_setting("price_message")
            await app.edit_message_text(chat_id, m_id,
                                   f"**متن فعلی پیام نرخ:**\n\n{current_message}\n\n**لطفا متن جدید را ارسال کنید:**\n\n**نکته:** برای نمایش قیمت‌ها میتوانید از متغیرهای زیر استفاده کنید:\n- `{{price_1month}}`\n- `{{price_2month}}`\n- `{{price_3month}}`\n- `{{price_4month}}`\n- `{{price_5month}}`\n- `{{price_6month}}`",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_price_message' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditSelfMessage":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_message = get_setting("whatself_message")
            await app.edit_message_text(chat_id, m_id,
                                   f"**متن فعلی توضیح سلف:**\n\n{current_message}\n\n**لطفا متن جدید را ارسال کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_self_message' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditPrices":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            f"**لطفا نرخ موردنظر خودتون رو به صورت زیر وارد کنید.\n( به صورت خط به خط ، خط اول نزخ یک ماهه، خط دوم نرخ دو ماهه و به همین صورت تا نرخ 6 ماهه )\n\n100000\n200000\n300000\n400000\n500000\n600000**"
    
            await app.edit_message_text(chat_id, m_id, prices_text,
                               reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                               ]))
            update_data(f"UPDATE user SET step = 'edit_all_prices' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditCardInfo":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_card = get_setting("card_number")
            current_name = get_setting("card_name")
        
            await app.edit_message_text(chat_id, m_id,
                                   f"**اطلاعات فعلی کارت:**\n\n**شماره کارت:** `{current_card}`\n**نام صاحب کارت:** {current_name}\n\n**لطفا گزینه مورد نظر را انتخاب کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="تغییر شماره کارت", callback_data="EditCardNumber")],
                                       [InlineKeyboardButton(text="تغییر نام صاحب کارت", callback_data="EditCardName")],
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                   ]))

    elif data == "EditCardNumber":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_card = get_setting("card_number")
            await app.edit_message_text(chat_id, m_id,
                                   f"**شماره کارت فعلی:** `{current_card}`\n\n**لطفا شماره کارت جدید را وارد کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="EditCardInfo")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_card_number' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "EditCardName":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            current_name = get_setting("card_name")
            await app.edit_message_text(chat_id, m_id,
                                   f"**نام صاحب کارت فعلی:** {current_name}\n\n**لطفا نام جدید را وارد کنید:**",
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="EditCardInfo")]
                                   ]))
            update_data(f"UPDATE user SET step = 'edit_card_name' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "ViewSettings":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            settings = get_all_settings()
            settings_text = "**تنظیمات فعلی ربات:**\n\n"
            for setting in settings:
                key = setting[1]
                value = setting[2][:50] + "..." if len(str(setting[2])) > 50 else setting[2]
                desc = setting[3]
                settings_text += f"**{desc}:**\n`{key}` = `{value}`\n\n"
        
            await app.edit_message_text(chat_id, m_id, settings_text,
                                   reply_markup=InlineKeyboardMarkup([
                                       [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                   ]))
    
    elif data == "InstallSelf":
        if expir > 0:
                user_info = get_data(f"SELECT phone, api_id, api_hash FROM user WHERE id = '{chat_id}' LIMIT 1")
        
                if user_info and user_info["phone"] and user_info["api_id"] and user_info["api_hash"]:
                    
                    api_hash = user_info["api_hash"]
                    if len(api_hash) >= 8:
                        masked_hash = f"{api_hash[:4]}{'*' * (len(api_hash)-8)}{api_hash[-4:]}"
                    else:
                        masked_hash = "****"
                    await app.edit_message_text(chat_id, m_id,
                        f"**📞 Number : `{user_info['phone']}`\n🆔 Api ID : `{user_info['api_id']}`\n🆔 Api Hash : `{masked_hash}`\n\n• آیا اطلاعات را تایید میکنید؟**",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("بله (✅)", callback_data="ConfirmInstall"),
                            InlineKeyboardButton("خیر (❎)", callback_data="ChangeInfo")],
                            [InlineKeyboardButton("(🔙) بازگشت", callback_data="Back")]
                        ]))
                else:
                    await app.edit_message_text(chat_id, m_id,
                        "**برای نصب سلف، لطفا شماره تلفن خود را با دکمه زیر به اشتراک بگذارید:**",
                        reply_markup=ReplyKeyboardMarkup(
                            [[KeyboardButton(text="اشتراک گذاری شماره", request_contact=True)]],
                            resize_keyboard=True
                        ))
                    update_data(f"UPDATE user SET step = 'install_phone' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat.id, "**شما انقضا ندارید.**")
    
    elif data == "ConfirmInstall":
        user_info = get_data(f"SELECT phone, api_id, api_hash FROM user WHERE id = '{chat_id}' LIMIT 1")
        if user_info and user_info["phone"] and user_info["api_id"] and user_info["api_hash"]:
            await app.edit_message_text(chat_id, m_id,
                "**• زبان سلف را انتخاب کنید.**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("فارسی 🇮🇷", callback_data=f"SelectLanguage-fa"),
                    InlineKeyboardButton("English 🇬🇧", callback_data=f"SelectLanguage-en")],
                    [InlineKeyboardButton("(🔙) بازگشت", callback_data="Back")]
                ]))
            update_data(f"UPDATE user SET step = 'select_language-{user_info['phone']}-{user_info['api_id']}-{user_info['api_hash']}' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.answer_callback_query(call.id, text="• اطلاعات شما ناقص است •", show_alert=True)

    elif data.startswith("SelectLanguage-"):
        target_language = data.split("-")[1]
        user_step = user["step"]
    
        if user_step.startswith("select_language-"):
            parts = user_step.split("-", 1)
            if len(parts) > 1:
                remaining_parts = parts[1]
                update_data(f"UPDATE user SET step = 'install_with_language-{remaining_parts}-{target_language}' WHERE id = '{chat_id}' LIMIT 1")
            
                remaining_parts_parts = remaining_parts.split("-")
                if len(remaining_parts_parts) >= 3:
                    phone = remaining_parts_parts[0]
                    api_id = remaining_parts_parts[1]
                    api_hash = remaining_parts_parts[2]
                
                    await app.edit_message_text(chat_id, m_id, "**• درحال ساخت سلف، لطفا صبور باشید.**")
                
                    await start_self_installation(chat_id, phone, api_id, api_hash, m_id, target_language)

    elif data == "ChangeInfo":
        await app.edit_message_text(chat_id, m_id,
            "**لطفا شماره تلفن خود را با دکمه زیر به اشتراک بگذارید:**",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(text="اشتراک گذاری شماره", request_contact=True)]],
                resize_keyboard=True
            ))
        update_data(f"UPDATE user SET step = 'install_phone' WHERE id = '{chat_id}' LIMIT 1")

    elif data == "StartInstallation":
        user_info = get_data(f"SELECT phone, api_id, api_hash FROM user WHERE id = '{chat_id}' LIMIT 1")
        if user_info and user_info["phone"] and user_info["api_id"] and user_info["api_hash"]:
            await app.edit_message_text(chat_id, m_id, "**• درحال ساخت سلف، لطفا صبور باشید.**")
            await start_self_installation(chat_id, user_info["phone"], user_info["api_id"], user_info["api_hash"])
        else:
            await app.answer_callback_query(call.id, text="• اطلاعات شما ناقص است •", show_alert=True)
    
    elif data == "ExpiryStatus":
        await app.answer_callback_query(call.id, text=f"انقضای شما : ( {expir} روز )", show_alert=True)

    elif data == "AdminPanel":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**مدیر گرامی، به پنل ربات سلف ساز تلگرام خوش آمدید.\nاکنون ربات کاملا در اختیار شماست، در صورتی که آشنایی با پنل مدیریت یا کارکرد ربات ندارید، بخش « راهنما » را بخوانید.**", reply_markup=AdminPanelKeyboard)
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            async with lock:
                if chat_id in temp_Client:
                    del temp_Client[chat_id]
        else:
            await app.answer_callback_query(call.id, text="**شما دسترسی به بخش مدیریت ندارید.**", show_alert=True)
    
    elif data == "AdminStats":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            botinfo = await app.get_me()
            allusers = get_datas("SELECT COUNT(id) FROM user")[0][0]
            allblocks = get_datas("SELECT COUNT(id) FROM block")[0][0]
            pending_cards = len(get_pending_cards())
            
            await app.edit_message_text(chat_id, m_id, f"""
            • تعداد کل کاربران ربات : **[ {allusers} ]**
            • تعداد کاربران بلاک شده :  **[ {allblocks} ]**
            • تعداد کارت های در انتضار تایید : **[ {pending_cards} ]**
            
            • نام ربات : **( {botinfo.first_name} )**
            • آیدی عددی ربات : **( `{botinfo.id}` )**
            • آیدی ربات : **( @{botinfo.username} )**
            """, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
    
    elif data == "AdminBroadcast":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, f"**پیام خود را جهت ارسال همگانی، ارسال کنید.**\n\n• با ارسال پیام در این بخش، پیام شما برای تمامی کاربران ربات **ارسال** میشود.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_broadcast' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminForward":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, f"**پیام خود را جهت فوروارد همگانی ارسال کنید.**\n\n• با ارسال پیام در این بخش، پیام شما برای تمامی کاربران ربات **فوروارد** میشود.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_forward' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminBlock":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**آیدی عددی کاربر را جهت مسدود از ربات ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_block' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminUnblock":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**آیدی عددی کاربر را جهت پاک کردن از لیست مسدود ها ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_unblock' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminAddExpiry":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**• آیدی عددی کاربر را جهت افزایش انقضا ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_add_expiry1' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminDeductExpiry":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**• آیدی عددی کاربر را جهت کسر انقضا ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_deduct_expiry1' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminActivateSelf":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**آیدی عددی کاربر را جهت فعالسازی سلف ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_activate_self' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminDeactivateSelf":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            await app.edit_message_text(chat_id, m_id, "**آیدی عددی کاربر را جهت غیرفعال سازی سلف ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'admin_deactivate_self' WHERE id = '{chat_id}' LIMIT 1")
    
    elif data == "AdminTurnOn":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            bot = get_data("SELECT * FROM bot")
            if bot["status"] != "ON":
                await app.edit_message_text(chat_id, m_id, "**• ربات روشن شد.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
                update_data(f"UPDATE bot SET status = 'ON' LIMIT 1")
            else:
                await app.answer_callback_query(call.id, text="**• ربات روشن بوده است.**", show_alert=True)
    
    elif data == "AdminTurnOff":
        if call.from_user.id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{call.from_user.id}' LIMIT 1") is not None:
            bot = get_data("SELECT * FROM bot")
            if bot["status"] != "OFF":
                await app.edit_message_text(chat_id, m_id, "**• ربات خاموش شد.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
                update_data(f"UPDATE bot SET status = 'OFF' LIMIT 1")
            else:
                await app.answer_callback_query(call.id, text="**• ربات خاموش بوده است.**", show_alert=True)
    
    elif data.startswith("AdminVerifyCard-"):
        params = data.split("-")
        user_id = int(params[1])
        card_number = params[2]
    
        bank_name = detect_bank(card_number)
        card = get_card_by_number(user_id, card_number)
    
        if card:
            update_card_status(card["id"], "verified", bank_name)
    
        user_info = await app.get_users(user_id)
        username = f"@{user_info.username}" if user_info.username else "ندارد"
    
        await app.edit_message_text(call.message.chat.id, call.message.id, f"""**• درخواست احراز هویت از طرف ( {html.escape(user_info.first_name)} - {username} - {user_id} )
• شماره کارت : [ {card_number} ]

به دستور ( {call.from_user.id} ) تایید شد.**""")
    
        await app.send_message(user_id, f"**• درخواست احراز هویت کارت ( `{card_number}` ) تایید شد.\nشما هم اکنون میتوانید از بخش خرید / تمدید اشتراک ، خرید خود را انجام دهید.**")

    elif data.startswith("AdminRejectCard-"):
        params = data.split("-")
        user_id = int(params[1])
        card_number = params[2]
    
        card = get_card_by_number(user_id, card_number)
        if card:
            update_card_status(card["id"], "rejected")
        user_info = await app.get_users(user_id)
        username = f"@{user_info.username}" if user_info.username else "ندارد"
    
        await app.edit_message_text(call.message.chat.id, call.message.id, f"""**• درخواست احراز هویت از طرف ( {html.escape(user_info.first_name)} - {username} - {user_id} )
• شماره کارت : [ {card_number} ]

به دستور ( {call.from_user.id} ) رد شد.**""")
    
        await app.send_message(user_id, f"**• درخواست احراز هویت کارت ( {card_number} ) به دلیل اشتباه بودن، رد شد.\nشما میتوانید مجددا برای احراز هویت با رعایت شرایط، درخواست دهید.**")

    elif data.startswith("AdminIncompleteCard-"):
        params = data.split("-")
        user_id = int(params[1])
        card_number = params[2]
    
        card = get_card_by_number(user_id, card_number)
        if card:
            update_card_status(card["id"], "rejected")
        user_info = await app.get_users(user_id)
        username = f"@{user_info.username}" if user_info.username else "ندارد"
    
        await app.edit_message_text(call.message.chat.id, call.message.id, f"""**• درخواست احراز هویت از طرف ( {html.escape(user_info.first_name)} - {username} - {user_id} )
• شماره کارت : [ {card_number} ]

به دستور ( {call.from_user.id} ) رد شد.**""")
    
        await app.send_message(user_id, f"**• درخواست احراز هویت کارت ( {card_number} ) به دلیل ناقص بودن ، رد شد.\nشما میتوانید مجددا برای احراز هویت با رعایت شرایط، درخواست دهید.**")
    
    elif data.startswith("AdminApprovePayment-"):
        params = data.split("-")
        user_id = int(params[1])
        expir_count = int(params[2])
        cost = params[3]
        transaction_id = params[4]
        
        user_data = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
        old_expir = user_data["expir"] if user_data else 0
        new_expir = old_expir + expir_count
        
        update_data(f"UPDATE user SET expir = '{new_expir}' WHERE id = '{user_id}' LIMIT 1")
        
        if expir_count == 31:
            month_text = "یک ماه"
        elif expir_count == 62:
            month_text = "دو ماه"
        elif expir_count == 93:
            month_text = "سه ماه"
        elif expir_count == 124:
            month_text = "چهار ماه"
        elif expir_count == 155:
            month_text = "پنج ماه"
        elif expir_count == 186:
            month_text = "شش ماه"
        else:
            month_text = f"{expir_count} روز"
        
        await app.edit_message_text(Admin, m_id, f"**پرداخت کاربر [ `{user_id}` ] تایید شد.\n\n• شناسه تراکنش : [ `{transaction_id}` ]\n• انقضای جدید کاربر : [ `{new_expir} روز` ]**")
        
        await app.send_message(user_id, f"**پرداخت شما تایید شد.\n\n• شناسه تراکنش : [ {transaction_id} ]\n• انقضای سلف شما {month_text} اضافه گردید.\n\nانقضای قبلی شما : ( `{old_expir}` ) روز\n\n• انقضای جدید : ( `{new_expir}` ) روز**")
    
    elif data.startswith("AdminRejectPayment-"):
        params = data.split("-")
        user_id = int(params[1])
        transaction_id = params[2]
        
        await app.edit_message_text(Admin, m_id,f"**• پرداخت کاربر [ `{user_id}` ] رد شد.**")
        
        await app.edit_message_text(user_id, f"**پرداخت شما رد گردید.\n\n•شناسه تراکنش : [ `{transaction_id}` ]\n• افزایش انقضای شما به دلیل ارسال فیش واربزی اشتباه رد شده و درخواست شما لغو گردید.\n• در صورتی که غکر میکنید اشتباه شده است، شناسه تراکنش را به پشتیبانی ارسال کرده و با پشتیان ها در ارتباط باشید.**")
    
    elif data.startswith("AdminBlockPayment-"):
        user_id = int(data.split("-")[1])
        
        update_data(f"INSERT INTO block(id) VALUES({user_id})")
        
        await app.edit_message_text(Admin, m_id, f"**• کاربر [ `{user_id}` ] از ربات مسدود شد.**")
        
        await app.send_message(user_id, f"**شما به دلیل نقض قوانین از ربات مسدود شده اید.\n• با پشتیبان ها در ارتباط باشید.**")
    
    elif data.startswith("Reply-"):
        user_id = int(data.split("-")[1])
        user_info = await app.get_users(user_id)
        await app.edit_message_text(
            Admin,
            m_id,
            f"**• پیام خود را جهت پاسخ به کاربر [ {html.escape(user_info.first_name)} ] ارسال کنید:**",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            )
        )
        update_data(f"UPDATE user SET step = 'ureply-{user_id}' WHERE id = '{Admin}' LIMIT 1")

    elif data.startswith("Block-"):
        user_id = int(data.split("-")[1])
        user_info = await app.get_users(user_id)
        block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
        if block is None:
            await app.send_message(user_id, "**شما به دلیل نقض قوانین از ربات مسدود شدید.**")
            await app.send_message(Admin, f"**• کاربر [ {html.escape(user_info.first_name)} ] از ربات مسدود شد.**")
            update_data(f"INSERT INTO block(id) VALUES({user_id})")
        else:
            await app.send_message(Admin, f"**• کاربر [ {html.escape(user_info.first_name)} ] از قبل بلاک بوده است.**")

    elif data == "Back":
        keyboard = get_main_keyboard(call.from_user.id)
        await app.edit_message_text(chat_id, m_id, "**‌ ‌ ‌ ‌ ‌ ‌ ‌     ‌ ‌‌‌  ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌‌‌‌‌‌ \nبه منوی اصلی بازگشتید.\n\nلطفا اگر سوالی دارید از بخش پشتیبانی ، با پستیبان ها در ارتباط باشید.\n\n‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ ‌ لطفا انتخاب کنید:\n‌ ‌ ‌‌        ‌‌‌‌‌‌    ‌‌‌‌‌‌ ‌‌‌‌‌**", reply_markup=keyboard)
        await app.answer_callback_query(call.id, text="• به منوی اصلی بازگشتید •", show_alert=False)
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{call.from_user.id}' LIMIT 1")
        async with lock:
            if chat_id in temp_Client:
                del temp_Client[chat_id]
    
    elif data == "text":
        await app.answer_callback_query(call.id, text="• دکمه نمایشی است •", show_alert=True)


@app.on_message(filters.contact)
@checker
async def contact_handler(c, m):
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    
    phone_number = str(m.contact.phone_number)
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"
    
    is_valid, error_message = validate_phone_number(phone_number)
    
    if not is_valid:
        await app.send_message(m.chat.id, f"**• تا اطلاع ثانوی، امکان خرید، نصب دستیار با شماره های خارج از ایران غیرمجاز میباشد.**.")
        return
    
    contact_id = m.contact.user_id
    
    if user["step"] == "install_phone":
        if m.contact and m.chat.id == contact_id:
            update_data(f"UPDATE user SET phone = '{phone_number}' WHERE id = '{m.chat.id}' LIMIT 1")
            Create = f'<a href=https://t.me/{api_channel}>کلیک کنید!</a>'
            await app.send_message(m.chat.id, "**شماره شما ثبت شد.**")
            
            await app.send_message(m.chat.id, f"**• لطفا `Api ID` خود را وارد کنید. ( نمونه : 123456 )**\n• آموزش ساخت : ( {Create} )\n\n**• لغو عملیات [ /start ]**")
            
            update_data(f"UPDATE user SET step = 'install_api_id' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(m.chat.id, "**• لطفا شماره خود را با دکمه «اشتراک گذاری شماره» ارسال کنید.**")
        return
    
    elif user["step"] == "contact":
        if m.contact and m.chat.id == contact_id:
            await app.send_message(m.chat.id, 
                                 "**• شماره شما با موفقیت ذخیره شد.\nاکنون می‌توانید از بخش خرید استفاده کنید.\n\nربات رو مجددا [ /start ] کنید.**", 
                                 reply_markup=ReplyKeyboardRemove())
            update_data(f"UPDATE user SET phone = '{phone_number}' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(m.chat.id, "**• با استفاده از دکمه « اشتراک گذاری شماره » شماره تلفن را ارسال نمایید.**")


@app.on_message(filters.private)
@checker
async def message_handler(c, m):
    global temp_Client
    user = get_data(f"SELECT * FROM user WHERE id = '{m.chat.id}' LIMIT 1")
    username = f"@{m.from_user.username}" if m.from_user.username else "وجود ندارد"
    expir = user["expir"] if user else 0
    chat_id = m.chat.id
    text = m.text
    m_id = m.id

    if user["step"] == "card_photo":
        if m.photo:
            photo_path = await m.download(file_name=f"cards/{chat_id}_{int(time.time())}.jpg")
            update_data(f"UPDATE user SET step = 'card_number-{photo_path}-{m_id}' WHERE id = '{m.chat.id}' LIMIT 1")
            
            await app.send_message(chat_id,
                                 "**• لطفا شماره کارت خود را به صورت اعداد انگلیسی ارسال کنید.\nدر صورتی که منصرف شدید ربات را مجدد [ /start ] کنید.**")
        else:
            await app.send_message(chat_id, "**• فقط ارسال عکس مجاز است.**")

    elif user["step"].startswith("card_number-"):
        if text and text.isdigit() and len(text) == 16:
            parts = user["step"].split("-", 2)
            photo_path = parts[1]
            photo_message_id = parts[2] if len(parts) > 2 else None
        
            card_number = text.strip()
    
            add_card(chat_id, card_number)
    
            if photo_message_id:
                try:
                    forwarded_photo_msg = await app.forward_messages(
                        from_chat_id=chat_id,
                        chat_id=Admin,
                        message_ids=int(photo_message_id)
                    )
                
                    await app.send_message(
                        Admin,
                        f"""**• درخواست احراز هویت از طرف ( {html.escape(m.chat.first_name)} - @{m.from_user.username if m.from_user.username else 'ندارد'} - {m.chat.id} )
شماره کارت : [ {card_number} ]**""",
                        reply_to_message_id=forwarded_photo_msg.id,
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(text="تایید (✅)", callback_data=f"AdminVerifyCard-{chat_id}-{card_number}")
                            ],
                            [
                                InlineKeyboardButton(text="اشتباه (❌)", callback_data=f"AdminRejectCard-{chat_id}-{card_number}"),
                                InlineKeyboardButton(text="کامل نیست (❌)", callback_data=f"AdminIncompleteCard-{chat_id}-{card_number}")
                            ]
                        ])
                    )
                except Exception as e:
                    await app.send_message(
                        Admin,
                        f"""**• درخواست احراز هویت از طرف ({html.escape(m.chat.first_name)} - @{m.from_user.username if m.from_user.username else 'ندارد'} - {m.chat.id})
شماره کارت : [ {card_number} ]**""",
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(text="تایید (✅)", callback_data=f"AdminVerifyCard-{chat_id}-{card_number}"),
                                InlineKeyboardButton(text="اشتباه (❌)", callback_data=f"AdminRejectCard-{chat_id}-{card_number}"),
                                InlineKeyboardButton(text="کامل نیست (❌)", callback_data=f"AdminIncompleteCard-{chat_id}-{card_number}")
                            ]
                        ])
                    )
            else:
                await app.send_message(
                    Admin,
                    f"""**• درخواست احراز هویت از طرف ({html.escape(m.chat.first_name)} - @{m.from_user.username if m.from_user.username else 'ندارد'} - {m.chat.id})
شماره کارت : [ {card_number} ]**""",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(text="تایید (✅)", callback_data=f"AdminVerifyCard-{chat_id}-{card_number}"),
                            InlineKeyboardButton(text="اشتباه (❌)", callback_data=f"AdminRejectCard-{chat_id}-{card_number}"),
                            InlineKeyboardButton(text="کامل نیست (❌)", callback_data=f"AdminIncompleteCard-{chat_id}-{card_number}")
                        ]
                    ])
                )
    
            await app.send_message(chat_id,
                            """**• درخواست احراز هویت شما برای پشتیبانی ارسال شد و در اولین فرصت تایید خواهد شد ، لطفا صبور باشید.

لطفا برای تایید کارت به پشتیبانی پیام ارسال نفرمایید و درخواست احرازهویتتون رو اسپم نکنید ، در صورت مشاهده این کار یک روز با تاخیر تایید میشود.**""")
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**شماره کارت باید 16 رقم باشد.\n• در صورتی که منصرف شدید ربات رو مجددا [ /start ] کنید.**")

    elif user["step"].startswith("payment_receipt-"):
        if m.photo:
            params = user["step"].split("-")
            expir_count = params[1]
            cost = params[2]
            card_id = params[3]
            
            card = get_card_by_id(card_id)
            card_number = card["card_number"] if card else "نامشخص"
            
            mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
            
            transaction_id = str(int(time.time()))[-11:]
            
            await app.send_message(Admin,
                                 f"""**• درخواست خرید اشتراک از طرف ( {html.escape(m.chat.first_name)} - @{m.from_user.username if m.from_user.username else 'ندارد'} - {m.chat.id} )
اشتراک انتخاب شده : ( `{cost} تومان - {expir_count} روز` )
کارت خرید : ( `{card_number}` )**""",
                                 reply_to_message_id=mess.id,
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="تایید (✅)", callback_data=f"AdminApprovePayment-{chat_id}-{expir_count}-{cost}-{transaction_id}")],
                                      [InlineKeyboardButton(text="مسدود (❌)", callback_data=f"AdminBlockPayment-{chat_id}"),
                                      InlineKeyboardButton(text="رد (❌)", callback_data=f"AdminRejectPayment-{chat_id}-{transaction_id}")]
                                 ]))
            
            await app.send_message(chat_id,
                                 f"""**فیش واریزی شما ارسال شد.
• شناسه تراکنش: [ `{transaction_id}` ]
منتظر تایید فیش توسط مدیر باشید.**""")
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{m.chat.id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**فقط عکس فیش واریزی را ارسال کنید.**")

    elif user["step"] == "support":
        mess = await app.forward_messages(from_chat_id=chat_id, chat_id=Admin, message_ids=m_id)
        await app.send_message(Admin, f"""**
• پیام جدید از طرف ( {html.escape(m.chat.first_name)} - `{m.chat.id}` - {username} )**\n
""", reply_to_message_id=mess.id, reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("پاسخ (✅)", callback_data=f"Reply-{m.chat.id}"),
                InlineKeyboardButton("مسدود (❌)", callback_data=f"Block-{m.chat.id}")
            ]
        ]
    ))
        await app.send_message(chat_id, "**• پیام شما به پشتیبانی ارسال شد.\nلطفا در بخش پشتیبانی اسپم نکنید و از دستورات استفاده نکنید به پیام شما در اسرع وقت پاسخ داده خواهد شد.**", reply_to_message_id=m_id)
    
    # ==================== Sales Admin Steps ==================== #
    
    elif user["step"] == "add_admin":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text and text.isdigit():
                new_admin_id = int(text.strip())
                
                # بررسی اینکه کاربر وجود دارد
                user_check = get_data(f"SELECT * FROM user WHERE id = '{new_admin_id}' LIMIT 1")
                if not user_check:
                    await app.send_message(chat_id,
                                         "**کاربر یافت نشد.**\n"
                                         "**لطفا ابتدا کاربر ربات را استارت کند.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                         ]))
                    return
                
                # اضافه کردن به لیست ادمین‌ها
                add_admin_role(new_admin_id, "sales")
                add_admin(new_admin_id)
                
                try:
                    user_info = await app.get_users(new_admin_id)
                    name = html.escape(user_info.first_name or "نامشخص")
                    username = f"@{user_info.username}" if user_info.username else "ندارد"
                    
                    await app.send_message(chat_id,
                                         f"**✅ کاربر {name} ({username}) با آیدی `{new_admin_id}` به ادمین‌ها اضافه شد.**\n\n"
                                         f"**لطفا دسترسی‌های این ادمین را تنظیم کنید.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="تنظیم دسترسی", callback_data="SetAdminPermissions")],
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                         ]))
                except:
                    await app.send_message(chat_id,
                                         f"**✅ کاربر با آیدی `{new_admin_id}` به ادمین‌ها اضافه شد.**\n\n"
                                         f"**لطفا دسترسی‌های این ادمین را تنظیم کنید.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="تنظیم دسترسی", callback_data="SetAdminPermissions")],
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                         ]))
                
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")

    elif user["step"].startswith("set_"):
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text and text.isdigit():
                admin_id = int(text.strip())
                step_type = user["step"]
                
                # تعیین دسترسی‌ها بر اساس نوع
                if "sales" in step_type:
                    set_admin_permissions(admin_id, can_sell=True, can_manage=False, can_transactions=False, can_support=False)
                    role_text = "فروش"
                elif "full" in step_type:
                    set_admin_permissions(admin_id, can_sell=True, can_manage=True, can_transactions=True, can_support=True)
                    role_text = "مدیریت کامل"
                elif "transactions" in step_type:
                    set_admin_permissions(admin_id, can_sell=False, can_manage=False, can_transactions=True, can_support=False)
                    role_text = "مدیریت تراکنش‌ها"
                elif "support" in step_type:
                    set_admin_permissions(admin_id, can_sell=False, can_manage=False, can_transactions=False, can_support=True)
                    role_text = "پشتیبانی"
                else:
                    role_text = "عمومی"
                
                try:
                    user_info = await app.get_users(admin_id)
                    name = html.escape(user_info.first_name or "نامشخص")
                    username = f"@{user_info.username}" if user_info.username else "ندارد"
                    
                    await app.send_message(chat_id,
                                         f"**✅ دسترسی {role_text} برای ادمین {name} ({username}) تنظیم شد.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                         ]))
                except:
                    await app.send_message(chat_id,
                                         f"**✅ دسترسی {role_text} برای ادمین با آیدی `{admin_id}` تنظیم شد.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminManagement")]
                                         ]))
                
                # اطلاع به ادمین
                await app.send_message(admin_id,
                                     f"**🎉 شما به عنوان ادمین {role_text} ربات تنظیم شدید!**\n\n"
                                     f"**دسترسی‌های شما:**\n"
                                     f"• {role_text}\n\n"
                                     f"**لطفا ربات را مجدد استارت کنید.**")
                
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")
    
    elif user["step"] == "sales_select_customer":
        if text and text.isdigit():
            customer_id = int(text.strip())
            
            # بررسی اینکه مشتری قبلاً به ادمین دیگری تعلق ندارد
            existing_assignment = check_customer_assigned(customer_id)
            if existing_assignment:
                if existing_assignment['admin_id'] == chat_id:
                    await app.send_message(chat_id, 
                                         f"**این مشتری قبلاً به شما تعلق دارد.**\n\n"
                                         f"**لطفا نوع اشتراک را انتخاب کنید:**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                         ]))
                else:
                    await app.send_message(chat_id,
                                         f"**این مشتری قبلاً به ادمین دیگری تعلق دارد.**",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                         ]))
                return
            
            # دریافت قیمت‌های ادمین فروش
            sales_prices = get_sales_admin_prices(chat_id)
            
            await app.send_message(chat_id,
                                 f"**قیمت‌های شما برای مشتری:**\n\n"
                                 f"**1. 1 ماهه:** `{sales_prices['price_1month']:,}` تومان\n"
                                 f"**2. 2 ماهه:** `{sales_prices['price_2month']:,}` تومان\n"
                                 f"**3. 3 ماهه:** `{sales_prices['price_3month']:,}` تومان\n"
                                 f"**4. 4 ماهه:** `{sales_prices['price_4month']:,}` تومان\n"
                                 f"**5. 5 ماهه:** `{sales_prices['price_5month']:,}` تومان\n"
                                 f"**6. 6 ماهه:** `{sales_prices['price_6month']:,}` تومان\n\n"
                                 f"**لطفا نوع اشتراک را انتخاب کنید:**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="1 ماهه", callback_data=f"SalesSub-30-{sales_prices['price_1month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="2 ماهه", callback_data=f"SalesSub-60-{sales_prices['price_2month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="3 ماهه", callback_data=f"SalesSub-90-{sales_prices['price_3month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="4 ماهه", callback_data=f"SalesSub-120-{sales_prices['price_4month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="5 ماهه", callback_data=f"SalesSub-150-{sales_prices['price_5month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="6 ماهه", callback_data=f"SalesSub-180-{sales_prices['price_6month']}-{customer_id}")],
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                 ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")

    elif user["step"] == "sales_customer_status":
        if text and text.isdigit():
            customer_id = int(text.strip())
            
            # بررسی اینکه مشتری متعلق به این ادمین است
            customer_check = check_customer_assigned(customer_id)
            if not customer_check or customer_check['admin_id'] != chat_id:
                await app.send_message(chat_id,
                                     f"**این مشتری متعلق به شما نیست یا وجود ندارد.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            # بررسی وضعیت سلف
            status_info = await check_self_status(customer_id)
            
            try:
                user_info = await app.get_users(customer_id)
                name = html.escape(user_info.first_name or "نامشخص")
                username = f"@{user_info.username}" if user_info.username else "ندارد"
            except:
                name = "نامشخص"
                username = "ندارد"
            
            status_message = f"**وضعیت سلف مشتری:**\n\n"
            status_message += f"**نام:** {name}\n"
            status_message += f"**آیدی:** `{customer_id}`\n"
            status_message += f"**یوزرنیم:** {username}\n"
            status_message += f"**وضعیت:** {status_info['message']}\n"
            
            if status_info['language']:
                status_message += f"**زبان:** {status_info['language']}\n"
            
            await app.send_message(chat_id, status_message,
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                 ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")

    elif user["step"] == "sales_change_lang":
        if text and text.isdigit():
            customer_id = int(text.strip())
            
            # بررسی اینکه مشتری متعلق به این ادمین است
            customer_check = check_customer_assigned(customer_id)
            if not customer_check or customer_check['admin_id'] != chat_id:
                await app.send_message(chat_id,
                                     f"**این مشتری متعلق به شما نیست یا وجود ندارد.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            # بررسی امکان تغییر زبان
            can_change, remaining = can_change_language(customer_id)
            
            if not can_change:
                await app.send_message(chat_id,
                                     f"**تغییر زبان برای این مشتری تا {remaining} دقیقه دیگر امکان‌پذیر نیست.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            current_lang = get_current_language(customer_id)
            next_lang = "en" if current_lang == "fa" else "fa"
            next_lang_display = "انگلیسی 🇬🇧" if next_lang == "en" else "فارسی 🇮🇷"
            current_lang_display = "فارسی 🇮🇷" if current_lang == "fa" else "انگلیسی 🇬🇧"
            
            await app.send_message(chat_id,
                                 f"**آیا می‌خواهید زبان سلف مشتری از {current_lang_display} به {next_lang_display} تغییر کند؟**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="بله ✔️", callback_data=f"SalesConfirmLang-{customer_id}-{next_lang}"),
                                      InlineKeyboardButton(text="خیر ✖️", callback_data="SalesAdminPanel")]
                                 ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")

    elif user["step"] == "sales_install_self":
        if text and text.isdigit():
            customer_id = int(text.strip())
            
            # بررسی اینکه مشتری متعلق به این ادمین است
            customer_check = check_customer_assigned(customer_id)
            if not customer_check or customer_check['admin_id'] != chat_id:
                await app.send_message(chat_id,
                                     f"**این مشتری متعلق به شما نیست یا وجود ندارد.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            # بررسی انقضای مشتری
            customer_data = get_data(f"SELECT expir FROM user WHERE id = '{customer_id}' LIMIT 1")
            if not customer_data or customer_data['expir'] <= 0:
                await app.send_message(chat_id,
                                     f"**این مشتری انقضا ندارد.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            try:
                user_info = await app.get_users(customer_id)
                name = html.escape(user_info.first_name or "نامشخص")
            except:
                name = "مشتری"
            
            await app.send_message(chat_id,
                                 f"**آیا می‌خواهید سلف برای {name} (آیدی: {customer_id}) نصب شود؟**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="بله ✔️", callback_data=f"SalesConfirmInstall-{customer_id}"),
                                      InlineKeyboardButton(text="خیر ✖️", callback_data="SalesAdminPanel")]
                                 ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**لطفا آیدی عددی معتبر ارسال کنید.**")

    elif user["step"] == "sales_add_balance":
        if text and text.isdigit():
            amount = int(text.strip())
            
            if amount < 10000:
                await app.send_message(chat_id,
                                     f"**حداقل مبلغ افزایش موجودی 10,000 تومان است.**",
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                     ]))
                return
            
            # ایجاد درخواست برای مالک
            transaction_id = str(int(time.time()))[-11:]
            
            await app.send_message(Admin,
                                 f"**درخواست افزایش موجودی از ادمین فروش:**\n\n"
                                 f"**آیدی ادمین:** `{chat_id}`\n"
                                 f"**نام:** {html.escape(call.from_user.first_name)}\n"
                                 f"**مبلغ درخواستی:** `{amount:,}` تومان\n"
                                 f"**شناسه تراکنش:** `{transaction_id}`\n\n"
                                 f"**لطفا پس از دریافت مبلغ، تایید کنید:**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="تایید دریافت ✅", callback_data=f"AdminApproveBalance-{chat_id}-{amount}-{transaction_id}")],
                                     [InlineKeyboardButton(text="رد ❌", callback_data=f"AdminRejectBalance-{chat_id}-{transaction_id}")]
                                 ]))
            
            await app.send_message(chat_id,
                                 f"**درخواست افزایش موجودی شما برای مالک ارسال شد.**\n\n"
                                 f"**مبلغ:** `{amount:,}` تومان\n"
                                 f"**شناسه تراکنش:** `{transaction_id}`\n\n"
                                 f"**لطفا مبلغ را به شماره کارت مالک واریز کنید و منتظر تایید باشید.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                 ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**لطفا مبلغ معتبر ارسال کنید.**")

    elif user["step"] == "sales_set_prices":
        lines = text.strip().split('\n')
        
        if len(lines) != 6:
            await app.send_message(chat_id,
                                 "**خطا: باید دقیقاً 6 قیمت (هر قیمت در یک خط) وارد کنید.**\n\n"
                                 "**فرمت صحیح:**\n```\nقیمت_1ماهه\nقیمت_2ماهه\nقیمت_3ماهه\nقیمت_4ماهه\nقیمت_5ماهه\nقیمت_6ماهه\n```",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                                 ]))
            return
        
        price_keys = ['1month', '2month', '3month', '4month', '5month', '6month']
        price_names = {
            '1month': '1 ماهه',
            '2month': '2 ماهه', 
            '3month': '3 ماهه',
            '4month': '4 ماهه',
            '5month': '5 ماهه',
            '6month': '6 ماهه'
        }
        
        valid_prices = []
        errors = []
        
        for i, line in enumerate(lines):
            price_text = line.strip()
            if not price_text.isdigit():
                errors.append(f"قیمت {price_names[price_keys[i]]} باید عدد باشد: {price_text}")
            else:
                price = int(price_text)
                # بررسی اینکه قیمت کمتر از قیمت اصلی نباشد
                main_prices = get_prices()
                if price < int(main_prices[price_keys[i]]):
                    errors.append(f"قیمت {price_names[price_keys[i]]} نمی‌تواند کمتر از قیمت اصلی ({main_prices[price_keys[i]]}) باشد")
                else:
                    valid_prices.append((price_keys[i], price))
        
        if errors:
            error_text = "**خطا در ورود قیمت‌ها:**\n\n"
            for error in errors:
                error_text += f"• {error}\n"
            error_text += "\n**لطفا مجددا تلاش کنید.**"
        
            await app.send_message(chat_id, error_text,
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                            ]))
            return
        
        # ذخیره قیمت‌ها
        prices_dict = {key: price for key, price in valid_prices}
        update_sales_admin_prices(chat_id, prices_dict)
        
        success_text = "**✅ قیمت‌های شما با موفقیت به‌روزرسانی شد:**\n\n"
        for key, price in valid_prices:
            success_text += f"**{price_names[key]}:** `{price:,}` تومان\n"
        
        success_text += "\n**تغییرات ذخیره شدند.**"
        
        await app.send_message(chat_id, success_text,
                        reply_markup=InlineKeyboardMarkup([
                             [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="SalesAdminPanel")]
                        ]))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "edit_main_channel":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            channel_id = text.strip()
            if update_channel('main', channel_id):
                await app.send_message(chat_id,
                                 f"**✅ کانال اصلی با موفقیت به @{get_channel_username(channel_id)} تغییر یافت.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            else:
                await app.send_message(chat_id,
                                 "**❌ خطا در تغییر کانال. لطفا مجدد تلاش کنید.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "edit_help_channel":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            channel_id = text.strip()
            if update_channel('help', channel_id):
                await app.send_message(chat_id,
                                 f"**✅ کانال راهنما با موفقیت به @{get_channel_username(channel_id)} تغییر یافت.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            else:
                await app.send_message(chat_id,
                                 "**❌ خطا در تغییر کانال. لطفا مجدد تلاش کنید.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "edit_api_channel":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            channel_id = text.strip()
            if update_channel('api', channel_id):
                await app.send_message(chat_id,
                                 f"**✅ کانال API با موفقیت به @{get_channel_username(channel_id)} تغییر یافت.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            else:
                await app.send_message(chat_id,
                                 "**❌ خطا در تغییر کانال. لطفا مجدد تلاش کنید.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "add_extra_channel":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            channel_id = text.strip()
            if add_channel(channel_id, 'extra'):
                await app.send_message(chat_id,
                                 f"**✅ کانال @{get_channel_username(channel_id)} با موفقیت به لیست کانال‌های جوین اجباری اضافه شد.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            else:
                await app.send_message(chat_id,
                                 "**❌ خطا در اضافه کردن کانال. لطفا مجدد تلاش کنید.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="ManageChannels")]
                                 ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "install_phone":
        if m.contact:
            phone_number = str(m.contact.phone_number)
            if not phone_number.startswith("+"):
                phone_number = f"+{phone_number}"
        
            update_data(f"UPDATE user SET phone = '{phone_number}' WHERE id = '{chat_id}'")
            update_data(f"UPDATE user SET step = 'install_api_id' WHERE id = '{chat_id}'")
        
            Create = f'<a href=https://t.me/{api_channel}>کلیک کنید!</a>'
            await app.send_message(m.chat.id, "**شماره شما ثبت شد.")
            
            await app.send_message(m.chat.id, f"**• لطفا `Api ID` خود را وارد کنید. ( نمونه : 123456 )**\n• آموزش ساخت : ( {Create} )\n\n**• لغو عملیات [ /start ]**")
        else:
            await app.send_message(chat_id, "**لطفا با استفاده از دکمه، شماره تلفن را به اشتراک بگذارید.**")

    elif user["step"] == "install_api_id":
        if text and text.isdigit():
            update_data(f"UPDATE user SET api_id = '{text}' WHERE id = '{chat_id}'")
            update_data(f"UPDATE user SET step = 'install_api_hash' WHERE id = '{chat_id}'")
            await app.send_message(m.chat.id, f"**• لطفا `Api Hash` خود را وارد کنید.\n( مثال : abcdefg0123456abcdefg123456789c )\n\n• لغو عملیات [ /start ]**")
        else:
            await app.send_message(chat_id, "**• لطفا یک Api ID معتبر وارد کنید.**")

    elif user["step"] == "install_api_hash":
        if text and len(text) == 32:
            update_data(f"UPDATE user SET api_hash = '{text}' WHERE id = '{chat_id}'")
        
            user_info = get_data(f"SELECT phone, api_id, api_hash FROM user WHERE id = '{chat_id}' LIMIT 1")
            
            api_hash = user_info["api_hash"]
            if len(api_hash) >= 8:
                masked_hash = f"{api_hash[:4]}{'*' * (len(api_hash)-8)}{api_hash[-4:]}"
            else:
                masked_hash = "****"
            
            await app.send_message(chat_id,
                f"**📞 Number : `{user_info['phone']}`\n🆔 Api ID : `{user_info['api_id']}`\n🆔 Api Hash : `{masked_hash}`\n\n• آیا اطلاعات را تایید میکنید؟**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("بله (✅)", callback_data="ConfirmInstall"),
                    InlineKeyboardButton("خیر (❎)", callback_data="ChangeInfo")],
                    [InlineKeyboardButton("(🔙) بازگشت", callback_data="Back")]
            ]))
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}'")
        else:
            await app.send_message(chat_id, "**لطفا یک Api Hash معتبر وارد کنید.**")

    elif user["step"].startswith("install_with_language-"):
        parts = user["step"].split("-")
        if len(parts) >= 5:
            phone = parts[1]
            api_id = parts[2]
            api_hash = parts[3]
            language = parts[4]
        
            if text:
                if "." in text:
                    code = "".join(text.split("."))
                else:
                    code = text
        
                if code.isdigit() and len(code) == 5:
                    await verify_code_and_login(chat_id, phone, api_id, api_hash, code, language)
                else:
                    await app.send_message(chat_id, "**• کد وارد شده نامعتبر است، مجدد کد را وارد کنید.**")
            else:
                await app.send_message(chat_id, "**لطفا کد تأیید را ارسال کنید.**")

    elif user["step"].startswith("install_code-"):
        parts = user["step"].split("-")
        phone = parts[1]
        api_id = parts[2]
        api_hash = parts[3]
        language = parts[4] if len(parts) > 4 else "fa"

        if text:
            if "." in text:
                code = "".join(text.split("."))
            else:
                code = text
    
            if code.isdigit() and len(code) == 5:
                await verify_code_and_login(chat_id, phone, api_id, api_hash, code, language)
        
        else:
            await app.send_message(chat_id, "**لطفا کد تأیید را ارسال کنید.**")

    elif user["step"].startswith("install_2fa-"):
        parts = user["step"].split("-")
        phone = parts[1]
        api_id = parts[2]
        api_hash = parts[3]
        language = parts[4] if len(parts) > 4 else "fa"

        if text:
            await verify_2fa_password(chat_id, phone, api_id, api_hash, text, language)
        else:
            await app.send_message(chat_id, "**• لطفا رمز دومرحله ای اکانت را بدون هیچ کلمه یا کاراکتر اضافه ای ارسال کنید :**")
    
    elif user["step"] == "admin_create_code_days":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                days = int(text.strip())
                code = create_code(days)
                await app.send_message(chat_id,
                                 f"**• کد انقضا با موفقیت ایجاد شد.**\n\n"
                                 f"**• کد : ( `{code}` )**\n"
                                 f"**• تعداد روز : ( {days} روز )**\n\n"
                                 f"**• تاریخ ثبت : ( `{time.strftime('%Y-%m-%d %H:%M:%S')}` )",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]
                                 ]))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**لطفا یک عدد معتبر وارد کنید.**")

    elif user["step"] == "use_code":
        code_value = text.strip().upper()
        code_data = get_code_by_value(code_value)
        
        if code_data:
            user_data = get_data(f"SELECT expir FROM user WHERE id = '{chat_id}' LIMIT 1")
            old_expir = user_data["expir"] if user_data else 0
            new_expir = old_expir + code_data["days"]
            
            update_data(f"UPDATE user SET expir = '{new_expir}' WHERE id = '{chat_id}' LIMIT 1")
            
            use_code(code_value, chat_id)
            
            user_info = await app.get_users(chat_id)
            username = f"@{user_info.username}" if user_info.username else "ندارد"
            
            days = code_data["days"]
            if days == 31:
                month_text = "یک ماه"
            elif days == 62:
                month_text = "دو ماه"
            elif days == 93:
                month_text = "سه ماه"
            elif days == 124:
                month_text = "چهار ماه"
            elif days == 155:
                month_text = "پنج ماه"
            elif days == 186:
                month_text = "شش ماه"
            else:
                month_text = f"{days} روز"
            
            message_to_user = f"**• افزایش انقضا با موفقیت انجام شد.**\n\n"
            message_to_user += f"**• کد شارژ استفاده شده : ( `{code_value}` )**\n"
            message_to_user += f"**• انقضای سلف شما {month_text} اضافه گردید.**\n\n"
            message_to_user += f"**• انقضای قبلی شما : ( `{old_expir}` روز )**\n\n"
            message_to_user += f"**• انقضای جدید : ( `{new_expir}` روز )**"
            
            await app.send_message(chat_id, message_to_user)
            
            message_to_admin = f"**کاربر ( {html.escape(user_info.first_name)} - {username} - {chat_id} ) با استفاده از کد `{code_value}` مقدار {month_text} انقضا خریداری کرد و این کد از لیست کدها حذف شد.**"
            await app.send_message(Admin, message_to_admin)
            
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
        else:
            await app.send_message(chat_id, "**کد ارسالی صحیح نیست.**")
            
    elif user["step"] == "edit_start_message":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            update_setting("start_message", text)
            await app.send_message(chat_id, "**✅ متن پیام استارت با موفقیت به‌روزرسانی شد.**",
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                             ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif user["step"] == "edit_price_message":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            update_setting("price_message", text)
            await app.send_message(chat_id, "**✅ متن پیام نرخ با موفقیت به‌روزرسانی شد.**",
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                             ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif user["step"] == "edit_self_message":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            update_setting("whatself_message", text)
            await app.send_message(chat_id, "**✅ متن توضیح سلف با موفقیت به‌روزرسانی شد.**",
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                             ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif user["step"] == "edit_all_prices":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            lines = text.strip().split('\n')
        
            if len(lines) != 6:
                await app.send_message(chat_id, "**خطا: باید دقیقا 6 قیمت (هر قیمت در یک خط) وارد کنید.**\n\n**فرمت صحیح:**\n```\nقیمت 1 ماهه\nقیمت 2 ماهه\nقیمت 3 ماهه\nقیمت 4 ماهه\nقیمت 5 ماهه\nقیمت 6 ماهه\n```",
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                ]))
                return
        
            price_keys = ['1month', '2month', '3month', '4month', '5month', '6month']
            price_names = {
                '1month': '1 ماهه',
                '2month': '2 ماهه', 
                '3month': '3 ماهه',
                '4month': '4 ماهه',
                '5month': '5 ماهه',
                '6month': '6 ماهه'
            }
        
            valid_prices = []
            errors = []
        
            for i, line in enumerate(lines):
                price_text = line.strip()
                if not price_text.isdigit():
                    errors.append(f"قیمت {price_names[price_keys[i]]} باید عدد باشد: {price_text}")
                else:
                    valid_prices.append((price_keys[i], price_text))
        
            if errors:
                error_text = "**خطا در ورود قیمت‌ها:**\n\n"
                for error in errors:
                    error_text += f"• {error}\n"
                error_text += "\n**لطفا مجددا تلاش کنید.**"
            
                await app.send_message(chat_id, error_text,
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                ]))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
                return
        
            success_text = "**✅ قیمت‌ها با موفقیت به‌روزرسانی شد:**\n\n"
            for key, price in valid_prices:
                update_setting(f"price_{key}", price)
                success_text += f"**{price_names[key]}:** {price} تومان\n"
        
            success_text += "\n**تغییرات ذخیره شدند.**"
        
            await app.send_message(chat_id, success_text,
                            reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                            ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")

    elif user["step"] == "edit_card_number":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.replace(" ", "").isdigit() and len(text.replace(" ", "")) >= 16:
                update_setting("card_number", text.replace(" ", ""))
                await app.send_message(chat_id, f"**✅ شماره کارت با موفقیت به `{text}` به‌روزرسانی شد.**",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                                 ]))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**شماره کارت نامعتبر است. لطفا یک شماره کارت معتبر وارد کنید.**")

    elif user["step"] == "edit_card_name":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            update_setting("card_name", text)
            await app.send_message(chat_id, f"**✅ نام صاحب کارت با موفقیت به `{text}` به‌روزرسانی شد.**",
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminSettings")]
                             ]))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_broadcast":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            mess = await app.send_message(chat_id, "**• ارسال پیام شما درحال انجام است، لطفا صبور باشید.**")
            users = get_datas(f"SELECT id FROM user")
            for user in users:
                await app.copy_message(from_chat_id=chat_id, chat_id=user[0], message_id=m_id)
                await asyncio.sleep(0.1)
            await app.edit_message_text(chat_id, mess.id, "**• پیام شما به تمامی کاربران ارسال شد.**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_forward":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            mess = await app.send_message(chat_id, "**• فوروارد پیام شما درحال انجام است، لطفا صبور باشید.**")
            users = get_datas(f"SELECT id FROM user")
            for user in users:
                await app.forward_messages(from_chat_id=chat_id, chat_id=user[0], message_ids=m_id)
                await asyncio.sleep(0.1)
            await app.edit_message_text(chat_id, mess.id, "**• پیام شما به تمامی کاربران فوروارد شد.**", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
            ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_block":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                    if block is None:
                        await app.send_message(user_id, f"**شما به دلیل نقض قوانین از ربات مسدود شدید.\n• با پشتیان ها در ارتباط باشید.**")
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] از ربات مسدود شد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                        update_data(f"INSERT INTO block(id) VALUES({user_id})")
                    else:
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] از ربات مسدود شد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                else:
                    await app.send_message(chat_id, "**کاربر پیدا نشد.\n• ابتدا آیدی کاربر را بررسی کرده و از ربات بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_unblock":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    block = get_data(f"SELECT * FROM block WHERE id = '{user_id}' LIMIT 1")
                    if block is not None:
                        await app.send_message(user_id, f"**شما توسط مدیر از لیست سیاه ربات خارج شدید.\n• اکنون میتوانید از ربات استفاده کنید.**")
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] از لیست سیاه خارج شد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                        update_data(f"DELETE FROM block WHERE id = '{user_id}' LIMIT 1")
                    else:
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] در لیست سیاه وجود ندارد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                else:
                    await app.send_message(chat_id, "**کاربر پیدا نشد.\n•ابتدا آیدی ربات را بررسی کرده و از کاربر بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_add_expiry1":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    await app.send_message(chat_id, "**• آیدی عددی کاربر را جهت افزایش انقضا ارسال کنید.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
                    update_data(f"UPDATE user SET step = 'admin_add_expiry2-{user_id}' WHERE id = '{chat_id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, f"**کاربر پیدا نشد.\n• ابتدا آیدی کاربر را بررسی کرده و از کاربر بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
    
    elif user["step"].startswith("admin_add_expiry2"):
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(user["step"].split("-")[1])
                count = int(text.strip())
                user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
                user_upexpir = int(user_expir["expir"]) + int(count)
                update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
                
                await app.send_message(user_id, f"**افزایش انقضا برای شما انجام شد.\n• ( `{count}` روز ) به انقضای شما اضافه گردید.\n\n• انقضای جدید شما : ( {user_upexpir} روز )\n")
                
                await app.send_message(chat_id, f"**افزایش انقضا برای کاربر [ `{user_id}` ] انجام شد.\n\n• انقضای اضافه شده: ( `{count}` روز )\n• انقضای جدید کاربر : ( `{user_upexpir}` روز )**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
    
    elif user["step"] == "admin_deduct_expiry1":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    await app.send_message(chat_id, "**زمان انقضای موردنظر را برای کاهش ارسال کنید:**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
                    update_data(f"UPDATE user SET step = 'admin_deduct_expiry2-{user_id}' WHERE id = '{chat_id}' LIMIT 1")
                else:
                    await app.send_message(chat_id, f"**کاربر پیدا نشد.\n• ابتدا آیدی کاربر را بررسی کرده و از کاربر بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
    
    elif user["step"].startswith("admin_deduct_expiry2"):
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(user["step"].split("-")[1])
                count = int(text.strip())
                user_expir = get_data(f"SELECT expir FROM user WHERE id = '{user_id}' LIMIT 1")
                user_upexpir = int(user_expir["expir"]) - int(count)
                update_data(f"UPDATE user SET expir = '{user_upexpir}' WHERE id = '{user_id}' LIMIT 1")
                
                await app.send_message(user_id, f"**کسر انقضا برای شما انجام شد.\n\nانقضای جدید شما : ( `{user_upexpir}` روز )\n\n• انقضای کسر شده ؛ ( `{count}` روز )**")
                
                await app.send_message(chat_id, f"**کسر انقضا برای کاربر [ `{user_id}` ] انجام شد.\n\n• انقضای کسر شده: ( `{count}` روز )\n• انقضای جدید کاربر : ( `{user_upexpir}` روز )**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
                update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
    
    elif user["step"] == "admin_activate_self":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    if os.path.isfile(f"sessions/{user_id}.session-journal"):
                        user_data = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
                        if user_data["self"] != "active":
                            mess = await app.send_message(chat_id, f"**• اشتراک سلف برای کاربر [ `{user_id}` ] درحال فعالسازی است، لطفا صبور باشید.**")
                            process = subprocess.Popen(["python3", "self.py", str(user_id), str(API_ID), API_HASH, Helper_ID], cwd=f"selfs/self-{user_id}")
                            await asyncio.sleep(10)
                            if process.poll() is None:
                                await app.edit_message_text(chat_id, mess.id, f"**• ربات سلف با موفقیت برای کاربر [ `{user_id}` ] فعال شد.**", reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                                ))
                                update_data(f"UPDATE user SET self = 'active' WHERE id = '{user_id}' LIMIT 1")
                                update_data(f"UPDATE user SET pid = '{process.pid}' WHERE id = '{user_id}' LIMIT 1")
                                add_admin(user_id)
                                await setscheduler(user_id)
                                await app.send_message(user_id, f"**• اشتراک سلف توسط مدیریت برای شما فعال شد.\nاکنون مجاز به استفاده از ربات دستیار میباشید.**")
                            else:
                                await app.edit_message_text(chat_id, mess.id, f"**فعالسازی سلف برای کاربر [ `{user_id}` ] با خطا مواجه شد.**", reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                                ))
                        else:
                            await app.send_message(chat_id, f"**اشتراک سلف برای کاربر [ `{user_id}` ] غیرفعال بوده است.**", reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                            ))
                    else:
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] اشتراک فعالی ندارد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                else:
                    await app.send_message(chat_id, "**کاربر یافت نشد، ابتدا از کاربر بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
    
    elif user["step"] == "admin_deactivate_self":
        if chat_id == Admin or helper_getdata(f"SELECT * FROM adminlist WHERE id = '{chat_id}' LIMIT 1") is not None:
            if text.isdigit():
                user_id = int(text.strip())
                if get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1") is not None:
                    if os.path.isfile(f"sessions/{user_id}.session-journal"):
                        user_data = get_data(f"SELECT * FROM user WHERE id = '{user_id}' LIMIT 1")
                        if user_data["self"] != "inactive":
                            mess = await app.send_message(chat_id, "**• درحال پردازش، لطفا صبور باشید.**")
                            try:
                                os.kill(user_data["pid"], signal.SIGKILL)
                            except:
                                pass
                            await app.edit_message_text(chat_id, mess.id, f"**• ربات سلف برای کاربر [ `{user_id}` ] غیرفعال شد.**", reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                            ))
                            update_data(f"UPDATE user SET self = 'inactive' WHERE id = '{user_id}' LIMIT 1")
                            if user_id != Admin:
                                delete_admin(user_id)
                            job = scheduler.get_job(str(user_id))
                            if job:
                                scheduler.remove_job(str(user_id))
                            await app.send_message(user_id, f"**کاربر [ `{user_id}` ] سلف شما به دلایلی غیرفعال شد، لطفا با پشتیبان ها در ارتباط باشید.**")
                        else:
                            await app.send_message(chat_id, f"**ربات سلف از قبل برای کاربر [ `{user_id}` ] غیرفعال بوده است.**", reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                            ))
                    else:
                        await app.send_message(chat_id, f"**کاربر [ `{user_id}` ] انقضای فعالی ندارد.**", reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                        ))
                else:
                    await app.send_message(chat_id, "**کاربر یافت نشد، ابتدا از کاربر بخواهید ربات را [ /start ] کند.**", reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                    ))
            else:
                await app.send_message(chat_id, "**فقط ارسال عدد مجاز است.**", reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
                ))
            update_data(f"UPDATE user SET step = 'none' WHERE id = '{chat_id}' LIMIT 1")
            
    elif user["step"].startswith("ureply-"):
        user_id = int(user["step"].split("-")[1])
        mess = await app.copy_message(from_chat_id=Admin, chat_id=user_id, message_id=m_id)
        await app.send_message(user_id, "**• کاربر گرامی، پاسخ شما از پشتیبانی دریافت شد.**", reply_to_message_id=mess.id)
        await app.send_message(Admin, "**• پیام شما برای کاربر ارسال شد.**", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="(🔙) بازگشت", callback_data="AdminPanel")]]
        ))
        update_data(f"UPDATE user SET step = 'none' WHERE id = '{Admin}' LIMIT 1")
#================== Print Format ===================#
TEXT1 = "ᗑ Succesfully!"
TEXT2 = "Telegram Bot Runned : "
TEXT3 = "Last Update Version : 12.12.21"
RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[37m"
GREEN = "\033[32m"
RED = "\033[31m"
#================== Run ===================#
app.start()
print(f"{BOLD}{GREEN}{TEXT1}{RESET}")
print(f"{BOLD}{WHITE}{TEXT2}@{(app.get_me()).username}{RESET}")
print(f"{BOLD}{RED}{TEXT3}{RESET}")
idle()
app.stop()
























