import os
import asyncio
import json
import random
import string
import time
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

from aiohttp import web
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
from aiogram.exceptions import TelegramBadRequest

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

ADMIN_PASSWORD = "fgffhg6767"
ADMIN_IDS = [8024241408]
DB_FILE = "users.json"

REQUIRED_CHANNELS = [
    {"name": "StarHandle", "username": "@StarHandle_Chanell", "url": "https://t.me/StarHandle_Chanell"},
    {"name": "StarHandle Chat", "username": "@StarHandle_chat", "url": "https://t.me/StarHandle_chat"},
]

SUB_PRICES = {
    "pro": {"month": 15, "3month": 25, "year": 75},
    "master": {"month": 50, "3month": 75, "year": 130, "forever": 350},
}
STARS_PRICES = [10, 25, 50, 100, 250, 500, 1000]
SUPPORT_CONTACTS = ["@Zawkhaing794", "@CEPNAYA_KISLOTA"]

NICK_CATEGORIES = {
    "gamer": {
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
    "space": {
        "name": "🌌 Космический",
        "emoji": "🌌",
        "description": "Звёздные и космические",
        "value": "rare",
        "value_emoji": "🔵",
        "prefixes": ["astro", "cosmo", "galaxy", "nova", "star", "luna", "solar", "nebula", "quasar", "pulsar", "comet", "orbit", "aurora", "zenith", "eclipse", "stellar", "meteor", "asteroid", "supernova"],
        "suffixes": ["ar", "on", "is", "us", "um", "ia", "ox", "ix", "ux", "os", "an", "en", "in", "un"],
        "words": ["star", "moon", "sun", "planet", "galaxy", "cosmos", "void", "light", "shadow", "dark", "bright", "shine", "glow", "spark", "nova", "comet", "orbit", "nebula", "quasar"]
    },
    "premium": {
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

CATEGORY_LIST = ["gamer", "anime", "cyber", "space", "premium", "nature", "funny", "crypto"]

NICK_RARITY = {
    "common": {"name": "Обычный", "emoji": "🟢", "stars": 1},
    "uncommon": {"name": "Необычный", "emoji": "🟡", "stars": 2},
    "rare": {"name": "Редкий", "emoji": "🔵", "stars": 3},
    "epic": {"name": "Эпический", "emoji": "🟣", "stars": 4},
    "legendary": {"name": "Легендарный", "emoji": "🔴", "stars": 5}
}

user_last_action = defaultdict(float)

def check_flood(user_id, cooldown=2):
    now = time.time()
    if now - user_last_action[user_id] < cooldown:
        return False
    user_last_action[user_id] = now
    return True

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}, "total_stars": 0}
    return {"users": {}, "total_stars": 0}

def save_db(db):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"DB save error: {e}")

def get_user(user_id):
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
            "total_attempts": 0,
            "max_rarity_found": 0,
            "notify_list": []
        }
        save_db(db)
    return db["users"][uid]

def update_user(user_id, data):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        get_user(user_id)
    db["users"][uid].update(data)
    save_db(db)

def check_and_reset_requests(user_id):
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
        user["total_attempts"] = 0
        update_user(user_id, user)
    return user

def check_subscription(user_id):
    user = get_user(user_id)
    if user["subscription"] != "free" and user["sub_expires"]:
        try:
            expires = datetime.strptime(user["sub_expires"], "%Y-%m-%d")
            if expires < datetime.now():
                user["subscription"] = "free"
                user["requests_limit"] = 10
                user["sub_expires"] = ""
                update_user(user_id, user)
        except:
            pass
    return user

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_referral_link(user_id):
    user = get_user(user_id)
    if not user["referral_code"]:
        code = generate_referral_code()
        user["referral_code"] = code
        update_user(user_id, user)
    return f"https://t.me/StarHandle_bot?start={user['referral_code']}"

def calculate_rarity(username):
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

def get_nick_value(category):
    cat = NICK_CATEGORIES.get(category, {})
    value = cat.get("value", "common")
    return NICK_RARITY.get(value, NICK_RARITY["common"])

def generate_nick_by_category(category, length, gen_type):
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

async def check_channel_subscription(user_id):
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if chat_member.status in ["left", "kicked"]:
                not_subscribed.append(channel)
        except:
            not_subscribed.append(channel)
    return len(not_subscribed) == 0, not_subscribed

def get_subscription_keyboard(not_subscribed):
    buttons = []
    for channel in not_subscribed:
        buttons.append([InlineKeyboardButton(text=f"Подписаться на {channel['name']}", url=channel["url"])])
    buttons.append([InlineKeyboardButton(text="Я подписался! Проверить", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def require_subscription(func):
    @wraps(func)
    async def wrapper(callback, *args, **kwargs):
        is_subscribed, not_subscribed = await check_channel_subscription(callback.from_user.id)
        if not is_subscribed:
            try:
                await callback.message.delete()
            except:
                pass
            await callback.message.answer(
                "Для доступа подпишитесь на каналы",
                reply_markup=get_subscription_keyboard(not_subscribed)
            )
            await callback.answer()
            return
        return await func(callback, *args, **kwargs)
    return wrapper

async def check_username_telegram(username):
    try:
        chat = await bot.get_chat(f"@{username}")
        return False
    except TelegramBadRequest as e:
        if "not found" in str(e).lower():
            return True
        return True
    except:
        return True

class GeneratorStates(StatesGroup):
    choosing_category = State()
    choosing_count = State()
    choosing_length = State()
    choosing_type = State()

class AdminStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_user_id = State()

class PremiumStates(StatesGroup):
    waiting_mask = State()
    waiting_rarity = State()
    waiting_nick_for_notify = State()

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Поиск ников", callback_data="generator")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💎 Подписки", callback_data="subscriptions")],
        [InlineKeyboardButton(text="⭐ Донат", callback_data="donate")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="📂 Мои ники", callback_data="my_nicks")],
        [InlineKeyboardButton(text="🏆 Топ ников", callback_data="top_nicks")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="✨ Премиум-функции", callback_data="premium_features")],
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=types.WebAppInfo(url="https://starhandle.infinityfreeapp.com"))],
    ])

