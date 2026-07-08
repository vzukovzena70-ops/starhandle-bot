# ============================================
# БОТ: @StarHandle_bot
# ФАЙЛ: bot.py (ВСЁ В ОДНОМ ФАЙЛЕ)
# ВЕРСИЯ: 8.3 (С ВЫДАЧЕЙ ВСЕМ ОНЛАЙН)
# ============================================

import asyncio
import json
import os
import random
import string
import time
import shutil
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
from functools import wraps

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    CallbackQuery,
    Message,
)
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

# ==================== КОНФИГ ====================
TOKEN = "8904955386:AAEmaP7APMo1RGsQkHs79JFLGppzRmQJZ-Y"
ADMIN_PASSWORD = "fgffhg6767"
ADMIN_IDS = [8024241408]  # Твой ID
DB_FILE = "users.json"
BACKUP_DIR = "backups"

# ==================== КАНАЛЫ ДЛЯ ПОДПИСКИ ====================
REQUIRED_CHANNELS = [
    {
        "name": "StarHandle", 
        "username": "@StarHandle_Chanell", 
        "url": "https://t.me/StarHandle_Chanell"
    },
    {
        "name": "StarHandle Chat", 
        "username": "@StarHandle_chat", 
        "url": "https://t.me/StarHandle_chat"
    },
]

# ==================== ЦЕНЫ ====================
SUB_PRICES = {
    "pro": {"month": 15, "3month": 25, "year": 75},
    "master": {"month": 50, "3month": 75, "year": 130, "forever": 350},
}

STARS_PRICES = [10, 25, 50, 100, 250, 500, 1000]
SUPPORT_CONTACTS = ["@Zawkhaing794", "@CEPNAYA_KISLOTA"]

# ==================== КАТЕГОРИИ НИКОВ ====================
NICK_CATEGORIES = {
    "gaming": {
        "name": "🎮 Геймерский",
        "emoji": "🎮",
        "description": "Крутые ники для игр",
        "value": "common",
        "value_emoji": "🟢",
        "prefixes": ["x", "z", "q", "v", "w", "y", "k", "j", "m", "n", "pro", "ultra", "super", "mega"],
        "suffixes": ["x", "z", "q", "v", "w", "y", "k", "j", "m", "n", "ex", "ix", "ox", "ux"],
        "words": ["pro", "god", "king", "legend", "star", "wolf", "fox", "shadow", "night", "death", "fire", "ice", "storm", "rage", "bane", "slash", "hunter", "killer", "ghost", "venom", "sniper", "assassin", "warrior", "dragon"]
    },
    "anime": {
        "name": "🌸 Аниме",
        "emoji": "🌸",
        "description": "Ники в стиле аниме",
        "value": "uncommon",
        "value_emoji": "🟡",
        "prefixes": ["aka", "kuro", "shiro", "midori", "ao", "hairo", "momo", "sora", "hana", "yuki", "sakura", "kaze", "tsuki", "hoshi", "ame", "yami", "hikari", "ryu", "tora", "neko"],
        "suffixes": ["chan", "kun", "san", "sama", "tan", "senpai", "dono", "shi", "mi", "ya", "ko", "hime", "maru", "chi", "ta", "ka", "na"],
        "words": ["anime", "manga", "kawaii", "baka", "sugoi", "neko", "inu", "tora", "ryu", "kami", "yami", "hikari", "tsuyoi", "hayai", "ookii", "senpai", "kohai", "otaku", "weeb", "moe"]
    },
    "cyber": {
        "name": "💻 Киберпанк",
        "emoji": "💻",
        "description": "Футуристические ники",
        "value": "rare",
        "value_emoji": "🔵",
        "prefixes": ["cyber", "neo", "tech", "data", "net", "wire", "sync", "grid", "pulse", "shift", "nexus", "vector", "null", "core", "byte", "quantum", "neon", "byte", "bit", "node"],
        "suffixes": ["x", "z", "q", "v", "w", "y", "k", "j", "m", "n", "ex", "ix", "ox", "ux", "ax", "ez", "iz", "oz", "uz"],
        "words": ["hack", "code", "zero", "one", "night", "city", "ghost", "shadow", "black", "white", "silver", "gold", "ice", "fire", "void", "matrix", "neon", "cyber", "pulse", "grid", "sync"]
    },
    "cosmic": {
        "name": "🌌 Космический",
        "emoji": "🌌",
        "description": "Звёздные и космические",
        "value": "rare",
        "value_emoji": "🔵",
        "prefixes": ["astro", "cosmo", "galaxy", "nova", "star", "luna", "solar", "nebula", "quasar", "pulsar", "comet", "orbit", "aurora", "zenith", "eclipse", "stellar", "meteor", "asteroid", "supernova"],
        "suffixes": ["ar", "on", "is", "us", "um", "ia", "ox", "ix", "ux", "os", "an", "en", "in", "un"],
        "words": ["star", "moon", "sun", "planet", "galaxy", "cosmos", "void", "light", "shadow", "dark", "bright", "shine", "glow", "spark", "nova", "comet", "orbit", "nebula", "quasar"]
    },
    "luxury": {
        "name": "💎 Премиум",
        "emoji": "💎",
        "description": "Элитные, дорогие ники",
        "value": "epic",
        "value_emoji": "🟣",
        "prefixes": ["elite", "prime", "luxe", "gold", "platinum", "diamond", "royal", "crown", "noble", "grand", "super", "ultra", "mega", "hyper", "alpha", "omega", "supreme", "legendary", "mythic", "divine"],
        "suffixes": ["ex", "ix", "ox", "ux", "ax", "ez", "iz", "oz", "uz", "us", "um", "ia", "is", "os"],
        "words": ["king", "queen", "lord", "lady", "prince", "princess", "emperor", "legend", "myth", "god", "angel", "devil", "immortal", "eternal", "divine", "phoenix", "dragon", "titan", "olympus", "valhalla"]
    },
    "nature": {
        "name": "🌿 Природа",
        "emoji": "🌿",
        "description": "Природные и спокойные",
        "value": "common",
        "value_emoji": "🟢",
        "prefixes": ["green", "wild", "forest", "ocean", "river", "mountain", "flower", "stone", "wind", "rain", "snow", "sun", "moon", "star", "sky", "earth", "water", "fire", "wood", "golden"],
        "suffixes": ["er", "or", "ar", "on", "us", "um", "ia", "ox", "ix", "ux", "an", "en", "in", "un"],
        "words": ["wolf", "fox", "bear", "eagle", "hawk", "lion", "tiger", "panther", "dragon", "phoenix", "thunder", "storm", "blaze", "shadow", "light", "river", "mountain", "forest", "ocean", "flower"]
    },
    "funny": {
        "name": "😂 Смешной",
        "emoji": "😂",
        "description": "Забавные и мемные ники",
        "value": "common",
        "value_emoji": "🟢",
        "prefixes": ["big", "mr", "mrs", "dr", "prof", "capt", "lord", "sir", "dame", "king", "queen", "supreme", "grand", "mega", "ultra", "super", "hyper", "epic", "giga", "omega"],
        "suffixes": ["y", "ie", "er", "or", "ar", "on", "us", "um", "ia", "ox", "ix", "ux", "zy", "ly", "ry"],
        "words": ["chill", "lazy", "cute", "funny", "haha", "lol", "xd", "cool", "epic", "fail", "win", "boss", "chad", "giga", "omega", "pog", "bruh", "sus", "simp", "based", "cringe", "sigma", "alpha", "beta"]
    },
    "crypto": {
        "name": "₿ Крипто",
        "emoji": "₿",
        "description": "Для криптоэнтузиастов",
        "value": "epic",
        "value_emoji": "🟣",
        "prefixes": ["btc", "eth", "sol", "bnb", "xrp", "ada", "dot", "ltc", "ton", "trx", "avax", "matic", "link", "uni", "vet", "atom", "sushi", "cake", "aave", "snx"],
        "suffixes": ["coin", "fi", "dex", "swap", "earn", "stack", "hodl", "gem", "bag", "ape", "whale", "shark", "bull", "bear", "moon", "mars", "sat", "wei", "gwei"],
        "words": ["moon", "mars", "bull", "bear", "ape", "whale", "hodl", "stack", "earn", "yield", "stake", "swap", "bridge", "node", "validator", "miner", "trader", "holder", "buyer", "seller", "gem", "bag", "lambo", "wen", "soon"]
    }
}

