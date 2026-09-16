import json
import os
import telebot
from telebot import types

# ==========================================
# SOZLAMALAR
# ==========================================

TOKEN = "8853316884:AAE5EMJfT738oDrahu756PjZJ0shoR4Cjew"

# BU YERGA FAQAT O'Z TELEGRAM ID INGIZNI YOZING
ADMIN_ID = 8140750076

bot = telebot.TeleBot(TOKEN)

PLAYERS_FILE = "players.json"
USERS_FILE = "users.json"


# ==========================================
# FAYLLAR
# ==========================================

def load_data(file_name, default):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return default
    return default


players = load_data(PLAYERS_FILE, {})
users = load_data(USERS_FILE, [])


def save_players():
    with open(PLAYERS_FILE, "w", encoding="utf-8") as file:
        json.dump(players, file, ensure_ascii=False, indent=4)


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)


# ==========================================
# FOYDALANUVCHINI SAQLASH
# ==========================================

def add_user(user_id):
    if user_id not in users:
        users.append(user_id)
        save_users()


# ==========================================
# ASOSIY MENYU
# ==========================================

def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=4
    )

    buttons = []
    for i in range(1, 14):
        buttons.append(types.KeyboardButton(str(i)))

    markup.add(*buttons)
    markup.add(
        types.KeyboardButton("📢 Yangiliklar"),
        types.KeyboardButton("ℹ️ Bot haqida")
    )

    # FAQAT ADMIN KO'RADI
    if user_id == ADMIN_ID:
        markup.add(
            types.KeyboardButton("🔐 ADMIN PANEL")
        )

    return markup


# ==========================================
# ADMIN MENYU
# ==========================================

def admin_menu():
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )
    markup.add(
        types.KeyboardButton("➕ Odam qo'shish"),
        types.KeyboardButton("✏️ Ma'lumotni o'zgartirish"),
        types.KeyboardButton("🗑 Odamni o'chirish"),
        types.KeyboardButton("📢 Yangilik yuborish"),
        types.KeyboardButton("👥 Foydalanuvchilar"),
        types.KeyboardButton("⬅️ Asosiy menyu")
    )
    return markup


# ==========================================
# START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):
    add_user(message.from_user.id)
    bot.send_message(
        message.chat.id,
        """⚽ <b>7-A FUTBOL STATISTIKA BOTI</b>

Futbolchini ko'rish uchun 1–13 raqamlardan birini bosing.""",
        parse_mode="HTML",
        reply_markup=main_menu(message.from_user.id)
    )


# ==========================================
# ADMIN PANEL
# ==========================================

@bot.message_handler(commands=["admin"])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Sizda admin huquqi yo'q.")
        return

    bot.send_message(
        message.chat.id,
        """🔐 <b>ADMIN PANEL</b>

Bu yerdan futbolchilarni boshqarishingiz mumkin.""",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔐 ADMIN PANEL")
def admin_button(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "🔐 <b>ADMIN PANEL</b>",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# ==========================================
# Odam qo'shish va Tahrirlash
# ==========================================

@bot.message_handler(func=lambda message: message.text == "➕ Odam qo'shish")
def add_start(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        """🔢 Qaysi raqamga futbolchi qo'shasiz?

1 dan 13 gacha raqam yuboring."""
    )
    bot.register_next_step_handler(msg, add_number)


def add_number(message):
    if message.from_user.id != ADMIN_ID:
        return

    number = message.text.strip()
    if not number.isdigit() or not 1 <= int(number) <= 13:
        msg = bot.send_message(message.chat.id, "❌ Faqat 1–13 orasidagi raqamni yuboring.")
        bot.register_next_step_handler(msg, add_number)
        return

    number = str(int(number))
    msg = bot.send_message(
        message.chat.id,
        f"""✅ {number}-raqam tanlandi.

👤 Endi futbolchining <b>ismini</b> yozing:""",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, add_name, number)


@bot.message_handler(func=lambda message: message.text == "✏️ Ma'lumotni o'zgartirish")
def edit_start(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        """✏️ Qaysi raqamdagi futbolchi ma'lumotlarini o'zgartirasiz?
1 dan 13 gacha raqam yuboring."""
    )
    bot.register_next_step_handler(msg, edit_choose_number)


def edit_choose_number(message):
    if message.from_user.id != ADMIN_ID:
        return

    number = message.text.strip()
    if number not in players:
        bot.send_message(
            message.chat.id,
            "❌ Bu raqamda hech qanday futbolchi topilmadi.",
            reply_markup=admin_menu()
        )
        return

    msg = bot.send_message(
        message.chat.id,
        f"""🔄 {number}-raqam tanlandi (Hozirgi: {players[number]['name']} {players[number]['surname']}).

👤 Futbolchining yangi <b>ismini</b> yozing:""",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, add_name, number)


def add_name(message, number):
    if message.from_user.id != ADMIN_ID:
        return

    name = message.text.strip()
    msg = bot.send_message(message.chat.id, "👤 Familiyasini yozing:")
    bot.register_next_step_handler(msg, add_surname, number, name)


def add_surname(message, number, name):
    if message.from_user.id != ADMIN_ID:
        return

    surname = message.text.strip()
    msg = bot.send_message(message.chat.id, """🏫 Sinfini yozing:
Masalan: 7-A""")
    bot.register_next_step_handler(msg, add_class, number, name, surname)


def add_class(message, number, name, surname):
    if message.from_user.id != ADMIN_ID:
        return

    class_name = message.text.strip()
    msg = bot.send_message(message.chat.id, "🏟️ O'yinlar sonini yozing:")
    bot.register_next_step_handler(msg, add_matches, number, name, surname, class_name)


def add_matches(message, number, name, surname, class_name):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "❌ O'yinlar sonini raqam bilan yozing.")
        bot.register_next_step_handler(msg, add_matches, number, name, surname, class_name)
        return

    matches = int(message.text)
    msg = bot.send_message(message.chat.id, "⚽ Gollar sonini yozing:")
    bot.register_next_step_handler(msg, add_goals, number, name, surname, class_name, matches)


def add_goals(message, number, name, surname, class_name, matches):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "❌ Gollarni raqam bilan yozing.")
        bot.register_next_step_handler(msg, add_goals, number, name, surname, class_name, matches)
        return

    goals = int(message.text)
    msg = bot.send_message(message.chat.id, "🎯 Assistlar sonini yozing:")
    bot.register_next_step_handler(msg, add_assists, number, name, surname, class_name, matches, goals)


