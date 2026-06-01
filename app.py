import os
import asyncio
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.executor import set_webhook

app = Flask(__name__)

BOT_TOKEN = "8962135280:AAGZIghAkTJAjXpkxNbGQxHbZ-4yjW3ndoc"
ADMIN_ID = int(os.environ.get("ADMIN_ID", 6224033630))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Kutish holatlari
waiting_for_photo = {}
waiting_for_phone = {}

# Menyu tugmalari
menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu.add(
    KeyboardButton("🎨 Mashina bo'yash"),
    KeyboardButton("🔄 Bamper almashtirish"),
    KeyboardButton("✨ Polirovka"),
    KeyboardButton("🔇 Shumoizolyatsiya"),
    KeyboardButton("🩸 Urib olgan man"),
    KeyboardButton("📞 Bog'lanish")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "🚘 *AvtoServis* botiga xush kelibsiz!\n\nXizmatlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=menu
    )

@dp.message_handler(text="🎨 Mashina bo'yash")
async def boyash(message: types.Message):
    await message.answer(
        "🎨 *Mashina bo'yash narxlari:*\n\n1 eshik — 150 000 so'm\n2 eshik — 280 000 so'm\nTo'liq kuzov — 1 200 000 so'm",
        parse_mode="Markdown"
    )

@dp.message_handler(text="🔄 Bamper almashtirish")
async def bamper(message: types.Message):
    await message.answer(
        "🔧 *Bamper almashtirish:*\n\nOld bamper — 350 000 so'm\nOrqa bamper — 320 000 so'm",
        parse_mode="Markdown"
    )

@dp.message_handler(text="✨ Polirovka")
async def polirovka(message: types.Message):
    await message.answer(
        "✨ *Polirovka:*\n\n1 eshik — 70 000 so'm\n2 eshik — 130 000 so'm",
        parse_mode="Markdown"
    )

@dp.message_handler(text="🔇 Shumoizolyatsiya")
async def shumo(message: types.Message):
    await message.answer(
        "🔇 *Shumoizolyatsiya:*\n\n1 eshik — 200 000 so'm\n2 eshik — 350 000 so'm",
        parse_mode="Markdown"
    )

@dp.message_handler(text="🩸 Urib olgan man")
async def urib_olgan(message: types.Message):
    user_id = message.from_user.id
    waiting_for_photo[user_id] = True
    await message.answer(
        "📸 *Zararlangan joyni suratga oling va tashlang!*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if waiting_for_photo.get(user_id):
        photo = message.photo[-1]
        file_id = photo.file_id
        waiting_for_photo[user_id] = False
        waiting_for_phone[user_id] = {"file_id": file_id}
        
        phone_button = ReplyKeyboardMarkup(resize_keyboard=True)
        phone_button.add(KeyboardButton("📱 Telefon raqam", request_contact=True))
        await message.answer(
            "✅ Rasm qabul qilindi!\n📞 Telefon raqamingizni yuboring:",
            reply_markup=phone_button
        )
    else:
        await message.answer("❌ Avval 'Urib olgan man' tugmasini bosing!")

@dp.message_handler(content_types=['contact'])
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_for_phone:
        phone = message.contact.phone_number
        file_id = waiting_for_phone[user_id]["file_id"]
        username = message.from_user.username or "Yo'q"
        
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=f"🩸 YANGI!\n👤 {message.from_user.full_name}\n📞 {phone}\n🆔 @{username}"
        )
        await message.answer(
            "✅ Adminga yuborildi!\nTez orada bog'lanamiz.",
            reply_markup=menu
        )
        del waiting_for_phone[user_id]
    else:
        await message.answer("❌ Avval 'Urib olgan man' tugmasini bosing!")

@dp.message_handler(text="📞 Bog'lanish")
async def contact(message: types.Message):
    await message.answer("📞 Telefon: +998 90 123 45 67\n📍 Manzil: Toshkent")

@dp.message_handler()
async def unknown(message: types.Message):
    await message.answer("❌ Tugmalardan birini tanlang!", reply_markup=menu)

# Flask route'lar
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = types.Update.to_object(await request.get_json())
    await dp.process_update(update)
    return jsonify({"status": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "alive"}), 200

@app.route("/")
def home():
    return "AvtoServis bot ishlayapti!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