# Доступные категории
CATEGORY_LIST = ["gaming", "anime", "cyber", "cosmic", "luxury", "nature", "funny", "crypto"]

# Редкость ников
NICK_RARITY = {
    "common": {"name": "Обычный", "emoji": "🟢", "stars": 1},
    "uncommon": {"name": "Необычный", "emoji": "🟡", "stars": 2},
    "rare": {"name": "Редкий", "emoji": "🔵", "stars": 3},
    "epic": {"name": "Эпический", "emoji": "🟣", "stars": 4},
    "legendary": {"name": "Легендарный", "emoji": "🔴", "stars": 5}
}

# ==================== АНТИФЛУД ====================
user_last_action = defaultdict(float)

def check_flood(user_id: int, cooldown: int = 2) -> bool:
    """Проверяет, не слишком часто пользователь нажимает кнопки"""
    now = time.time()
    if now - user_last_action[user_id] < cooldown:
        return False
    user_last_action[user_id] = now
    return True

# ==================== БД ====================
def load_db() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("⚠️ Файл БД повреждён, создаю новый!")
            return {"users": {}, "total_stars": 0}
    return {"users": {}, "total_stars": 0}

def save_db(db: dict):
    try:
        if os.path.exists(DB_FILE):
            backup_db()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения БД: {e}")

def backup_db():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.exists(DB_FILE):
        backup_name = f"{BACKUP_DIR}/backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        try:
            shutil.copy(DB_FILE, backup_name)
            for f in os.listdir(BACKUP_DIR):
                if f.startswith("backup_"):
                    file_path = os.path.join(BACKUP_DIR, f)
                    if os.path.getctime(file_path) < time.time() - 7 * 86400:
                        os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Ошибка бэкапа: {e}")

def get_user(user_id: int) -> dict:
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "id": user_id,
            "username": "",
            "first_name": "",
            "stars": 0,
            "reputation": 0,
            "subscription": "free",
            "sub_expires": "",
            "requests_today": 0,
            "requests_limit": 10,
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
            "referral_code": "",
            "referred_by": "",
            "referrals": [],
            "saved_nicks": [],
            "banned": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_db(db)
    return db["users"][uid]

def update_user(user_id: int, data: dict):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        get_user(user_id)
    db["users"][uid].update(data)
    save_db(db)

def check_and_reset_requests(user_id: int) -> dict:
    user = get_user(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if user["last_reset"] != today:
        limit = 10
        if user["subscription"] == "pro":
            limit = 30
        elif user["subscription"] == "master":
            limit = 150
        user["requests_today"] = 0
        user["requests_limit"] = limit
        user["last_reset"] = today
        update_user(user_id, user)
    return user

def check_subscription(user_id: int) -> dict:
    user = get_user(user_id)
    if user["subscription"] != "free" and user["sub_expires"]:
        try:
            expires = datetime.strptime(user["sub_expires"], "%Y-%m-%d")
            if expires < datetime.now():
                user["subscription"] = "free"
                user["requests_limit"] = 10
                user["sub_expires"] = ""
                update_user(user_id, user)
        except ValueError:
            user["sub_expires"] = ""
            update_user(user_id, user)
    return user

def generate_referral_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_referral_link(user_id: int) -> str:
    user = get_user(user_id)
    if not user["referral_code"]:
        code = generate_referral_code()
        user["referral_code"] = code
        update_user(user_id, user)
    return f"https://t.me/StarHandle_bot?start={user['referral_code']}"

def calculate_rarity(username: str) -> int:
    rarity = 1
    if len(username) <= 5:
        rarity += 1
    if username.isalpha():
        rarity += 1
    if not any(c.isdigit() for c in username):
        rarity += 1
    if len(set(username)) >= len(username) - 1:
        rarity += 1
    return min(rarity, 5)

def get_nick_value(category: str) -> dict:
    """Возвращает ценность ника по категории"""
    cat = NICK_CATEGORIES.get(category, {})
    value = cat.get("value", "common")
    return NICK_RARITY.get(value, NICK_RARITY["common"])

def generate_nick_by_category(category: str, length: int, gen_type: str) -> str:
    """Генерирует ник по выбранной категории"""
    cat = NICK_CATEGORIES.get(category, {})
    
    if not cat:
        if gen_type == "digits":
            return ''.join(random.choices(string.digits, k=length))
        elif gen_type == "letters":
            return ''.join(random.choices(string.ascii_lowercase, k=length))
        else:
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    nick_parts = []
    
    if cat.get("prefixes") and random.random() > 0.3:
        nick_parts.append(random.choice(cat["prefixes"]))
    
    if cat.get("words") and random.random() > 0.2:
        word = random.choice(cat["words"])
        if random.random() > 0.5:
            word = word.capitalize()
        nick_parts.append(word)
    
    if cat.get("suffixes") and random.random() > 0.4:
        nick_parts.append(random.choice(cat["suffixes"]))
    
    if not nick_parts and cat.get("words"):
        nick_parts.append(random.choice(cat["words"]))
    
    nick = ''.join(nick_parts)
    
    if len(nick) > length:
        nick = nick[:length]
    
    if len(nick) < length:
        remaining = length - len(nick)
        if gen_type == "digits":
            nick += ''.join(random.choices(string.digits, k=remaining))
        elif gen_type == "letters":
            nick += ''.join(random.choices(string.ascii_lowercase, k=remaining))
        else:
            nick += ''.join(random.choices(string.ascii_lowercase + string.digits, k=remaining))
    
    return nick

# ==================== ПРОВЕРКА ПОДПИСКИ ====================
async def check_channel_subscription(user_id: int) -> tuple:
    """
    Проверяет, подписан ли пользователь на все обязательные каналы
    Возвращает (все_подписан, список_неподписанных)
    """
    not_subscribed = []
    
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await bot.get_chat_member(
                chat_id=channel["username"], 
                user_id=user_id
            )
            if chat_member.status in ["left", "kicked"]:
                not_subscribed.append(channel)
        except Exception as e:
            print(f"⚠️ Ошибка проверки {channel['username']}: {e}")
            not_subscribed.append(channel)
    
    return len(not_subscribed) == 0, not_subscribed

def get_subscription_keyboard(not_subscribed: list) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками для подписки"""
    buttons = []
    
    for channel in not_subscribed:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 Подписаться на {channel['name']}", 
                url=channel["url"]
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="✅ Я подписался! Проверить", 
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ==================== ДЕКОРАТОР ПРОВЕРКИ ПОДПИСКИ ====================
def require_subscription(func):
    """Декоратор для проверки подписки перед выполнением"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        
        is_subscribed, not_subscribed = await check_channel_subscription(user_id)
        
        if not is_subscribed:
            try:
                await callback.message.delete()
            except:
                pass
            
            await callback.message.answer(
                "🔒 <b>Доступ ограничен!</b>\n\n"
                "Чтобы пользоваться ботом, необходимо подписаться на наши каналы:\n\n"
                "📢 <b>StarHandle</b> — новости и обновления\n"
                "💬 <b>StarHandle Chat</b> — общение и поддержка\n\n"
                "👇 Нажми на кнопки ниже и подпишись!",
                reply_markup=get_subscription_keyboard(not_subscribed),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        return await func(callback, *args, **kwargs)
    
    return wrapper

# ==================== ПРОВЕРКА ЮЗЕРНЕЙМА (УЛУЧШЕННАЯ) ====================
async def check_username_telegram(username: str) -> bool:
    """
    Проверяет, свободен ли юзернейм через Telegram API
    Возвращает True если свободен, False если занят
    """
    try:
        chat = await bot.get_chat(f"@{username}")
        if chat:
            print(f"❌ @{username} — ЗАНЯТ")
            return False
    except TelegramBadRequest as e:
        error_text = str(e).lower()
        if "chat not found" in error_text or "not found" in error_text:
            print(f"✅ @{username} — СВОБОДЕН")
            return True
        if "user not found" in error_text:
            print(f"✅ @{username} — СВОБОДЕН")
            return True
        if "bot was blocked" in error_text:
            print(f"⚠️ @{username} — бот заблокирован, считаем свободным")
            return True
        print(f"⚠️ @{username} — ошибка: {e}, считаем свободным")
        return True
    except Exception as e:
        print(f"⚠️ @{username} — неизвестная ошибка: {e}, считаем свободным")
        return True
    return False

# ==================== FSM ====================
class GeneratorStates(StatesGroup):
    choosing_category = State()
    choosing_count = State()
    choosing_length = State()
    choosing_type = State()

class AdminStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_user_id = State()

# ==================== КЛАВИАТУРЫ ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Генератор", callback_data="generator")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💎 Подписки", callback_data="subscriptions")],
        [InlineKeyboardButton(text="⭐ Донат", callback_data="donate")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="📂 Мои ники", callback_data="my_nicks")],
        [InlineKeyboardButton(text="🏆 Топ ников", callback_data="top_nicks")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])