def add_assists(message, number, name, surname, class_name, matches, goals):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "❌ Assistni raqam bilan yozing.")
        bot.register_next_step_handler(msg, add_assists, number, name, surname, class_name, matches, goals)
        return

    assists = int(message.text)
    msg = bot.send_message(message.chat.id, "📏 Bo'yini yozing (cm):")
    bot.register_next_step_handler(msg, add_height, number, name, surname, class_name, matches, goals, assists)


def add_height(message, number, name, surname, class_name, matches, goals, assists):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, """❌ Bo'yni raqam bilan yozing.
Masalan: 171""")
        bot.register_next_step_handler(msg, add_height, number, name, surname, class_name, matches, goals, assists)
        return

    height = int(message.text)
    msg = bot.send_message(message.chat.id, "⚖️ Vaznini yozing (kg):")
    bot.register_next_step_handler(msg, add_weight, number, name, surname, class_name, matches, goals, assists, height)


def add_weight(message, number, name, surname, class_name, matches, goals, assists, height):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, """❌ Vaznni raqam bilan yozing.
Masalan: 55""")
        bot.register_next_step_handler(msg, add_weight, number, name, surname, class_name, matches, goals, assists, height)
        return

    weight = int(message.text)
    msg = bot.send_message(
        message.chat.id,
        """🦶 Qaysi oyoqda o'ynaydi?

Masalan:
O'ng oyoq
Chap oyoq
Ikki oyoq"""
    )
    bot.register_next_step_handler(msg, add_foot, number, name, surname, class_name, matches, goals, assists, height, weight)


def add_foot(message, number, name, surname, class_name, matches, goals, assists, height, weight):
    if message.from_user.id != ADMIN_ID:
        return

    foot = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        """⭐ 5 ta yulduzdan nechta berasiz?

1, 2, 3, 4 yoki 5 yozing."""
    )
    bot.register_next_step_handler(msg, add_stars, number, name, surname, class_name, matches, goals, assists, height, weight, foot)


def add_stars(message, number, name, surname, class_name, matches, goals, assists, height, weight, foot):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text not in ["1", "2", "3", "4", "5"]:
        msg = bot.send_message(message.chat.id, "❌ Faqat 1 dan 5 gacha yozing.")
        bot.register_next_step_handler(msg, add_stars, number, name, surname, class_name, matches, goals, assists, height, weight, foot)
        return

    stars = int(message.text)

    players[number] = {
        "name": name,
        "surname": surname,
        "class": class_name,
        "matches": matches,
        "goals": goals,
        "assists": assists,
        "height": height,
        "weight": weight,
        "foot": foot,
        "stars": stars
    }
    save_players()

    bot.send_message(
        message.chat.id,
        f"""✅ <b>Futbolchi ma'lumotlari saqlandi!</b>

🔢 Raqam: {number}
👤 Ism: {name} {surname}
🏫 Sinf: {class_name}
🏟️ O'yinlar: {matches}
⚽ Gollar: {goals}
🎯 Assistlar: {assists}
📏 Bo'y: {height} cm
⚖️ Vazn: {weight} kg
🦶 Oyoq: {foot}
⭐ Bahosi: {'⭐' * stars}""",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )


