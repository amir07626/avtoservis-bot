import os
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import asyncio

app = Flask(__name__)

BOT_TOKEN = "8962135280:AAHjqD7dxNLZossVjI4qtoYnftbOhZ49XzY"
ADMIN_IDS = [6224033630, 616529579]  # ❗ AZIM_PRO ID sini qo'shing

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Kutilayotgan holatlar
waiting_for_media = {}   # rasm yoki video
waiting_for_phone = {}
notified_users = set()   # esemes yuborilgan mijozlar

# ============ MENYU (YANGI) ============
menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu.add(
    KeyboardButton("✨ Polirovka"),
    KeyboardButton("🔄 Bamper almashtirish"),
    KeyboardButton("🔇 Shumoizolyatsiya"),
    KeyboardButton("🩸 Urib olgan man"),
    KeyboardButton("📞 Bog'lanish")
)

# ============ START ============
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "🚘 *AvtoServis* botiga xush kelibsiz!\n\nQuyidagi xizmatlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=menu
    )

# ============ POLIROVKA ============
@dp.message_handler(text="✨ Polirovka")
async def polishing(message: types.Message):
    await message.answer(
        "✨ *Polirovka narxlari:*\n\n"
        "• Mashina holatiga qarab — 1 000 000 so'mdan boshlanadi\n"
        "• Qora rang — qimmatroq\n"
        "• Oq rang — nisbatan arzonroq\n\n"
        "📞 Aniq narx uchun biz bilan bog'laning!",
        parse_mode="Markdown"
    )

# ============ BAMPER ============
@dp.message_handler(text="🔄 Bamper almashtirish")
async def bumper(message: types.Message):
    await message.answer(
        "🔧 *Bamper almashtirish:*\n\n"
        "• Old bamper — 150 000 so'mdan\n"
        "• Orqa bamper — 150 000 so'mdan\n\n"
        "🚗 Mashina modeliga qarab narx o'zgarishi mumkin.",
        parse_mode="Markdown"
    )

# ============ SHUMOIZOLYATSIYA ============
@dp.message_handler(text="🔇 Shumoizolyatsiya")
async def shumo(message: types.Message):
    await message.answer(
        "🔇 *Shumoizolyatsiya narxlari:*\n\n"
        "• Eshiklar — 500 000 - 1 500 000 so'm\n"
        "• Pol va bagaj — 2 000 000 - 4 000 000 so'm\n"
        "• To'liq salon — 3 500 000 - 5 500 000 so'm",
        parse_mode="Markdown"
    )

# ============ BOG'LANISH ============
@dp.message_handler(text="📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer(
        "📞 *Bog'lanish ma'lumotlari:*\n\n"
        "📍 Manzil: ул. Рудакий 152, Toshkent\n"
        "📱 Telefon: +998 91 547 70 99\n"
        "🕐 Ish vaqti: 09:00 - 19:00",
        parse_mode="Markdown"
    )

# ============ URIB OLGAN MAN (RASM YOKI VIDEO) ============
@dp.message_handler(text="🩸 Urib olgan man")
async def urib_olgan(message: types.Message):
    user_id = message.from_user.id
    waiting_for_media[user_id] = True
    await message.answer(
        "📸 *Zararlangan joyni suratga yoki videoga oling va tashlang!*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

# ============ MEDIA QABUL QILISH (RASM YOKI VIDEO) ============
@dp.message_handler(content_types=['photo', 'video'])
async def handle_media(message: types.Message):
    user_id = message.from_user.id
    if waiting_for_media.get(user_id):
        if message.photo:
            media = message.photo[-1]
            media_type = "🖼️ Rasm"
            file_id = media.file_id
        elif message.video:
            media = message.video
            media_type = "🎥 Video"
            file_id = media.file_id
        else:
            return
        
        waiting_for_media[user_id] = False
        waiting_for_phone[user_id] = {"file_id": file_id, "type": media_type}
        
        phone_button = ReplyKeyboardMarkup(resize_keyboard=True)
        phone_button.add(KeyboardButton("📱 Telefon raqam", request_contact=True))
        await message.answer(
            f"✅ {media_type} qabul qilindi!\n📞 Telefon raqamingizni yuboring:",
            reply_markup=phone_button
        )
    else:
        await message.answer("❌ Avval 'Urib olgan man' tugmasini bosing!")

# ============ TELEFON VA ADMINGA YUBORISH ============
@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_for_phone:
        phone = message.contact.phone_number
        data = waiting_for_phone[user_id]
        file_id = data["file_id"]
        media_type = data["type"]
        username = message.from_user.username or "Yo'q"
        full_name = message.from_user.full_name
        
        # IKKALA ADMINGA YUBORAMIZ
        for admin_id in ADMIN_IDS:
            try:
                if "Rasm" in media_type:
                    await bot.send_photo(
                        chat_id=admin_id,
                        photo=file_id,
                        caption=f"🩸 *YANGI MIJOZ!*\n\n👤 {full_name}\n📞 {phone}\n🆔 @{username}"
                    )
                else:
                    await bot.send_video(
                        chat_id=admin_id,
                        video=file_id,
                        caption=f"🩸 *YANGI MIJOZ!*\n\n👤 {full_name}\n📞 {phone}\n🆔 @{username}"
                    )
            except:
                pass
        
        # FAQAT BIRINCHI MARTA ESEMES KELADI
        if user_id not in notified_users:
            await message.answer(
                "✅ *Yangi mijoz!*\n"
                "Ma'lumotlaringiz adminga yuborildi.\n"
                "Admin ko'rib chiqguncha boshqa xabar kelmaydi.",
                parse_mode="Markdown",
                reply_markup=menu
            )
            notified_users.add(user_id)
        else:
            await message.answer(
                "✅ Ma'lumotlaringiz adminga yuborildi.\n"
                "Admin tez orada siz bilan bog'lanadi.",
                reply_markup=menu
            )
        
        del waiting_for_phone[user_id]
    else:
        await message.answer("❌ Avval 'Urib olgan man' tugmasini bosing!")

# ============ XATO XABAR ============
@dp.message_handler()
async def unknown(message: types.Message):
    user_id = message.from_user.id
    if waiting_for_media.get(user_id):
        await message.answer("❌ Iltimos, *RASM* yoki *VIDEO* tashlang!", parse_mode="Markdown")
    else:
        await message.answer("❌ Tugmalardan birini tanlang!", reply_markup=menu)

# ============ FLASK ============
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = types.Update.to_object(await request.get_json())
    await dp.process_update(update)
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