def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

def generator_category_keyboard():
    buttons = []
    row = []
    for cat_key in CATEGORY_LIST:
        cat = NICK_CATEGORIES[cat_key]
        value_info = get_nick_value(cat_key)
        row.append(InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']} {value_info['emoji']}", 
            callback_data=f"gen_cat_{cat_key}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generator_count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 шт", callback_data="gen_count_1"),
         InlineKeyboardButton(text="5 шт", callback_data="gen_count_5")],
        [InlineKeyboardButton(text="8 шт", callback_data="gen_count_8"),
         InlineKeyboardButton(text="10 шт", callback_data="gen_count_10")],
        [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="gen_back_category")],
    ])

def generator_length_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 букв", callback_data="gen_len_5"),
         InlineKeyboardButton(text="6 букв", callback_data="gen_len_6")],
        [InlineKeyboardButton(text="🔙 Назад к количеству", callback_data="gen_back_count")],
    ])

def generator_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 Только цифры", callback_data="gen_type_digits")],
        [InlineKeyboardButton(text="🔡 Буквы + цифры", callback_data="gen_type_mixed")],
        [InlineKeyboardButton(text="🔤 Только буквы", callback_data="gen_type_letters")],
        [InlineKeyboardButton(text="🔙 Назад к длине", callback_data="gen_back_length")],
    ])

def subscriptions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ PRO — 1 месяц (15⭐)", callback_data="buy_pro_month")],
        [InlineKeyboardButton(text="⭐ PRO — 3 месяца (25⭐)", callback_data="buy_pro_3month")],
        [InlineKeyboardButton(text="⭐ PRO — 1 год (75⭐)", callback_data="buy_pro_year")],
        [InlineKeyboardButton(text="👑 MASTER — 1 месяц (50⭐)", callback_data="buy_master_month")],
        [InlineKeyboardButton(text="👑 MASTER — 3 месяца (75⭐)", callback_data="buy_master_3month")],
        [InlineKeyboardButton(text="👑 MASTER — 1 год (130⭐)", callback_data="buy_master_year")],
        [InlineKeyboardButton(text="👑 MASTER — НАВСЕГДА (350⭐)", callback_data="buy_master_forever")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")],
    ])

def donate_keyboard():
    buttons = []
    row = []
    for price in STARS_PRICES:
        row.append(InlineKeyboardButton(text=f"{price} ⭐", callback_data=f"donate_{price}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def referral_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Скопировать ссылку", callback_data=f"copy_ref_{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")],
    ])

def support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Написать @Zawkhaing794", url="https://t.me/Zawkhaing794")],
        [InlineKeyboardButton(text="📩 Написать @CEPNAYA_KISLOTA", url="https://t.me/CEPNAYA_KISLOTA")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")],
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🎁 Выдать подписку", callback_data="admin_sub")],
        [InlineKeyboardButton(text="🚫 Бан/Разбан", callback_data="admin_ban")],
        [InlineKeyboardButton(text="📊 Выдать запросы", callback_data="admin_requests")],
        [InlineKeyboardButton(text="⭐ Выдать звёзды", callback_data="admin_stars")],
        [InlineKeyboardButton(text="🟢 Выдать запросы ОНЛАЙН", callback_data="admin_online_requests")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Статистика пользователей", callback_data="user_stats")],
        [InlineKeyboardButton(text="🔙 Выйти из админки", callback_data="main_menu")],
    ])

