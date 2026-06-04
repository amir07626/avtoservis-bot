import os
import time
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import asyncio

# Flask ilovasi
app = Flask(__name__)

# ============ SOZLAMALAR ============
BOT_TOKEN = "8962135280:AAHQ_1r6LQzjZe5gDUg6CrqXeRSMbhe3Ork"
ADMIN_IDS = [6224033630, 616529579]  # Siz va Azim_pro

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Holatlar
waiting_for_media = {}
waiting_for_phone = {}
notified_users = set()

# ============ MENYU ============
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
        "• Orqa bamper — 150 000 so'mdan",
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

# ============ URIB OLGAN MAN ============
@dp.message_handler(text="🩸 Urib olgan man")
async def urib_olgan(message: types.Message):
    user_id = message.from_user.id
    waiting_for_media[user_id] = True
    await message.answer(
        "📸 *Zararlangan joyni suratga yoki videoga oling va tashlang!*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

# ============ MEDIA QABUL QILISH ============
@dp.message_handler(content_types=['photo', 'video'])
async def handle_media(message: types.Message):
    user_id = message.from_user.id
    if waiting_for_media.get(user_id):
        if message.photo:
            media = message.photo[-1]
            media_type = "Rasm"
            file_id = media.file_id
        elif message.video:
            media = message.video
            media_type = "Video"
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

# ============ TELEFON VA ADMIN ============
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
        
        for admin_id in ADMIN_IDS:
            try:
                if media_type == "Rasm":
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
        
        if user_id not in notified_users:
            await message.answer(
                "✅ *Yangi mijoz!*\nMa'lumotlaringiz adminga yuborildi.\nAdmin ko'rib chiqguncha boshqa xabar kelmaydi.",
                parse_mode="Markdown",
                reply_markup=menu
            )
            notified_users.add(user_id)
        else:
            await message.answer(
                "✅ Ma'lumotlaringiz adminga yuborildi.\nAdmin tez orada siz bilan bog'lanadi.",
                reply_markup=menu
            )
        
        del waiting_for_phone[user_id]
    else:
        await message.answer("❌ Avval 'Urib olgan man' tugmasini bosing!")

# ============ XATO ============
@dp.message_handler()
async def unknown(message: types.Message):
    user_id = message.from_user.id
    if waiting_for_media.get(user_id):
        await message.answer("❌ Iltimos, *RASM* yoki *VIDEO* tashlang!", parse_mode="Markdown")
    else:
        await message.answer("❌ Tugmalardan birini tanlang!", reply_markup=menu)

# ============ WEBHOOK ============
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = types.Update.to_object(await request.get_json())
    await dp.process_update(update)
    return jsonify({"status": "ok"}), 200

@app.route("/health")
def health():
    return "OK", 200

# ============ ISHGA TUSHIRISH ============
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
