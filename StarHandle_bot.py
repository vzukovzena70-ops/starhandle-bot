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

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Генератор", callback_data="generator")],
        [InlineKeyboardButton(text="Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="Подписки", callback_data="subscriptions")],
        [InlineKeyboardButton(text="Донат", callback_data="donate")],
        [InlineKeyboardButton(text="Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="Мои ники", callback_data="my_nicks")],
        [InlineKeyboardButton(text="Топ ников", callback_data="top_nicks")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Открыть приложение", web_app=types.WebAppInfo(url="https://starhandle.infinityfreeapp.com"))],
    ])

def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
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
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generator_count_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="gen_count_1"), InlineKeyboardButton(text="5", callback_data="gen_count_5")],
        [InlineKeyboardButton(text="8", callback_data="gen_count_8"), InlineKeyboardButton(text="10", callback_data="gen_count_10")],
        [InlineKeyboardButton(text="Назад к категориям", callback_data="gen_back_category")],
    ])

def generator_length_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 букв", callback_data="gen_len_5"), InlineKeyboardButton(text="6 букв", callback_data="gen_len_6")],
        [InlineKeyboardButton(text="Назад к количеству", callback_data="gen_back_count")],
    ])

def generator_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Только цифры", callback_data="gen_type_digits")],
        [InlineKeyboardButton(text="Буквы + цифры", callback_data="gen_type_mixed")],
        [InlineKeyboardButton(text="Только буквы", callback_data="gen_type_letters")],
        [InlineKeyboardButton(text="Назад к длине", callback_data="gen_back_length")],
    ])

def subscriptions_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="PRO — 1 месяц (15⭐)", callback_data="buy_pro_month")],
        [InlineKeyboardButton(text="PRO — 3 месяца (25⭐)", callback_data="buy_pro_3month")],
        [InlineKeyboardButton(text="PRO — 1 год (75⭐)", callback_data="buy_pro_year")],
        [InlineKeyboardButton(text="MASTER — 1 месяц (50⭐)", callback_data="buy_master_month")],
        [InlineKeyboardButton(text="MASTER — 3 месяца (75⭐)", callback_data="buy_master_3month")],
        [InlineKeyboardButton(text="MASTER — 1 год (130⭐)", callback_data="buy_master_year")],
        [InlineKeyboardButton(text="MASTER — НАВСЕГДА (350⭐)", callback_data="buy_master_forever")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")],
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
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def referral_keyboard(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скопировать ссылку", callback_data=f"copy_ref_{user_id}")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")],
    ])

def support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать @Zawkhaing794", url="https://t.me/Zawkhaing794")],
        [InlineKeyboardButton(text="Написать @CEPNAYA_KISLOTA", url="https://t.me/CEPNAYA_KISLOTA")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")],
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="Выдать подписку", callback_data="admin_sub")],
        [InlineKeyboardButton(text="Бан/Разбан", callback_data="admin_ban")],
        [InlineKeyboardButton(text="Выдать запросы", callback_data="admin_requests")],
        [InlineKeyboardButton(text="Выдать звёзды", callback_data="admin_stars")],
        [InlineKeyboardButton(text="Выдать запросы ОНЛАЙН", callback_data="admin_online_requests")],
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Статистика пользователей", callback_data="user_stats")],
        [InlineKeyboardButton(text="Выйти из админки", callback_data="main_menu")],
    ])

def generated_nicks_keyboard(nicks=None):
    buttons = [[InlineKeyboardButton(text="Сгенерировать ещё", callback_data="generator")]]
    if nicks and len(nicks) > 0:
        buttons.append([InlineKeyboardButton(text="Сохранить все ники", callback_data="save_nicks")])
    buttons.append([InlineKeyboardButton(text="Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def my_nicks_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Очистить все", callback_data="clear_nicks")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
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
            f"Добро пожаловать в StarHandle!\n\nПодписка: {user['subscription'].upper()}\nЗапросов: {user['requests_today']}/{user['requests_limit']}\nБаланс: {user['stars']} звёзд",
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
            "Подписка подтверждена!",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            "Вы подписались не на все каналы:",
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
            f"Главное меню\n\nПользователь: {user['first_name']}\nПодписка: {user['subscription'].upper()}\nЗапросов: {user['requests_today']}/{user['requests_limit']}\nБаланс: {user['stars']} звёзд",
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
            "Помощь по боту\n\n1. Нажми «Генератор»\n2. Выбери категорию\n3. Выбери количество, длину и тип\n4. Получи ники!\n\nПодписки: FREE 10/день, PRO 30/день, MASTER 150/день",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        print(f"Help error: {e}")
        await callback.answer("Ошибка")

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
                "Лимит запросов исчерпан!\nКупи подписку в меню.",
                reply_markup=main_menu_keyboard()
            )
            await callback.answer()
            return
        await state.set_state(GeneratorStates.choosing_category)
        await callback.message.edit_text(
            "Выбери категорию:",
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
            "Выбери количество:",
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
            "Выбери длину:",
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
            "Выбери тип символов:",
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
                "Лимит запросов исчерпан!",