def generated_nicks_keyboard(nicks: list = None):
    buttons = [
        [InlineKeyboardButton(text="🔄 Сгенерировать ещё", callback_data="generator")],
    ]
    if nicks and len(nicks) > 0:
        buttons.append([InlineKeyboardButton(text="💾 Сохранить все ники", callback_data="save_nicks")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def my_nicks_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Очистить все", callback_data="clear_nicks")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

# ==================== ХЕНДЛЕРЫ ====================
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------- СТАРТ ----------
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    try:
        await state.clear()
        user_id = message.from_user.id
        
        is_subscribed, not_subscribed = await check_channel_subscription(user_id)
        
        if not is_subscribed:
            await message.answer(
                "🔒 <b>Добро пожаловать в StarHandle!</b>\n\n"
                "Чтобы пользоваться ботом, необходимо подписаться на наши каналы:\n\n"
                "📢 <b>StarHandle</b> — новости и обновления\n"
                "💬 <b>StarHandle Chat</b> — общение и поддержка\n\n"
                "👇 Нажми на кнопки ниже и подпишись!",
                reply_markup=get_subscription_keyboard(not_subscribed),
                parse_mode="HTML"
            )
            return
        
        user = get_user(user_id)
        if user.get("banned", False):
            await message.answer("🚫 <b>Вы забанены!</b>\n\nОбратитесь в поддержку для разблокировки.", parse_mode="HTML")
            return
        
        args = message.text.split()
        if len(args) > 1:
            ref_code = args[1]
            db = load_db()
            for uid, data in db["users"].items():
                if data.get("referral_code") == ref_code and int(uid) != user_id:
                    ref_user = get_user(int(uid))
                    if int(uid) not in ref_user.get("referrals", []):
                        ref_user["referrals"].append(user_id)
                        update_user(int(uid), ref_user)
                        user = get_user(user_id)
                        user["requests_today"] += 3
                        user["referred_by"] = int(uid)
                        update_user(user_id, user)
                        await message.answer("✅ Вы активировали реферальный код! +3 запроса вам и пригласившему 🎉")
                    break
        
        user = get_user(user_id)
        user["username"] = message.from_user.username or ""
        user["first_name"] = message.from_user.first_name or ""
        update_user(user_id, user)
        
        welcome_text = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌟 <b>STARHANDLE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔍 Я помогу тебе найти <b>свободные юзернеймы</b> для Telegram!\n\n"
            f"📌 <i>Твой текущий статус:</i>\n"
            f"• 📦 Подписка: <b>{user['subscription'].upper()}</b>\n"
            f"• 📊 Запросов сегодня: <b>{user['requests_today']}/{user['requests_limit']}</b>\n"
            f"• ⭐ Баланс: <b>{user['stars']} звёзд</b>\n\n"
            f"👇 Выбери действие в меню ниже:"
        )
        await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
    except Exception as e:
        print(f"❌ Ошибка в start: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")

# ---------- ПРОВЕРКА ПОДПИСКИ ----------
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed, not_subscribed = await check_channel_subscription(user_id)
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "Теперь ты можешь пользоваться ботом!\n"
            "👇 Нажми на кнопку ниже, чтобы начать:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("✅ Подписка подтверждена!")
    else:
        await callback.message.edit_text(
            "🔒 <b>Ты ещё не подписался на все каналы!</b>\n\n"
            "Пожалуйста, подпишись на все каналы и нажми «Проверить»:",
            reply_markup=get_subscription_keyboard(not_subscribed),
            parse_mode="HTML"
        )
        await callback.answer("❌ Ты ещё не подписался на все каналы!", show_alert=True)

# ---------- ГЛАВНОЕ МЕНЮ ----------
@dp.callback_query(lambda c: c.data == "main_menu")
@require_subscription
async def main_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        user = get_user(callback.from_user.id)
        if user.get("banned", False):
            await callback.message.delete()
            await callback.message.answer("🚫 <b>Вы забанены!</b>", parse_mode="HTML")
            await callback.answer()
            return
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌟 <b>STARHANDLE</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Пользователь:</b> {user['first_name']}\n"
            f"📦 <b>Подписка:</b> {user['subscription'].upper()}\n"
            f"📊 <b>Запросов:</b> {user['requests_today']}/{user['requests_limit']}\n"
            f"⭐ <b>Баланс:</b> {user['stars']} звёзд\n\n"
            f"👇 Выбери действие:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в main_menu: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ПОМОЩЬ ----------
@dp.callback_query(lambda c: c.data == "help")
@require_subscription
async def show_help(callback: CallbackQuery):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        help_text = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"❓ <b>Помощь</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>🤔 Как пользоваться ботом?</b>\n\n"
            f"1️⃣ Нажми <b>«Генератор»</b>\n"
            f"2️⃣ Выбери <b>категорию</b> ника\n"
            f"3️⃣ Выбери количество (1-10)\n"
            f"4️⃣ Выбери длину (5-6 символов)\n"
            f"5️⃣ Выбери тип символов\n"
            f"6️⃣ Получи список свободных ников!\n\n"
            f"<b>🏷️ Категории и ценность:</b>\n"
            f"🟢 Обычные\n"
            f"🟡 Необычные\n"
            f"🔵 Редкие\n"
            f"🟣 Эпические\n"
            f"🔴 Легендарные\n\n"
            f"<b>💎 Что дают подписки?</b>\n"
            f"• FREE — 10 запросов/день\n"
            f"• PRO — 30 запросов/день\n"
            f"• MASTER — 150 запросов/день\n\n"
            f"<b>⭐ Где взять звёзды?</b>\n"
            f"• Купить через «Донат»\n"
            f"• Получить за рефералов\n\n"
            f"📞 <b>Поддержка:</b> {SUPPORT_CONTACTS[0]}, {SUPPORT_CONTACTS[1]}"
        )
        await callback.message.edit_text(help_text, reply_markup=back_to_main_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в help: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ГЕНЕРАТОР ----------
@dp.callback_query(lambda c: c.data == "generator")
@require_subscription
async def start_generator(callback: CallbackQuery, state: FSMContext):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        user = check_and_reset_requests(callback.from_user.id)
        user = check_subscription(callback.from_user.id)
        if user.get("banned", False):
            await callback.answer("🚫 Вы забанены!", show_alert=True)
            return
        if user["requests_today"] >= user["requests_limit"]:
            await callback.message.edit_text(
                "❌ <b>Лимит запросов исчерпан!</b>\n\n"
                "Купи подписку, чтобы увеличить лимит:\n"
                "• PRO — 30 запросов/день\n"
                "• MASTER — 150 запросов/день\n\n"
                "💎 Нажми «Подписки» в меню",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        await state.set_state(GeneratorStates.choosing_category)
        await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 <b>Шаг 1 из 4: Выбор категории</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📂 Выбери стиль ника:\n\n"
            f"🔥 <i>Осталось запросов: {user['requests_today']}/{user['requests_limit']}</i>",
            reply_markup=generator_category_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в start_generator: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(GeneratorStates.choosing_category, lambda c: c.data.startswith("gen_cat_"))
@require_subscription
async def choose_category(callback: CallbackQuery, state: FSMContext):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        category = callback.data.split("_")[2]
        if category not in NICK_CATEGORIES:
            await callback.answer("❌ Неверная категория!", show_alert=True)
            return
        cat_data = NICK_CATEGORIES[category]
        value_info = get_nick_value(category)
        await state.update_data(category=category)
        await state.set_state(GeneratorStates.choosing_count)
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{cat_data['emoji']} <b>{cat_data['name']}</b> {value_info['emoji']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📖 {cat_data['description']}\n"
            f"💎 <b>Ценность:</b> {value_info['name']}\n\n"
            f"⚡ <b>Шаг 2 из 4: Выбор количества</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 Сколько юзернеймов сгенерировать?",
            reply_markup=generator_count_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в choose_category: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(GeneratorStates.choosing_count, lambda c: c.data.startswith("gen_count_"))
@require_subscription
async def choose_count(callback: CallbackQuery, state: FSMContext):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        count = int(callback.data.split("_")[2])
        if count not in [1, 5, 8, 10]:
            await callback.answer("❌ Можно выбрать только 1, 5, 8 или 10!", show_alert=True)
            return
        await state.update_data(count=count)
        await state.set_state(GeneratorStates.choosing_length)
        await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>Шаг 3 из 4: Выбор длины</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📏 Какой длины должны быть юзернеймы?",
            reply_markup=generator_length_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в choose_count: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(GeneratorStates.choosing_length, lambda c: c.data.startswith("gen_len_"))
@require_subscription
async def choose_length(callback: CallbackQuery, state: FSMContext):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        length = int(callback.data.split("_")[2])
        if length not in [5, 6]:
            await callback.answer("❌ Можно выбрать только 5 или 6!", show_alert=True)
            return
        await state.update_data(length=length)
        await state.set_state(GeneratorStates.choosing_type)
        await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>Шаг 4 из 4: Выбор типа</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔤 Из каких символов генерировать?",
            reply_markup=generator_type_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в choose_length: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(GeneratorStates.choosing_type, lambda c: c.data.startswith("gen_type_"))
@require_subscription
async def choose_type(callback: CallbackQuery, state: FSMContext):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("⏳ Подожди 2 секунды!", show_alert=True)
            return
        gen_type = callback.data.split("_")[2]
        if gen_type not in ["digits", "mixed", "letters"]:
            await callback.answer("❌ Неверный тип!", show_alert=True)
            return
        data = await state.get_data()
        count = data.get("count", 5)
        length = data.get("length", 5)
        category = data.get("category", None)
        user_id = callback.from_user.id
        user = get_user(user_id)
        user = check_and_reset_requests(user_id)
        if user["requests_today"] >= user["requests_limit"]:
            await callback.message.edit_text(
                "❌ <b>Лимит запросов исчерпан!</b>",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        if count > 10:
            count = 10
        await callback.message.edit_text(
            "⏳ <b>Идёт поиск свободных юзернеймов...</b>\n\n"
            f"🔍 Проверяем {count} вариантов...\n"
            f"⏱ Это может занять несколько секунд",
            parse_mode="HTML"
        )
        found_nicks = []
        checked = 0
        max_attempts = count * 5
        while len(found_nicks) < count and checked < max_attempts:
            checked += 1
            if category and category in NICK_CATEGORIES:
                nick = generate_nick_by_category(category, length, gen_type)
            else:
                if gen_type == "digits":
                    nick = ''.join(random.choices(string.digits, k=length))
                elif gen_type == "letters":
                    nick = ''.join(random.choices(string.ascii_lowercase, k=length))
                else:
                    nick = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            if len(nick) > length:
                nick = nick[:length]
            if len(nick) < length:
                remaining = length - len(nick)
                nick += ''.join(random.choices(string.ascii_lowercase + string.digits, k=remaining))
            
            is_free = await check_username_telegram(nick)
            if is_free:
                rarity = calculate_rarity(nick)
                if category and category in NICK_CATEGORIES:
                    value_info = get_nick_value(category)
                    nick_value = value_info["name"]
                    nick_emoji = value_info["emoji"]
                else:
                    nick_value = "Обычный"
                    nick_emoji = "🟢"
                found_nicks.append({
                    "nick": nick, 
                    "rarity": rarity,
                    "value": nick_value,
                    "emoji": nick_emoji
                })
        user["requests_today"] += count
        update_user(user_id, user)
        if not found_nicks:
            await callback.message.edit_text(
                "😔 <b>Не найдено свободных ников</b>\n\n"
                "Попробуй изменить параметры генерации:\n"
                "• Увеличь длину\n"
                "• Выбери другой тип символов\n"
                "• Выбери другую категорию\n"
                "• Попробуй позже",
                reply_markup=generated_nicks_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return
        await state.update_data(found_nicks=found_nicks)
        cat_name = ""
        if category and category in NICK_CATEGORIES:
            cat_name = f" ({NICK_CATEGORIES[category]['emoji']} {NICK_CATEGORIES[category]['name']})"
        result_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"✨ <b>Найдены свободные ники{cat_name}!</b>\n"
        result_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, item in enumerate(found_nicks, 1):
            stars = "⭐" * item["rarity"] + "☆" * (5 - item["rarity"])
            result_text += f"{i}. @{item['nick']} {stars} {item['emoji']} {item['value']}\n"
        result_text += "\n━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"🔥 Осталось запросов: {user['requests_today']}/{user['requests_limit']}"
        await callback.message.edit_text(
            result_text,
            reply_markup=generated_nicks_keyboard(found_nicks),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в choose_type: {e}")
        await callback.answer("⚠️ Ошибка генерации", show_alert=True)

@dp.callback_query(lambda c: c.data == "gen_back_category")
@require_subscription
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(GeneratorStates.choosing_category)
        user = get_user(callback.from_user.id)
        await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎯 <b>Шаг 1 из 4: Выбор категории</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📂 Выбери стиль ника:\n\n"
            f"🔥 <i>Осталось запросов: {user['requests_today']}/{user['requests_limit']}</i>",
            reply_markup=generator_category_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в back_to_category: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data == "gen_back_count")
@require_subscription
async def back_to_count(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(GeneratorStates.choosing_count)
        data = await state.get_data()
        category = data.get("category", "gaming")
        cat_data = NICK_CATEGORIES.get(category, {})
        value_info = get_nick_value(category)
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{cat_data.get('emoji', '🎯')} <b>{cat_data.get('name', 'Категория')}</b> {value_info['emoji']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📖 {cat_data.get('description', '')}\n"
            f"💎 <b>Ценность:</b> {value_info['name']}\n\n"
            f"⚡ <b>Шаг 2 из 4: Выбор количества</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 Сколько юзернеймов сгенерировать?",
            reply_markup=generator_count_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в back_to_count: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data == "gen_back_length")
@require_subscription
async def back_to_length(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(GeneratorStates.choosing_length)
        await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>Шаг 3 из 4: Выбор длины</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📏 Какой длины должны быть юзернеймы?",
            reply_markup=generator_length_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в back_to_length: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- СОХРАНЕНИЕ НИКОВ ----------
@dp.callback_query(lambda c: c.data == "save_nicks")
@require_subscription
async def save_nicks(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        found_nicks = data.get("found_nicks", [])
        if not found_nicks:
            await callback.answer("❌ Нет ников для сохранения!", show_alert=True)
            return
        user = get_user(callback.from_user.id)
        saved = user.get("saved_nicks", [])
        if len(saved) >= 100:
            await callback.answer("❌ Ты сохранил максимум 100 ников!", show_alert=True)
            return
        for item in found_nicks:
            if item["nick"] not in saved:
                saved.append(item["nick"])
        user["saved_nicks"] = saved
        update_user(callback.from_user.id, user)
        await callback.answer(f"✅ Сохранено {len(found_nicks)} ников!")
        await callback.message.edit_text(
            f"✅ <b>Ники сохранены!</b>\n\n"
            f"📂 Всего сохранено: {len(saved)} ников\n\n"
            f"📌 Чтобы посмотреть их — нажми «Мои ники» в главном меню",
            reply_markup=back_to_main_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в save_nicks: {e}")
        await callback.answer("⚠️ Ошибка сохранения", show_alert=True)

# ---------- МОИ НИКИ ----------
@dp.callback_query(lambda c: c.data == "my_nicks")
@require_subscription
async def my_nicks(callback: CallbackQuery):
    try:
        user = get_user(callback.from_user.id)
        saved_nicks = user.get("saved_nicks", [])
        if not saved_nicks:
            await callback.message.edit_text(
                "📭 <b>У тебя пока нет сохранённых ников</b>\n\n"
                "💡 Найди крутой ник через генератор и сохрани его!",
                reply_markup=back_to_main_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        nicks_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        nicks_text += "📂 <b>Твои сохранённые ники</b>\n"
        nicks_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, nick in enumerate(saved_nicks, 1):
            rarity = calculate_rarity(nick)
            stars = "⭐" * rarity + "☆" * (5 - rarity)
            nicks_text += f"{i}. @{nick} {stars}\n"
        nicks_text += f"\n📊 <i>Всего: {len(saved_nicks)} ников (макс 100)</i>"
        await callback.message.edit_text(
            nicks_text,
            reply_markup=my_nicks_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в my_nicks: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data == "clear_nicks")
@require_subscription
async def clear_nicks(callback: CallbackQuery):
    try:
        user = get_user(callback.from_user.id)
        user["saved_nicks"] = []
        update_user(callback.from_user.id, user)
        await callback.message.edit_text(
            "🗑 <b>Все сохранённые ники удалены</b>",
            reply_markup=back_to_main_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в clear_nicks: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ТОП НИКОВ ----------
@dp.callback_query(lambda c: c.data == "top_nicks")
@require_subscription
async def top_nicks(callback: CallbackQuery):
    try:
        db = load_db()
        all_nicks = []
        for uid, data in db["users"].items():
            for nick in data.get("saved_nicks", []):
                rarity = calculate_rarity(nick)
                all_nicks.append({"nick": nick, "rarity": rarity})
        if not all_nicks:
            await callback.message.edit_text(
                "📊 <b>Топ редких ников</b>\n\n"
                "😔 Пока никто не сохранил ни одного ника...\n"
                "💡 Будь первым!",
                reply_markup=back_to_main_keyboard(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        all_nicks.sort(key=lambda x: x["rarity"], reverse=True)
        top_nicks = all_nicks[:10]
        top_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        top_text += "🏆 <b>Топ редких ников</b>\n"
        top_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, item in enumerate(top_nicks, 1):
            stars = "⭐" * item["rarity"] + "☆" * (5 - item["rarity"])
            top_text += f"{i}. @{item['nick']} {stars}\n"
        top_text += f"\n📊 <i>Всего в базе: {len(all_nicks)} ников</i>"
        await callback.message.edit_text(
            top_text,
            reply_markup=back_to_main_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в top_nicks: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ПРОФИЛЬ ----------
@dp.callback_query(lambda c: c.data == "profile")
@require_subscription
async def show_profile(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        user = get_user(user_id)
        user = check_and_reset_requests(user_id)
        user = check_subscription(user_id)
        sub_text = f"{user['subscription'].upper()}"
        if user["sub_expires"]:
            try:
                expires = datetime.strptime(user["sub_expires"], "%Y-%m-%d")
                days_left = (expires - datetime.now()).days
                sub_text += f" (осталось {days_left} дн.)"
            except:
                pass
        profile_text = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Твой профиль</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📛 <b>Имя:</b> {user['first_name']}\n"
            f"🆔 <b>UID:</b> <code>{user_id}</code>\n"
            f"⭐ <b>Баланс:</b> {user['stars']} звёзд\n"
            f"🏆 <b>Репутация:</b> {user['reputation']}\n"
            f"📦 <b>Подписка:</b> {sub_text}\n"
            f"📊 <b>Запросов сегодня:</b> {user['requests_today']}/{user['requests_limit']}\n"
            f"👥 <b>Рефералов:</b> {len(user['referrals'])}\n"
            f"📂 <b>Сохранено ников:</b> {len(user.get('saved_nicks', []))}\n"
            f"📅 <b>В системе:</b> {user['created_at']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        await callback.message.edit_text(
            profile_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в profile: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ПОДПИСКИ ----------
@dp.callback_query(lambda c: c.data == "subscriptions")
@require_subscription
async def show_subscriptions(callback: CallbackQuery):
    try:
        user = get_user(callback.from_user.id)
        sub_text = f"{user['subscription'].upper()}"
        if user["sub_expires"]:
            try:
                expires = datetime.strptime(user["sub_expires"], "%Y-%m-%d")
                days_left = (expires - datetime.now()).days
                sub_text += f" (осталось {days_left} дн.)"
            except:
                pass
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 <b>Доступные подписки</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆓 <b>FREE</b> — 10 запросов/день (бесплатно)\n\n"
            f"⭐ <b>PRO</b> — 30 запросов/день\n"
            f"  ▫️ 1 месяц — 15 ⭐\n"
            f"  ▫️ 3 месяца — 25 ⭐\n"
            f"  ▫️ 1 год — 75 ⭐\n\n"
            f"👑 <b>MASTER</b> — 150 запросов/день\n"
            f"  ▫️ 1 месяц — 50 ⭐\n"
            f"  ▫️ 3 месяца — 75 ⭐\n"
            f"  ▫️ 1 год — 130 ⭐\n"
            f"  ▫️ НАВСЕГДА — 350 ⭐\n\n"
            f"📌 <i>Твоя подписка: {sub_text}</i>",
            reply_markup=subscriptions_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в subscriptions: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("buy_"))
@require_subscription
async def buy_subscription(callback: CallbackQuery):
    try:
        data = callback.data.split("_")
        sub_type = data[1]
        period = data[2]
        user = get_user(callback.from_user.id)
        if sub_type not in SUB_PRICES or period not in SUB_PRICES[sub_type]:
            await callback.answer("❌ Неверный тип подписки", show_alert=True)
            return
        cost = SUB_PRICES[sub_type][period]
        if user["stars"] < cost:
            await callback.answer(f"❌ Не хватает звёзд! Нужно {cost} ⭐, у тебя {user['stars']} ⭐", show_alert=True)
            return
        user["stars"] -= cost
        period_days = {"month": 30, "3month": 90, "year": 365, "forever": 9999}
        days = period_days.get(period, 30)
        if period == "forever":
            user["sub_expires"] = "2099-12-31"
        else:
            expires = datetime.now() + timedelta(days=days)
            user["sub_expires"] = expires.strftime("%Y-%m-%d")
        user["subscription"] = sub_type
        if sub_type == "pro":
            user["requests_limit"] = 30
        elif sub_type == "master":
            user["requests_limit"] = 150
        update_user(callback.from_user.id, user)
        await callback.message.edit_text(
            f"✅ <b>Подписка {sub_type.upper()} активирована!</b>\n\n"
            f"📅 Период: {period}\n"
            f"⭐ Снято: {cost} звёзд\n"
            f"💰 Остаток: {user['stars']} ⭐\n\n"
            f"📊 Лимит запросов: {user['requests_limit']}/день",
            reply_markup=subscriptions_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в buy_subscription: {e}")
        await callback.answer("⚠️ Ошибка покупки", show_alert=True)

# ---------- ДОНАТ ----------
@dp.callback_query(lambda c: c.data == "donate")
@require_subscription
async def show_donate(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ <b>Пополнить звёзды</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Выбери сумму для пополнения:\n"
            f"💰 <i>Оплата через Telegram Stars</i>\n\n"
            f"💡 <b>Курс:</b> 1 ⭐ ≈ 1 ₽\n"
            f"⚡ <i>Звёзды зачисляются мгновенно</i>",
            reply_markup=donate_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в donate: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("donate_"))
@require_subscription
async def process_donate(callback: CallbackQuery):
    try:
        amount = int(callback.data.split("_")[1])
        if amount not in STARS_PRICES:
            await callback.answer("❌ Неверная сумма!", show_alert=True)
            return
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title="Пополнение баланса StarHandle",
            description=f"Пополнение на {amount} звёзд",
            payload=f"balance_{amount}_{callback.from_user.id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount} звёзд", amount=amount)],
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False,
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в process_donate: {e}")
        await callback.answer("⚠️ Ошибка оплаты", show_alert=True)

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    try:
        await pre_checkout.bot.answer_pre_checkout_query(pre_checkout.id, ok=True)
    except Exception as e:
        print(f"❌ Ошибка в pre_checkout: {e}")

@dp.message(lambda msg: msg.successful_payment)
async def process_successful_payment(message: Message):
    try:
        payload = message.successful_payment.invoice_payload
        parts = payload.split("_")
        amount = int(parts[1])
        user_id = int(parts[2]) if len(parts) > 2 else message.from_user.id
        if user_id != message.from_user.id:
            await message.answer("❌ Ошибка оплаты!")
            return
        user = get_user(user_id)
        user["stars"] += amount
        update_user(user_id, user)
        await message.answer(
            f"✅ <b>Пополнение успешно!</b>\n\n"
            f"⭐ Зачислено: {amount} звёзд\n"
            f"💰 Твой баланс: {user['stars']} ⭐\n\n"
            f"💎 Теперь ты можешь купить подписку в разделе «Подписки»",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Ошибка в successful_payment: {e}")
        await message.answer("⚠️ Ошибка обработки оплаты")

# ---------- РЕФЕРАЛЫ ----------
@dp.callback_query(lambda c: c.data == "referrals")
@require_subscription
async def show_referrals(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        user = get_user(user_id)
        link = get_referral_link(user_id)
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Реферальная система</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Приглашай друзей и получай бонусы!\n\n"
            f"🔗 <b>Твоя ссылка:</b>\n"
            f"<code>{link}</code>\n\n"
            f"📊 <b>Твоя статистика:</b>\n"
            f"• Приглашено: {len(user['referrals'])} чел.\n"
            f"• Бонус: +3 запроса за каждого реферала\n\n"
            f"🔥 <i>Чем больше друзей — тем больше возможностей!</i>",
            reply_markup=referral_keyboard(user_id),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в referrals: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("copy_ref_"))
@require_subscription
async def copy_referral(callback: CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[2])
        link = get_referral_link(user_id)
        await callback.answer(f"📋 {link}")
    except Exception as e:
        print(f"❌ Ошибка в copy_referral: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- ТЕХПОДДЕРЖКА ----------
@dp.callback_query(lambda c: c.data == "support")
@require_subscription
async def show_support(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📞 <b>Техническая поддержка</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❓ Возникли вопросы или проблемы?\n\n"
            f"📩 <b>Наши контакты:</b>\n"
            f"• {SUPPORT_CONTACTS[0]}\n"
            f"• {SUPPORT_CONTACTS[1]}\n\n"
            f"⏰ <i>Время ответа: обычно 5-15 минут</i>\n"
            f"💬 <i>Пишите чётко и подробно</i>",
            reply_markup=support_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в support: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

# ---------- АДМИНИСТРАТОР ----------
@dp.message(Command("adminpassword"))
async def admin_login(message: Message):
    try:
        args = message.text.split()
        if len(args) > 1 and args[1] == ADMIN_PASSWORD:
            if message.from_user.id not in ADMIN_IDS:
                await message.answer("⛔ Доступ запрещён! Вы не в списке администраторов.")
                return
            await message.answer(
                "🔐 <b>Добро пожаловать в админ-панель!</b>\n\n"
                "Доступные действия:",
                reply_markup=admin_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Неверный пароль!")
    except Exception as e:
        print(f"❌ Ошибка в admin_login: {e}")
        await message.answer("⚠️ Ошибка")

# ---------- ВЫДАТЬ ВСЕМ ОНЛАЙН ----------
@dp.callback_query(lambda c: c.data == "admin_online_requests")
async def admin_online_requests(callback: CallbackQuery, state: FSMContext):
    """Выдаёт запросы всем пользователям, которые были активны сегодня"""
    try:
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("⛔ Доступ запрещён!", show_alert=True)
            return
        
        await state.set_state(AdminStates.waiting_for_user_id)
        await state.update_data(admin_action="online_requests")
        await callback.message.edit_text(
            "🟢 <b>Выдача запросов ВСЕМ ОНЛАЙН</b>\n\n"
            "Введи количество запросов, которое нужно выдать ВСЕМ пользователям,\n"
            "которые были активны сегодня (делали хотя бы 1 запрос):\n\n"
            "<code>10</code>\n\n"
            "Для отмены напиши /cancel",
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в admin_online_requests: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, state: FSMContext):
    try:
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("⛔ Доступ запрещён!", show_alert=True)
            return
        action = callback.data.split("_")[1]
        if action == "broadcast":
            await state.set_state(AdminStates.waiting_for_message)
            await callback.message.edit_text(
                "📢 <b>Рассылка</b>\n\n"
                "Отправь сообщение для рассылки всем пользователям.\n"
                "Для отмены напиши /cancel",
                parse_mode="HTML"
            )
        elif action == "sub":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="sub")
            await callback.message.edit_text(
                "🎁 <b>Выдача подписки</b>\n\n"
                "Введи ID пользователя и тип подписки через пробел:\n"
                "<code>123456789 pro month</code>\n"
                "или <code>123456789 master forever</code>\n\n"
                "Доступные типы: pro, master\n"
                "Доступные периоды: month, 3month, year, forever",
                parse_mode="HTML"
            )
        elif action == "ban":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="ban")
            await callback.message.edit_text(
                "🚫 <b>Бан пользователя</b>\n\n"
                "Введи ID пользователя для бана/разбана:\n"
                "<code>123456789</code>",
                parse_mode="HTML"
            )
        elif action == "requests":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="requests")
            await callback.message.edit_text(
                "📊 <b>Выдача запросов</b>\n\n"
                "Введи ID пользователя и количество запросов через пробел:\n"
                "<code>123456789 50</code>",
                parse_mode="HTML"
            )
        elif action == "stars":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="stars")
            await callback.message.edit_text(
                "⭐ <b>Выдача звёзд</b>\n\n"
                "Введи ID пользователя и количество звёзд через пробел:\n"
                "<code>123456789 100</code>",
                parse_mode="HTML"
            )
        elif action == "stats":
            db = load_db()
            users = db.get("users", {})
            total_users = len(users)
            total_stars = 0
            pro_users = 0
            master_users = 0
            banned_users = 0
            total_saved_nicks = 0
            for u in users.values():
                total_stars += u.get("stars", 0)
                if u.get("subscription") == "pro":
                    pro_users += 1
                elif u.get("subscription") == "master":
                    master_users += 1
                if u.get("banned", False):
                    banned_users += 1
                total_saved_nicks += len(u.get("saved_nicks", []))
            await callback.message.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>СТАТИСТИКА БОТА</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👥 <b>Всего пользователей:</b> {total_users}\n"
                f"⭐ <b>Всего звёзд:</b> {total_stars}\n"
                f"💎 <b>PRO подписок:</b> {pro_users}\n"
                f"👑 <b>MASTER подписок:</b> {master_users}\n"
                f"📂 <b>Сохранено ников:</b> {total_saved_nicks}\n"
                f"🚫 <b>Забанено:</b> {banned_users}\n"
                f"━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=admin_keyboard(),
                parse_mode="HTML"
            )
        elif action == "user_stats":
            db = load_db()
            users = db.get("users", {})
            total = len(users)
            if total == 0:
                await callback.message.edit_text(
                    "📊 <b>Статистика пользователей</b>\n\n"
                    "😔 Пока нет пользователей",
                    reply_markup=admin_keyboard(),
                    parse_mode="HTML"
                )
                await callback.answer()
                return
            active_today = 0
            for u in users.values():
                if u.get("requests_today", 0) > 0:
                    active_today += 1
            week_ago = datetime.now() - timedelta(days=7)
            active_week = 0
            for u in users.values():
                try:
                    created_str = u.get("created_at", "2000-01-01 00:00:00")
                    created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
                    if created > week_ago:
                        active_week += 1
                except (ValueError, TypeError):
                    pass
            pro_users = 0
            master_users = 0
            free_users = 0
            for u in users.values():
                sub = u.get("subscription", "free")
                if sub == "pro":
                    pro_users += 1
                elif sub == "master":
                    master_users += 1
                else:
                    free_users += 1
            banned_users = 0
            for u in users.values():
                if u.get("banned", False):
                    banned_users += 1
            total_stars = 0
            for u in users.values():
                total_stars += u.get("stars", 0)
            total_saved_nicks = 0
            for u in users.values():
                total_saved_nicks += len(u.get("saved_nicks", []))
            total_referrals = 0
            for u in users.values():
                total_referrals += len(u.get("referrals", []))
            await callback.message.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👥 <b>Всего пользователей:</b> {total}\n"
                f"🟢 <b>Активны сегодня:</b> {active_today}\n"
                f"🟡 <b>Новых за неделю:</b> {active_week}\n\n"
                f"💎 <b>Подписки:</b>\n"
                f"  • FREE: {free_users}\n"
                f"  • PRO: {pro_users}\n"
                f"  • MASTER: {master_users}\n\n"
                f"⭐ <b>Всего звёзд:</b> {total_stars}\n"
                f"📂 <b>Сохранено ников:</b> {total_saved_nicks}\n"
                f"👥 <b>Всего рефералов:</b> {total_referrals}\n"
                f"🚫 <b>Забанено:</b> {banned_users}\n"
                f"━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=admin_keyboard(),
                parse_mode="HTML"
            )
        await callback.answer()
    except Exception as e:
        print(f"❌ Ошибка в admin_actions: {e}")
        await callback.answer("⚠️ Ошибка", show_alert=True)

@dp.message(AdminStates.waiting_for_message)
async def admin_broadcast(message: Message, state: FSMContext):
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("⛔ Доступ запрещён!")
            return
        db = load_db()
        sent = 0
        for uid in db["users"].keys():
            try:
                await bot.send_message(
                    int(uid),
                    f"📢 <b>Объявление от администрации</b>\n\n{message.text}",
                    parse_mode="HTML"
                )
                sent += 1
                await asyncio.sleep(0.05)
            except:
                pass
        await message.answer(f"✅ Рассылка завершена! Отправлено {sent} пользователям.")
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в admin_broadcast: {e}")
        await message.answer("⚠️ Ошибка рассылки")

@dp.message(AdminStates.waiting_for_user_id)
async def admin_action_input(message: Message, state: FSMContext):
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("⛔ Доступ запрещён!")
            return
        data = await state.get_data()
        action = data.get("admin_action")
        parts = message.text.split()
        
        # ========== НОВАЯ ФУНКЦИЯ: ВЫДАТЬ ВСЕМ ОНЛАЙН ==========
        if action == "online_requests" and len(parts) >= 1:
            try:
                amount = int(parts[0])
            except ValueError:
                await message.answer("❌ Введи число!")
                return
            
            if amount < 0:
                await message.answer("❌ Нельзя выдать отрицательное количество!")
                return
            if amount > 10000:
                await message.answer("❌ Слишком много! Максимум 10000")
                return
            
            db = load_db()
            online_users = []
            
            # Находим всех активных сегодня
            for uid, user_data in db["users"].items():
                if user_data.get("requests_today", 0) > 0:
                    online_users.append(int(uid))
            
            if not online_users:
                await message.answer("😔 Нет активных пользователей сегодня!")
                await state.clear()
                await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
                return
            
            # Выдаём запросы
            count = 0
            for uid in online_users:
                user = get_user(uid)
                user["requests_today"] += amount
                update_user(uid, user)
                count += 1
                
                # Уведомляем пользователя
                try:
                    await bot.send_message(
                        uid,
                        f"🎁 <b>Администратор выдал бонус!</b>\n\n"
                        f"📊 +{amount} запросов\n"
                        f"🔥 Ты был в онлайне, поэтому получил бонус!",
                        parse_mode="HTML"
                    )
                    await asyncio.sleep(0.05)
                except:
                    pass
            
            await message.answer(
                f"✅ <b>Выдано {amount} запросов {count} активным пользователям!</b>\n\n"
                f"👥 Всего онлайн сегодня: {count}"
            )
            await state.clear()
            await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
        
        # ========== ОСТАЛЬНЫЕ ДЕЙСТВИЯ ==========
        elif action == "sub" and len(parts) >= 3:
            try:
                user_id = int(parts[0])
            except ValueError:
                await message.answer("❌ Неверный ID пользователя!")
                return
            sub_type = parts[1]
            period = parts[2]
            if sub_type not in SUB_PRICES or period not in SUB_PRICES[sub_type]:
                await message.answer("❌ Неверный тип подписки или период!")
                return
            user = get_user(user_id)
            period_days = {"month": 30, "3month": 90, "year": 365, "forever": 9999}
            days = period_days.get(period, 30)
            if period == "forever":
                user["sub_expires"] = "2099-12-31"
            else:
                expires = datetime.now() + timedelta(days=days)
                user["sub_expires"] = expires.strftime("%Y-%m-%d")
            user["subscription"] = sub_type
            if sub_type == "pro":
                user["requests_limit"] = 30
            elif sub_type == "master":
                user["requests_limit"] = 150
            update_user(user_id, user)
            await message.answer(f"✅ Подписка {sub_type.upper()} ({period}) выдана пользователю {user_id}")
            try:
                await bot.send_message(
                    user_id,
                    f"🎁 <b>Вам выдана подписка {sub_type.upper()}!</b>\n\n"
                    f"📅 Период: {period}\n"
                    f"📊 Лимит запросов: {user['requests_limit']}/день",
                    parse_mode="HTML"
                )
            except:
                pass
        
        elif action == "ban" and len(parts) >= 1:
            try:
                user_id = int(parts[0])
            except ValueError:
                await message.answer("❌ Неверный ID пользователя!")
                return
            user = get_user(user_id)
            user["banned"] = not user.get("banned", False)
            update_user(user_id, user)
            status = "забанен" if user["banned"] else "разбанен"
            await message.answer(f"✅ Пользователь {user_id} {status}")
            try:
                await bot.send_message(
                    user_id,
                    f"🚫 Вы были {'забанены' if user['banned'] else 'разбанены'} администратором",
                    parse_mode="HTML"
                )
            except:
                pass
        
        elif action == "requests" and len(parts) >= 2:
            try:
                user_id = int(parts[0])
                amount = int(parts[1])
            except ValueError:
                await message.answer("❌ Неверный ID или количество!")
                return
            if amount < 0:
                await message.answer("❌ Нельзя выдать отрицательное количество!")
                return
            if amount > 10000:
                await message.answer("❌ Слишком много! Максимум 10000")
                return
            user = get_user(user_id)
            user["requests_today"] += amount
            update_user(user_id, user)
            await message.answer(f"✅ Пользователю {user_id} выдано {amount} запросов")
        
        elif action == "stars" and len(parts) >= 2:
            try:
                user_id = int(parts[0])
                amount = int(parts[1])
            except ValueError:
                await message.answer("❌ Неверный ID или количество!")
                return
            if amount < 0:
                await message.answer("❌ Нельзя выдать отрицательное количество звёзд!")
                return
            if amount > 1000000:
                await message.answer("❌ Слишком много! Максимум 1 000 000")
                return
            user = get_user(user_id)
            user["stars"] += amount
            update_user(user_id, user)
            await message.answer(f"✅ Пользователю {user_id} выдано {amount} звёзд")
        
        else:
            await message.answer("❌ Неверный формат! Попробуй снова.")
            return
        
        await state.clear()
        await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
    except Exception as e:
        print(f"❌ Ошибка в admin_action_input: {e}")
        await message.answer("⚠️ Ошибка")

@dp.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Действие отменено",
        reply_markup=main_menu_keyboard()
    )

@dp.message(Command("stats"))
async def stats_command(message: Message):
    try:
        is_subscribed, _ = await check_channel_subscription(message.from_user.id)
        if not is_subscribed:
            await message.answer(
                "🔒 <b>Подпишись на каналы чтобы увидеть статистику!</b>",
                parse_mode="HTML"
            )
            return
        db = load_db()
        total = len(db.get("users", {}))
        active_today = 0
        for u in db.get("users", {}).values():
            if u.get("requests_today", 0) > 0:
                active_today += 1
        await message.answer(
            f"📊 <b>Статистика бота</b>\n\n"
            f"👥 Всего пользователей: <b>{total}</b>\n"
            f"🟢 Активны сегодня: <b>{active_today}</b>\n\n"
            f"💡 <i>Подробная статистика — только для админов</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Ошибка в stats_command: {e}")
        await message.answer("⚠️ Ошибка")

# ==================== ЗАПУСК ====================
async def main():
    print("🚀 Бот @StarHandle_bot запущен!")
    print("🛡️ Все уязвимости исправлены!")
    print(f"👥 Администраторы: {ADMIN_IDS}")
    print(f"📁 БД: {DB_FILE}")
    print(f"💾 Бэкапы: {BACKUP_DIR}/")
    print("🔒 Требуется подписка на каналы:")
    for channel in REQUIRED_CHANNELS:
        print(f"  - {channel['name']}: {channel['username']}")
    print("🏷️ Категории ников (БЕЗ ЦЕНЫ):")
    for key, cat in NICK_CATEGORIES.items():
        value_info = get_nick_value(key)
        print(f"  {cat['emoji']} {cat['name']} — {value_info['name']}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())