def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

def premium_features_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Поиск по маске", callback_data="premium_mask")],
        [InlineKeyboardButton(text="📊 Поиск по рейтингу", callback_data="premium_rarity")],
        [InlineKeyboardButton(text="🔔 Ловушка для ника", callback_data="premium_notify")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")],
    ])

def generator_category_keyboard():
    buttons = []
    row = []
    for cat_key in CATEGORY_LIST:
        cat = NICK_CATEGORIES[cat_key]
        value_info = get_nick_value(cat_key)
        row.append(InlineKeyboardButton(text=f"{cat['emoji']} {cat['name']} {value_info['emoji']}", callback_data=f"gen_cat_{cat_key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generator_count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="gen_count_1"), InlineKeyboardButton(text="5", callback_data="gen_count_5")],
        [InlineKeyboardButton(text="8", callback_data="gen_count_8"), InlineKeyboardButton(text="10", callback_data="gen_count_10")],
        [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="gen_back_category")],
    ])

def generator_length_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 букв", callback_data="gen_len_5"), InlineKeyboardButton(text="6 букв", callback_data="gen_len_6")],
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

def referral_keyboard(user_id):
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

def generated_nicks_keyboard(nicks=None):
    buttons = [[InlineKeyboardButton(text="🔄 Сгенерировать ещё", callback_data="generator")]]
    if nicks and len(nicks) > 0:
        buttons.append([InlineKeyboardButton(text="💾 Сохранить все ники", callback_data="save_nicks")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def my_nicks_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Очистить все", callback_data="clear_nicks")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message, state):
    try:
        await state.clear()
        user_id = message.from_user.id
        is_subscribed, not_subscribed = await check_channel_subscription(user_id)
        if not is_subscribed:
            await message.answer(
                "Добро пожаловать! Подпишитесь на каналы:",
                reply_markup=get_subscription_keyboard(not_subscribed)
            )
            return
        user = get_user(user_id)
        if user.get("banned"):
            await message.answer("Вы забанены.")
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
                        await message.answer("Реферальный код активирован! +3 запроса")
                    break
        user = get_user(user_id)
        user["username"] = message.from_user.username or ""
        user["first_name"] = message.from_user.first_name or ""
        update_user(user_id, user)
        await message.answer(
            f"🌟 StarHandle — поиск свободных ников\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {user['first_name']}\n"
            f"📦 Подписка: {user['subscription'].upper()}\n"
            f"📊 Запросов: {user['requests_today']}/{user['requests_limit']}\n"
            f"⭐ Баланс: {user['stars']} звёзд\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 Выберите действие:",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        print(f"Start error: {e}")
        await message.answer("Произошла ошибка.")

@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_handler(callback):
    user_id = callback.from_user.id
    is_subscribed, not_subscribed = await check_channel_subscription(user_id)
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Подписка подтверждена!",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            "❌ Вы подписались не на все каналы:",
            reply_markup=get_subscription_keyboard(not_subscribed)
        )
        await callback.answer()

@dp.callback_query(lambda c: c.data == "main_menu")
@require_subscription
async def main_menu(callback, state):
    try:
        await state.clear()
        user = get_user(callback.from_user.id)
        if user.get("banned"):
            await callback.message.delete()
            await callback.message.answer("Вы забанены.")
            await callback.answer()
            return
        await callback.message.edit_text(
            f"🌟 StarHandle — поиск свободных ников\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Пользователь: {user['first_name']}\n"
            f"📦 Подписка: {user['subscription'].upper()}\n"
            f"📊 Запросов: {user['requests_today']}/{user['requests_limit']}\n"
            f"⭐ Баланс: {user['stars']} звёзд\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 Выберите действие:",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Main menu error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "help")
@require_subscription
async def show_help(callback):
    try:
        await callback.message.edit_text(
            "❓ Помощь по боту\n\n"
            "1. Нажми «Поиск ников»\n"
            "2. Выбери категорию\n"
            "3. Выбери количество, длину и тип\n"
            "4. Получи список свободных ников!\n\n"
            "💎 Подписки:\n"
            "• FREE — 10 запросов/день\n"
            "• PRO — 30 запросов/день\n"
            "• MASTER — 150 запросов/день\n\n"
            "✨ Премиум-функции (доступны с PRO):\n"
            "• Поиск по маске (a?b?c → любые буквы)\n"
            "• Поиск по рейтингу (7/10–10/10)\n"
            "• Ловушка — уведомление когда ник освободится",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Help error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "premium_features")
@require_subscription
async def premium_features(callback):
    try:
        user = get_user(callback.from_user.id)
        if user["subscription"] == "free":
            await callback.message.edit_text(
                "✨ Премиум-функции\n\n"
                "Доступны только с подпиской PRO или MASTER!\n\n"
                "💎 PRO — 30 запросов/день\n"
                "👑 MASTER — 150 запросов/день\n\n"
                "Купи подписку в разделе «Подписки»",
                reply_markup=back_to_main_keyboard()
            )
            await callback.answer()
            return
        await callback.message.edit_text(
            "✨ Премиум-функции\n\n"
            "🎯 Поиск по маске — найди ники по шаблону (a?b?c → любые буквы)\n"
            "📊 Поиск по рейтингу — отфильтруй ники по редкости (7/10–10/10)\n"
            "🔔 Ловушка — получи уведомление, когда ник освободится\n\n"
            "Выберите функцию:",
            reply_markup=premium_features_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Premium features error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "premium_mask")
@require_subscription
async def premium_mask(callback, state):
    try:
        user = get_user(callback.from_user.id)
        if user["subscription"] == "free":
            await callback.answer("Только для PRO и MASTER!")
            return
        await state.set_state(PremiumStates.waiting_mask)
        await callback.message.edit_text(
            "🎯 Поиск по маске\n\n"
            "Введи шаблон ника:\n"
            "• ? — любая буква\n"
            "• * — любое количество букв\n\n"
            "Примеры:\n"
            "a?b?c — найдет 5-буквенные ники (например, a b c)\n"
            "p*r — найдет ники, начинающиеся на p и заканчивающиеся на r\n\n"
            "Отправь шаблон:",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Premium mask error: {e}")
        await callback.answer("Ошибка")

@dp.message(PremiumStates.waiting_mask)
async def process_premium_mask(message, state):
    try:
        user = get_user(message.from_user.id)
        if user["subscription"] == "free":
            await message.answer("Только для PRO и MASTER!")
            await state.clear()
            return
        mask = message.text.strip()
        if not mask or len(mask) > 20:
            await message.answer("Неверный формат. Попробуй снова.")
            return
        # Преобразуем маску в регулярное выражение
        import re
        pattern = mask.replace('?', '[a-zA-Z]').replace('*', '[a-zA-Z]*')
        # Генерируем варианты
        found = []
        for _ in range(50):
            nick = ''.join(random.choices(string.ascii_lowercase, k=len(mask.replace('*', '')) + random.randint(0, 3)))
            if re.match(pattern, nick):
                is_free = await check_username_telegram(nick)
                if is_free:
                    found.append(nick)
                    if len(found) >= 5:
                        break
        if found:
            await message.answer(
                f"🎯 Найдено по маске:\n\n" + "\n".join([f"@{n}" for n in found])
            )
        else:
            await message.answer("Не найдено ников по этой маске.")
        await state.clear()
    except Exception as e:
        print(f"Process mask error: {e}")
        await message.answer("Ошибка")
        await state.clear()

@dp.callback_query(lambda c: c.data == "premium_rarity")
@require_subscription
async def premium_rarity(callback, state):
    try:
        user = get_user(callback.from_user.id)
        if user["subscription"] == "free":
            await callback.answer("Только для PRO и MASTER!")
            return
        await state.set_state(PremiumStates.waiting_rarity)
        await callback.message.edit_text(
            "📊 Поиск по рейтингу\n\n"
            "Выбери минимальный рейтинг (от 1 до 10):\n"
            "• 7/10 — хорошие ники\n"
            "• 8/10 — редкие ники\n"
            "• 9/10 — очень редкие\n"
            "• 10/10 — легендарные\n\n"
            "Отправь число от 1 до 10:",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Premium rarity error: {e}")
        await callback.answer("Ошибка")

@dp.message(PremiumStates.waiting_rarity)
async def process_premium_rarity(message, state):
    try:
        user = get_user(message.from_user.id)
        if user["subscription"] == "free":
            await message.answer("Только для PRO и MASTER!")
            await state.clear()
            return
        try:
            min_rarity = int(message.text.strip())
            if min_rarity < 1 or min_rarity > 10:
                await message.answer("Введи число от 1 до 10!")
                return
        except:
            await message.answer("Введи число!")
            return
        found = []
        attempts = 0
        while len(found) < 5 and attempts < 50:
            attempts += 1
            nick = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            is_free = await check_username_telegram(nick)
            if is_free:
                rarity = calculate_rarity(nick)
                rating = rarity * 2
                if rating >= min_rarity:
                    found.append(f"@{nick} — {rating}/10 ⭐")
        if found:
            await message.answer(
                f"📊 Найдено ников с рейтингом {min_rarity}/10+:\n\n" + "\n".join(found)
            )
        else:
            await message.answer("Не найдено ников с таким рейтингом.")
        await state.clear()
    except Exception as e:
        print(f"Process rarity error: {e}")
        await message.answer("Ошибка")
        await state.clear()

@dp.callback_query(lambda c: c.data == "premium_notify")
@require_subscription
async def premium_notify(callback, state):
    try:
        user = get_user(callback.from_user.id)
        if user["subscription"] == "free":
            await callback.answer("Только для PRO и MASTER!")
            return
        await state.set_state(PremiumStates.waiting_nick_for_notify)
        await callback.message.edit_text(
            "🔔 Ловушка для ника\n\n"
            "Введи ник, за которым нужно следить:\n"
            "Пример: @myperfectnick\n\n"
            "Как только ник освободится — ты получишь уведомление!",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Premium notify error: {e}")
        await callback.answer("Ошибка")

@dp.message(PremiumStates.waiting_nick_for_notify)
async def process_premium_notify(message, state):
    try:
        user = get_user(message.from_user.id)
        if user["subscription"] == "free":
            await message.answer("Только для PRO и MASTER!")
            await state.clear()
            return
        nick = message.text.strip().replace('@', '')
        if not nick or len(nick) < 3:
            await message.answer("Введи корректный ник (минимум 3 символа)")
            return
        user["notify_list"].append(nick)
        update_user(message.from_user.id, user)
        await message.answer(
            f"🔔 Ловушка для @{nick} активирована!\n\n"
            f"Ты получишь уведомление, когда ник освободится."
        )
        await state.clear()
    except Exception as e:
        print(f"Process notify error: {e}")
        await message.answer("Ошибка")
        await state.clear()

@dp.callback_query(lambda c: c.data == "generator")
@require_subscription
async def start_generator(callback, state):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("Подожди 2 секунды!")
            return
        user = check_and_reset_requests(callback.from_user.id)
        user = check_subscription(callback.from_user.id)
        if user.get("banned"):
            await callback.answer("Вы забанены!")
            return
        if user["requests_today"] >= user["requests_limit"]:
            await callback.message.edit_text(
                "❌ Лимит запросов исчерпан!\n\n"
                "Купи подписку, чтобы увеличить лимит:\n"
                "• PRO — 30 запросов/день\n"
                "• MASTER — 150 запросов/день\n\n"
                "💎 Нажми «Подписки» в меню",
                reply_markup=main_menu_keyboard()
            )
            await callback.answer()
            return
        await state.set_state(GeneratorStates.choosing_category)
        await callback.message.edit_text(
            "🎯 Выбери категорию:",
            reply_markup=generator_category_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Generator start error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(GeneratorStates.choosing_category, lambda c: c.data.startswith("gen_cat_"))
@require_subscription
async def choose_category(callback, state):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("Подожди 2 секунды!")
            return
        category = callback.data.split("_")[2]
        if category not in NICK_CATEGORIES:
            await callback.answer("Неверная категория!")
            return
        await state.update_data(category=category)
        await state.set_state(GeneratorStates.choosing_count)
        await callback.message.edit_text(
            "📦 Выбери количество:",
            reply_markup=generator_count_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Choose category error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(GeneratorStates.choosing_count, lambda c: c.data.startswith("gen_count_"))
@require_subscription
async def choose_count(callback, state):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("Подожди 2 секунды!")
            return
        count = int(callback.data.split("_")[2])
        if count not in [1, 5, 8, 10]:
            await callback.answer("Выбери 1, 5, 8 или 10!")
            return
        await state.update_data(count=count)
        await state.set_state(GeneratorStates.choosing_length)
        await callback.message.edit_text(
            "📏 Выбери длину:",
            reply_markup=generator_length_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Choose count error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(GeneratorStates.choosing_length, lambda c: c.data.startswith("gen_len_"))
@require_subscription
async def choose_length(callback, state):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("Подожди 2 секунды!")
            return
        length = int(callback.data.split("_")[2])
        if length not in [5, 6]:
            await callback.answer("Выбери 5 или 6!")
            return
        await state.update_data(length=length)
        await state.set_state(GeneratorStates.choosing_type)
        await callback.message.edit_text(
            "🔤 Выбери тип символов:",
            reply_markup=generator_type_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Choose length error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(GeneratorStates.choosing_type, lambda c: c.data.startswith("gen_type_"))
@require_subscription
async def choose_type(callback, state):
    try:
        if not check_flood(callback.from_user.id):
            await callback.answer("Подожди 2 секунды!")
            return
        gen_type = callback.data.split("_")[2]
        if gen_type not in ["digits", "mixed", "letters"]:
            await callback.answer("Неверный тип!")
            return
        data = await state.get_data()
        count = data.get("count", 5)
        length = data.get("length", 5)
        category = data.get("category", "gamer")
        user_id = callback.from_user.id
        user = get_user(user_id)
        user = check_and_reset_requests(user_id)
        if user["requests_today"] >= user["requests_limit"]:
            await callback.message.edit_text(
                "❌ Лимит запросов исчерпан!",
                reply_markup=main_menu_keyboard()
            )
            await callback.answer()
            return
        if count > 10:
            count = 10
        await callback.message.edit_text(
            "⏳ Идёт поиск свободных ников...",
            reply_markup=None
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
        user["total_attempts"] = user.get("total_attempts", 0) + 1
        if found_nicks:
            max_rarity = max([n["rarity"] for n in found_nicks])
            if max_rarity > user["max_rarity_found"]:
                user["max_rarity_found"] = max_rarity
        update_user(user_id, user)
        if not found_nicks:
            await callback.message.edit_text(
                "😔 Не найдено свободных ников.\n\n"
                "Попробуй изменить параметры:\n"
                "• Увеличь длину\n"
                "• Выбери другой тип символов\n"
                "• Выбери другую категорию",
                reply_markup=generated_nicks_keyboard()
            )
            await state.clear()
            return
        await state.update_data(found_nicks=found_nicks)
        cat_name = ""
        if category and category in NICK_CATEGORIES:
            cat_name = f" ({NICK_CATEGORIES[category]['emoji']} {NICK_CATEGORIES[category]['name']})"
        result_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"✨ Найдены свободные ники{cat_name}!\n"
        result_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, item in enumerate(found_nicks, 1):
            stars = "⭐" * item["rarity"] + "☆" * (5 - item["rarity"])
            result_text += f"{i}. @{item['nick']} {stars} {item['emoji']} {item['value']}\n"
        result_text += "\n━━━━━━━━━━━━━━━━━━━━━\n"
        result_text += f"🔥 Осталось запросов: {user['requests_today']}/{user['requests_limit']}"
        await callback.message.edit_text(
            result_text,
            reply_markup=generated_nicks_keyboard(found_nicks)
        )
        await callback.answer()
    except Exception as e:
        print(f"Choose type error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "gen_back_category")
@require_subscription
async def back_to_category(callback, state):
    try:
        await state.set_state(GeneratorStates.choosing_category)
        await callback.message.edit_text(
            "🎯 Выбери категорию:",
            reply_markup=generator_category_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Back to category error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "gen_back_count")
@require_subscription
async def back_to_count(callback, state):
    try:
        await state.set_state(GeneratorStates.choosing_count)
        await callback.message.edit_text(
            "📦 Выбери количество:",
            reply_markup=generator_count_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Back to count error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "gen_back_length")
@require_subscription
async def back_to_length(callback, state):
    try:
        await state.set_state(GeneratorStates.choosing_length)
        await callback.message.edit_text(
            "📏 Выбери длину:",
            reply_markup=generator_length_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Back to length error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "save_nicks")
@require_subscription
async def save_nicks(callback, state):
    try:
        data = await state.get_data()
        found_nicks = data.get("found_nicks", [])
        if not found_nicks:
            await callback.answer("Нет ников для сохранения!")
            return
        user = get_user(callback.from_user.id)
        saved = user.get("saved_nicks", [])
        if len(saved) >= 100:
            await callback.answer("Максимум 100 ников!")
            return
        for item in found_nicks:
            if item["nick"] not in saved:
                saved.append(item["nick"])
        user["saved_nicks"] = saved
        update_user(callback.from_user.id, user)
        await callback.answer(f"Сохранено {len(found_nicks)} ников!")
        await callback.message.edit_text(
            f"✅ Ники сохранены!\n\n"
            f"📂 Всего сохранено: {len(saved)} ников",
            reply_markup=back_to_main_keyboard()
        )
        await state.clear()
    except Exception as e:
        print(f"Save nicks error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "my_nicks")
@require_subscription
async def my_nicks(callback):
    try:
        user = get_user(callback.from_user.id)
        saved_nicks = user.get("saved_nicks", [])
        if not saved_nicks:
            await callback.message.edit_text(
                "📭 У тебя пока нет сохранённых ников",
                reply_markup=back_to_main_keyboard()
            )
            await callback.answer()
            return
        nicks_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        nicks_text += "📂 Твои сохранённые ники\n"
        nicks_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, nick in enumerate(saved_nicks, 1):
            rarity = calculate_rarity(nick)
            stars = "⭐" * rarity + "☆" * (5 - rarity)
            nicks_text += f"{i}. @{nick} {stars}\n"
        nicks_text += f"\n📊 Всего: {len(saved_nicks)} ников"
        await callback.message.edit_text(
            nicks_text,
            reply_markup=my_nicks_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"My nicks error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "clear_nicks")
@require_subscription
async def clear_nicks(callback):
    try:
        user = get_user(callback.from_user.id)
        user["saved_nicks"] = []
        update_user(callback.from_user.id, user)
        await callback.message.edit_text(
            "🗑 Все сохранённые ники удалены",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Clear nicks error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "top_nicks")
@require_subscription
async def top_nicks(callback):
    try:
        db = load_db()
        all_nicks = []
        for uid, data in db["users"].items():
            for nick in data.get("saved_nicks", []):
                rarity = calculate_rarity(nick)
                all_nicks.append({"nick": nick, "rarity": rarity})
        if not all_nicks:
            await callback.message.edit_text(
                "🏆 Топ редких ников\n\n"
                "😔 Пока никто не сохранил ни одного ника...\n"
                "💡 Будь первым!",
                reply_markup=back_to_main_keyboard()
            )
            await callback.answer()
            return
        all_nicks.sort(key=lambda x: x["rarity"], reverse=True)
        top_nicks = all_nicks[:10]
        top_text = "━━━━━━━━━━━━━━━━━━━━━\n"
        top_text += "🏆 Топ редких ников\n"
        top_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, item in enumerate(top_nicks, 1):
            stars = "⭐" * item["rarity"] + "☆" * (5 - item["rarity"])
            top_text += f"{i}. @{item['nick']} {stars}\n"
        top_text += f"\n📊 Всего в базе: {len(all_nicks)} ников"
        await callback.message.edit_text(
            top_text,
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Top nicks error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "profile")
@require_subscription
async def show_profile(callback):
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
            f"👤 Твой профиль\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📛 Имя: {user['first_name']}\n"
            f"🆔 UID: <code>{user_id}</code>\n"
            f"⭐ Баланс: {user['stars']} звёзд\n"
            f"🏆 Репутация: {user['reputation']}\n"
            f"📦 Подписка: {sub_text}\n"
            f"📊 Запросов сегодня: {user['requests_today']}/{user['requests_limit']}\n"
            f"👥 Рефералов: {len(user['referrals'])}\n"
            f"📂 Сохранено ников: {len(user.get('saved_nicks', []))}\n"
            f"✨ Макс. редкость: {user.get('max_rarity_found', 0)}⭐\n"
            f"📅 В системе: {user['created_at']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        await callback.message.edit_text(
            profile_text,
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Profile error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "subscriptions")
@require_subscription
async def show_subscriptions(callback):
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
            f"💎 Доступные подписки\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆓 FREE — 10 запросов/день (бесплатно)\n\n"
            f"⭐ PRO — 30 запросов/день\n"
            f"  ▫️ 1 месяц — 15 ⭐\n"
            f"  ▫️ 3 месяца — 25 ⭐\n"
            f"  ▫️ 1 год — 75 ⭐\n\n"
            f"👑 MASTER — 150 запросов/день\n"
            f"  ▫️ 1 месяц — 50 ⭐\n"
            f"  ▫️ 3 месяца — 75 ⭐\n"
            f"  ▫️ 1 год — 130 ⭐\n"
            f"  ▫️ НАВСЕГДА — 350 ⭐\n\n"
            f"✨ Премиум-функции PRO:\n"
            f"• Поиск по маске\n"
            f"• Поиск по рейтингу\n"
            f"• Ловушка для ников\n\n"
            f"📌 Твоя подписка: {sub_text}",
            reply_markup=subscriptions_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Subscriptions error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data.startswith("buy_"))
@require_subscription
async def buy_subscription(callback):
    try:
        data = callback.data.split("_")
        sub_type = data[1]
        period = data[2]
        user = get_user(callback.from_user.id)
        if sub_type not in SUB_PRICES or period not in SUB_PRICES[sub_type]:
            await callback.answer("Неверный тип подписки")
            return
        cost = SUB_PRICES[sub_type][period]
        if user["stars"] < cost:
            await callback.answer(f"Не хватает звёзд! Нужно {cost} ⭐, у тебя {user['stars']} ⭐")
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
            f"✅ Подписка {sub_type.upper()} активирована!\n\n"
            f"📅 Период: {period}\n"
            f"⭐ Снято: {cost} звёзд\n"
            f"💰 Остаток: {user['stars']} ⭐\n\n"
            f"📊 Лимит запросов: {user['requests_limit']}/день\n"
            f"✨ Премиум-функции разблокированы!",
            reply_markup=subscriptions_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Buy subscription error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "donate")
@require_subscription
async def show_donate(callback):
    try:
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ Пополнить звёзды\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Выбери сумму для пополнения:\n"
            f"💰 Оплата через Telegram Stars\n\n"
            f"💡 Курс: 1 ⭐ ≈ 1 ₽\n"
            f"⚡ Звёзды зачисляются мгновенно",
            reply_markup=donate_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Donate error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data.startswith("donate_"))
@require_subscription
async def process_donate(callback):
    try:
        amount = int(callback.data.split("_")[1])
        if amount not in STARS_PRICES:
            await callback.answer("Неверная сумма!")
            return
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"Пополнение на {amount}⭐",
            description=f"Пополнение баланса StarHandle на {amount} звёзд",
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
        print(f"Process donate error: {e}")
        await callback.answer("Ошибка")

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout):
    try:
        await pre_checkout.bot.answer_pre_checkout_query(pre_checkout.id, ok=True)
    except Exception as e:
        print(f"Pre checkout error: {e}")

@dp.message(lambda msg: msg.successful_payment)
async def process_successful_payment(message):
    try:
        payload = message.successful_payment.invoice_payload
        parts = payload.split("_")
        amount = int(parts[1])
        user_id = int(parts[2]) if len(parts) > 2 else message.from_user.id
        if user_id != message.from_user.id:
            await message.answer("Ошибка оплаты!")
            return
        user = get_user(user_id)
        user["stars"] += amount
        update_user(user_id, user)
        await message.answer(
            f"✅ Пополнение успешно!\n\n"
            f"⭐ Зачислено: {amount} звёзд\n"
            f"💰 Твой баланс: {user['stars']} ⭐\n\n"
            f"💎 Теперь ты можешь купить подписку в разделе «Подписки»",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        print(f"Successful payment error: {e}")
        await message.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "referrals")
@require_subscription
async def show_referrals(callback):
    try:
        user_id = callback.from_user.id
        user = get_user(user_id)
        link = get_referral_link(user_id)
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Реферальная система\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 Приглашай друзей и получай бонусы!\n\n"
            f"🔗 Твоя ссылка:\n"
            f"<code>{link}</code>\n\n"
            f"📊 Твоя статистика:\n"
            f"• Приглашено: {len(user['referrals'])} чел.\n"
            f"• Бонус: +3 запроса за каждого реферала\n\n"
            f"🔥 Чем больше друзей — тем больше возможностей!",
            reply_markup=referral_keyboard(user_id)
        )
        await callback.answer()
    except Exception as e:
        print(f"Referrals error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data.startswith("copy_ref_"))
@require_subscription
async def copy_referral(callback):
    try:
        user_id = int(callback.data.split("_")[2])
        link = get_referral_link(user_id)
        await callback.answer(f"📋 {link}")
    except Exception as e:
        print(f"Copy referral error: {e}")
        await callback.answer("Ошибка")

@dp.callback_query(lambda c: c.data == "support")
@require_subscription
async def show_support(callback):
    try:
        await callback.message.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📞 Техническая поддержка\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❓ Возникли вопросы или проблемы?\n\n"
            f"📩 Наши контакты:\n"
            f"• {SUPPORT_CONTACTS[0]}\n"
            f"• {SUPPORT_CONTACTS[1]}\n\n"
            f"⏰ Время ответа: обычно 5-15 минут\n"
            f"💬 Пишите чётко и подробно",
            reply_markup=support_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Support error: {e}")
        await callback.answer("Ошибка")

@dp.message(Command("adminpassword"))
async def admin_login(message):
    try:
        args = message.text.split()
        if len(args) > 1 and args[1] == ADMIN_PASSWORD:
            if message.from_user.id not in ADMIN_IDS:
                await message.answer("Доступ запрещён!")
                return
            await message.answer(
                "🔐 Добро пожаловать в админ-панель!",
                reply_markup=admin_keyboard()
            )
        else:
            await message.answer("Неверный пароль!")
    except Exception as e:
        print(f"Admin login error: {e}")
        await message.answer("Ошибка")

@dp.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_actions(callback, state):
    try:
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("Доступ запрещён!")
            return
        action = callback.data.split("_")[1]
        if action == "broadcast":
            await state.set_state(AdminStates.waiting_for_message)
            await callback.message.edit_text(
                "📢 Рассылка\n\n"
                "Отправь сообщение для рассылки всем пользователям.\n"
                "Для отмены напиши /cancel"
            )
        elif action == "sub":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="sub")
            await callback.message.edit_text(
                "🎁 Выдача подписки\n\n"
                "Введи ID пользователя и тип подписки через пробел:\n"
                "<code>123456789 pro month</code>\n"
                "или <code>123456789 master forever</code>\n\n"
                "Доступные типы: pro, master\n"
                "Доступные периоды: month, 3month, year, forever"
            )
        elif action == "ban":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="ban")
            await callback.message.edit_text(
                "🚫 Бан пользователя\n\n"
                "Введи ID пользователя для бана/разбана:\n"
                "<code>123456789</code>"
            )
        elif action == "requests":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="requests")
            await callback.message.edit_text(
                "📊 Выдача запросов\n\n"
                "Введи ID пользователя и количество запросов через пробел:\n"
                "<code>123456789 50</code>"
            )
        elif action == "stars":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="stars")
            await callback.message.edit_text(
                "⭐ Выдача звёзд\n\n"
                "Введи ID пользователя и количество звёзд через пробел:\n"
                "<code>123456789 100</code>"
            )
        elif action == "online_requests":
            await state.set_state(AdminStates.waiting_for_user_id)
            await state.update_data(admin_action="online_requests")
            await callback.message.edit_text(
                "🟢 Выдача запросов ВСЕМ ОНЛАЙН\n\n"
                "Введи количество запросов для всех активных сегодня пользователей:\n"
                "<code>10</code>"
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
                if u.get("banned"):
                    banned_users += 1
                total_saved_nicks += len(u.get("saved_nicks", []))
            await callback.message.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 СТАТИСТИКА БОТА\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👥 Всего пользователей: {total_users}\n"
                f"⭐ Всего звёзд: {total_stars}\n"
                f"💎 PRO подписок: {pro_users}\n"
                f"👑 MASTER подписок: {master_users}\n"
                f"📂 Сохранено ников: {total_saved_nicks}\n"
                f"🚫 Забанено: {banned_users}\n"
                f"━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=admin_keyboard()
            )
        elif action == "user_stats":
            db = load_db()
            users = db.get("users", {})
            total = len(users)
            if total == 0:
                await callback.message.edit_text(
                    "📊 Статистика пользователей\n\n"
                    "😔 Пока нет пользователей",
                    reply_markup=admin_keyboard()
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
                    created = datetime.strptime(u.get("created_at", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
                    if created > week_ago:
                        active_week += 1
                except:
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
                if u.get("banned"):
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
                f"📊 СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👥 Всего пользователей: {total}\n"
                f"🟢 Активны сегодня: {active_today}\n"
                f"🟡 Новых за неделю: {active_week}\n\n"
                f"💎 Подписки:\n"
                f"  • FREE: {free_users}\n"
                f"  • PRO: {pro_users}\n"
                f"  • MASTER: {master_users}\n\n"
                f"⭐ Всего звёзд: {total_stars}\n"
                f"📂 Сохранено ников: {total_saved_nicks}\n"
                f"👥 Всего рефералов: {total_referrals}\n"
                f"🚫 Забанено: {banned_users}\n"
                f"━━━━━━━━━━━━━━━━━━━━━",
                reply_markup=admin_keyboard()
            )
        await callback.answer()
    except Exception as e:
        print(f"Admin actions error: {e}")
        await callback.answer("Ошибка")

@dp.message(AdminStates.waiting_for_message)
async def admin_broadcast(message, state):
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("Доступ запрещён!")
            return
        db = load_db()
        sent = 0
        for uid in db["users"].keys():
            try:
                await bot.send_message(int(uid), f"📢 Объявление от администрации\n\n{message.text}")
                sent += 1
                await asyncio.sleep(0.05)
            except:
                pass
        await message.answer(f"✅ Рассылка завершена! Отправлено {sent} пользователям.")
        await state.clear()
    except Exception as e:
        print(f"Admin broadcast error: {e}")
        await message.answer("Ошибка")

@dp.message(AdminStates.waiting_for_user_id)
async def admin_action_input(message, state):
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("Доступ запрещён!")
            return
        data = await state.get_data()
        action = data.get("admin_action")
        parts = message.text.split()
        if action == "online_requests" and len(parts) >= 1:
            try:
                amount = int(parts[0])
            except:
                await message.answer("Введи число!")
                return
            if amount < 0 or amount > 10000:
                await message.answer("Введи число от 0 до 10000")
                return
            db = load_db()
            online_users = []
            for uid, user_data in db["users"].items():
                if user_data.get("requests_today", 0) > 0:
                    online_users.append(int(uid))
            if not online_users:
                await message.answer("Нет активных пользователей сегодня!")
                await state.clear()
                await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
                return
            count = 0
            for uid in online_users:
                user = get_user(uid)
                user["requests_today"] += amount
                update_user(uid, user)
                count += 1
                try:
                    await bot.send_message(uid, f"🎁 Администратор выдал бонус!\n\n📊 +{amount} запросов")
                    await asyncio.sleep(0.05)
                except:
                    pass
            await message.answer(f"✅ Выдано {amount} запросов {count} активным пользователям!")
            await state.clear()
            await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
        elif action == "sub" and len(parts) >= 3:
            try:
                user_id = int(parts[0])
            except:
                await message.answer("Неверный ID!")
                return
            sub_type = parts[1]
            period = parts[2]
            if sub_type not in SUB_PRICES or period not in SUB_PRICES[sub_type]:
                await message.answer("Неверный тип или период!")
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
                await bot.send_message(user_id, f"🎁 Вам выдана подписка {sub_type.upper()}!\n\n📅 Период: {period}\n📊 Лимит: {user['requests_limit']}/день")
            except:
                pass
        elif action == "ban" and len(parts) >= 1:
            try:
                user_id = int(parts[0])
            except:
                await message.answer("Неверный ID!")
                return
            user = get_user(user_id)
            user["banned"] = not user.get("banned", False)
            update_user(user_id, user)
            status = "забанен" if user["banned"] else "разбанен"
            await message.answer(f"✅ Пользователь {user_id} {status}")
            try:
                await bot.send_message(user_id, f"🚫 Вы были {status} администратором")
            except:
                pass
        elif action == "requests" and len(parts) >= 2:
            try:
                user_id = int(parts[0])
                amount = int(parts[1])
            except:
                await message.answer("Неверный ID или количество!")
                return
            if amount < 0 or amount > 10000:
                await message.answer("Введи число от 0 до 10000")
                return
            user = get_user(user_id)
            user["requests_today"] += amount
            update_user(user_id, user)
            await message.answer(f"✅ Пользователю {user_id} выдано {amount} запросов")
        elif action == "stars" and len(parts) >= 2:
            try:
                user_id = int(parts[0])
                amount = int(parts[1])
            except:
                await message.answer("Неверный ID или количество!")
                return
            if amount < 0 or amount > 1000000:
                await message.answer("Введи число от 0 до 1 000 000")
                return
            user = get_user(user_id)
            user["stars"] += amount
            update_user(user_id, user)
            await message.answer(f"✅ Пользователю {user_id} выдано {amount} звёзд")
        else:
            await message.answer("Неверный формат!")
            return
        await state.clear()
        await message.answer("🔐 Админ-панель:", reply_markup=admin_keyboard())
    except Exception as e:
        print(f"Admin action input error: {e}")
        await message.answer("Ошибка")

@dp.message(Command("cancel"))
async def cancel_command(message, state):
    await state.clear()
    await message.answer("❌ Действие отменено", reply_markup=main_menu_keyboard())

@dp.message(Command("stats"))
async def stats_command(message):
    try:
        is_subscribed, _ = await check_channel_subscription(message.from_user.id)
        if not is_subscribed:
            await message.answer("Подпишись на каналы чтобы увидеть статистику!")
            return
        db = load_db()
        total = len(db.get("users", {}))
        active_today = 0
        for u in db.get("users", {}).values():
            if u.get("requests_today", 0) > 0:
                active_today += 1
        await message.answer(
            f"📊 Статистика бота\n\n"
            f"👥 Всего пользователей: {total}\n"
            f"🟢 Активны сегодня: {active_today}\n\n"
            f"💡 Подробная статистика — только для админов"
        )
    except Exception as e:
        print(f"Stats command error: {e}")
        await message.answer("Ошибка")

@dp.message()
async def web_app_handler(message: Message):
    if not message.web_app_data:
        return
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        user_id = message.from_user.id
        user = get_user(user_id)
        if action == "getProfile":
            response = {
                "id": user_id,
                "first_name": message.from_user.first_name or "",
                "stars": user["stars"],
                "subscription": user["subscription"],
                "requests_today": user["requests_today"],
                "requests_limit": user["requests_limit"],
                "reputation": user["reputation"],
                "referrals": len(user.get("referrals", [])),
                "saved_nicks": user.get("saved_nicks", [])
            }
            await message.answer(json.dumps(response))
        elif action == "generate":
            category = data.get("category", "gamer")
            count = data.get("count", 5)
            length = data.get("length", 6)
            gen_type = data.get("type", "mixed")
            user = check_and_reset_requests(user_id)
            if user["requests_today"] >= user["requests_limit"]:
                await message.answer(json.dumps({"error": "Лимит запросов исчерпан!"}))
                return
            found_nicks = []
            checked = 0
            max_attempts = count * 5
            while len(found_nicks) < count and checked < max_attempts:
                checked += 1
                if gen_type == "digits":
                    nick = ''.join(random.choices(string.digits, k=length))
                elif gen_type == "letters":
                    nick = ''.join(random.choices(string.ascii_lowercase, k=length))
                else:
                    nick = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
                is_free = await check_username_telegram(nick)
                if is_free:
                    rarity = calculate_rarity(nick)
                    value_info = get_nick_value(category)
                    found_nicks.append({"nick": nick, "rarity": rarity, "value": value_info["name"]})
            user["requests_today"] += count
            update_user(user_id, user)
            await message.answer(json.dumps({"nicks": found_nicks}))
        elif action == "saveNicks":
            nicks = data.get("nicks", [])
            saved = user.get("saved_nicks", [])
            for nick in nicks:
                if nick not in saved:
                    saved.append(nick)
            user["saved_nicks"] = saved
            update_user(user_id, user)
            await message.answer(json.dumps({"success": True, "saved": len(nicks)}))
        elif action == "buySubscription":
            plan = data.get("plan", "pro")
            period = data.get("period", "month")
            price = data.get("price", 15)
            if user["stars"] < price:
                await message.answer(json.dumps({"error": f"Не хватает звёзд! Нужно {price}⭐"}))
                return
            user["stars"] -= price
            period_days = {"month": 30, "year": 365, "forever": 9999}
            days = period_days.get(period, 30)
            if period == "forever":
                user["sub_expires"] = "2099-12-31"
            else:
                expires = datetime.now() + timedelta(days=days)
                user["sub_expires"] = expires.strftime("%Y-%m-%d")
            user["subscription"] = plan
            if plan == "pro":
                user["requests_limit"] = 30
            elif plan == "master":
                user["requests_limit"] = 150
            update_user(user_id, user)
            await message.answer(json.dumps({"success": True, "plan": plan, "stars_left": user["stars"]}))
        elif action == "donate":
            amount = data.get("amount", 10)
            await bot.send_invoice(
                chat_id=user_id,
                title=f"Пополнение на {amount}⭐",
                description=f"Пополнение баланса StarHandle на {amount} звёзд",
                payload=f"donate_{amount}_{user_id}",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(label=f"{amount} звёзд", amount=amount)],
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                is_flexible=False,
            )
        elif action == "buyRequests":
            amount = data.get("amount", 10)
            price = data.get("price", 5)
            if user["stars"] < price:
                await message.answer(json.dumps({"error": f"Не хватает звёзд! Нужно {price}⭐"}))
                return
            user["stars"] -= price
            user["requests_today"] -= amount
            if user["requests_today"] < 0:
                user["requests_today"] = 0
            update_user(user_id, user)
            await message.answer(json.dumps({"success": True, "added": amount, "stars_left": user["stars"]}))
        elif action == "getTop":
            db = load_db()
            top_users = []
            for uid, data in db["users"].items():
                top_users.append({"id": int(uid), "name": data.get("first_name", "Аноним"), "count": len(data.get("saved_nicks", []))})
            top_users.sort(key=lambda x: x["count"], reverse=True)
            top_users = top_users[:10]
            for u in top_users:
                if u["id"] == user_id:
                    u["isMe"] = True
                else:
                    u["isMe"] = False
            await message.answer(json.dumps({"top": top_users}))
        else:
            await message.answer(json.dumps({"error": f"Неизвестное действие: {action}"}))
    except Exception as e:
        print(f"Web app handler error: {e}")
        await message.answer(json.dumps({"error": str(e)}))

async def start_web_server():
    app = web.Application()
    async def health_check(request):
        return web.Response(text="OK", status=200)
    app.router.add_get('/', health_check)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    await asyncio.Event().wait()

async def main():
    print("Bot started")
    await asyncio.gather(
        dp.start_polling(bot),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