# ==========================================
# RAQAM BOSILGANDA
# ==========================================

@bot.message_handler(func=lambda message: message.text in [str(i) for i in range(1, 14)])
def player_info(message):
    add_user(message.from_user.id)
    number = message.text

    if number not in players:
        bot.send_message(
            message.chat.id,
            f"""🔢 <b>{number}-raqam</b>

⚠️ Bu raqamga hali futbolchi qo'shilmagan.""",
            parse_mode="HTML",
            reply_markup=main_menu(message.from_user.id)
        )
        return

    p = players[number]
    stars = "⭐" * p["stars"] + "☆" * (5 - p["stars"])
    matches_count = p.get("matches", 0)

    text = (
        f"⚽ <b>{p['name']} {p['surname']}</b>\n\n"
        f"🔢 Raqami: <b>{number}</b>\n"
        f"🏫 Sinfi: <b>{p['class']}</b>\n\n"
        f"🏟️ O'yinlar soni: <b>{matches_count}</b>\n"
        f"⚽ Gollar: <b>{p['goals']}</b>\n"
        f"🎯 Assistlar: <b>{p['assists']}</b>\n"
        f"📏 Bo'yi: <b>{p['height']} cm</b>\n"
        f"⚖️ Vazni: <b>{p['weight']} kg</b>\n"
        f"🦶 Asosiy oyoq: <b>{p['foot']}</b>\n"
        f"⭐ Darajasi: <b>{stars}</b>\n\n"
        f"📊 <b>{p['name']}ning {p['class']} safidagi statistikasi</b>"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu(message.from_user.id)
    )


# ==========================================
# O'CHIRISH
# ==========================================

@bot.message_handler(func=lambda message: message.text == "🗑 Odamni o'chirish")
def delete_start(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        """🗑 Qaysi raqamdagi odamni o'chirasiz?
1–13 raqam yuboring."""
    )
    bot.register_next_step_handler(msg, delete_player)


def delete_player(message):
    if message.from_user.id != ADMIN_ID:
        return

    number = message.text.strip()
    if number in players:
        name = players[number]["name"]
        del players[number]
        save_players()

        bot.send_message(
            message.chat.id,
            f"🗑 <b>{number}-raqamdagi {name} o'chirildi.</b>",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Bu raqamda futbolchi yo'q.",
            reply_markup=admin_menu()
        )


# ==========================================
# FOYDALANUVCHILAR
# ==========================================

@bot.message_handler(func=lambda message: message.text == "👥 Foydalanuvchilar")
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        f"👥 Botdan foydalanganlar: <b>{len(users)}</b>",
        parse_mode="HTML"
    )


# ==========================================
# YANGILIK
# ==========================================

@bot.message_handler(func=lambda message: message.text == "📢 Yangilik yuborish")
def news_start(message):
    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "📢 Yangilik matnini yuboring:"
    )
    bot.register_next_step_handler(msg, send_news)


def send_news(message):
    if message.from_user.id != ADMIN_ID:
        return

    success = 0
    failed = 0

    for user_id in users:
        try:
            bot.send_message(
                user_id,
                message.text,
                parse_mode="HTML"
            )
            success += 1
        except Exception:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"""✅ Yangilik yuborildi!

👥 Yuborildi: {success}
❌ Yuborilmadi: {failed}""",
        reply_markup=admin_menu()
    )


# ==========================================
# ASOSIY MENYU
# ==========================================

@bot.message_handler(func=lambda message: message.text == "⬅️ Asosiy menyu")
def back_main(message):
    bot.send_message(
        message.chat.id,
        "⚽ Asosiy menyu",
        reply_markup=main_menu(message.from_user.id)
    )


# ==========================================
# BOT HAQIDA
# ==========================================

@bot.message_handler(func=lambda message: message.text == "ℹ️ Bot haqida")
def about(message):
    bot.send_message(
        message.chat.id,
        """⚽ <b>7-A Futbol Statistikasi</b>

Bu bot orqali 1–13 raqamdagi futbolchilarning statistikalarini ko'rish mumkin.

🔐 Futbolchilarni faqat admin qo'sha oladi.""",
        parse_mode="HTML"
    )


# ==========================================
# YANGILIKLAR
# ==========================================

@bot.message_handler(func=lambda message: message.text == "📢 Yangiliklar")
def news(message):
    bot.send_message(
        message.chat.id,
        """📢 Hozircha yangi yangiliklar yo'q."""
    )


# ==========================================
# ISHGA TUSHIRISH
# ==========================================

if __name__ == "__main__":
    print("🤖 BOT ISHLADI!")
    bot.infinity_polling()
