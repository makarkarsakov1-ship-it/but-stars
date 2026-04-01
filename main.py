import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web  # Добавили для Web Service

# --- КОНФИГУРАЦИЯ ---
ADMIN_ID = 7323296973
TOKEN_1 = "8734424678:AAH7K4Ubg61Jd5umYnSPsbmI9wA4jMKyGKc"
PAYMENT_TOKEN = "1744374395:TEST:fe69aeca23963436d65b"
TOKEN_2 = "ВСТАВЬ_ТОКЕН_ВТОРОГО_БОТА"

logging.basicConfig(level=logging.INFO)
bot1 = Bot(TOKEN_1, parse_mode="HTML")
dp1 = Dispatcher()
bot2 = Bot(TOKEN_2, parse_mode="HTML")
dp2 = Dispatcher()

# --- ХЕНДЛЕРЫ БОТА №1 ---
@dp1.message(Command("start"))
async def start_1(message: types.Message):
    await message.answer("<b>Бот №1:</b> Нажмите кнопку для покупки:", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💎 Купить Звёзды", callback_data="buy_stars")]]))

@dp1.callback_query(F.data == "buy_stars")
async def ask_quantity(call: types.CallbackQuery):
    await call.message.answer("Введите количество звезд (минимум 15):")
    await call.answer()

@dp1.message(F.text.regexp(r'^\d+$'))
async def process_payment(msg: types.Message):
    quantity = int(msg.text)
    if quantity < 15: return await msg.answer("Минимум 15.")
    await msg.answer_invoice(title="Покупка", description=f"{quantity} ⭐", provider_token=PAYMENT_TOKEN, 
                             currency="RUB", prices=[LabeledPrice(label="⭐", amount=int(quantity * 1.2 * 100))],
                             payload=str(quantity), start_parameter="top-up")

@dp1.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery): await query.answer(ok=True)

@dp1.message(F.successful_payment)
async def success(message: types.Message):
    await message.answer(f"✅ Оплачено: {message.successful_payment.invoice_payload} ⭐")
    await bot1.send_message(ADMIN_ID, f"💰 Покупка от @{message.from_user.username}")

# --- WEB SERVER ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Bot is running!")

# --- ЗАПУСК ---
async def main():
    # Запуск веб-сервера
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    
    # Запуск ботов
    await bot1.delete_webhook(drop_pending_updates=True)
    await bot2.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(dp1.start_polling(bot1), dp2.start_polling(bot2))

if __name__ == "__main__":
    asyncio.run(main())
