import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties  # Новый импорт
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
ADMIN_ID = 7323296973
TOKEN_1 = "8734424678:AAH7K4Ubg61Jd5umYnSPsbmI9wA4jMKyGKc"
PAYMENT_TOKEN = "1744374395:TEST:fe69aeca23963436d65b"
TOKEN_2 = "ВСТАВЬ_ТОКЕН_ВТОРОГО_БОТА"

logging.basicConfig(level=logging.INFO)

# Инициализация ботов по новым правилам aiogram 3.7+
bot1 = Bot(
    token=TOKEN_1, 
    default=DefaultBotProperties(parse_mode="HTML")
)
dp1 = Dispatcher()

bot2 = Bot(
    token=TOKEN_2, 
    default=DefaultBotProperties(parse_mode="HTML")
)
dp2 = Dispatcher()

# --- ХЕНДЛЕРЫ БОТА №1 (Оплата) ---

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Купить Звёзды", callback_data="buy_stars")]
    ])

@dp1.message(Command("start"))
async def start_1(message: types.Message):
    await message.answer("<b>Бот №1 (Оплата):</b> Нажмите кнопку для покупки:", reply_markup=main_kb())

@dp1.callback_query(F.data == "buy_stars")
async def ask_quantity(call: types.CallbackQuery):
    await call.message.answer("Введите количество звезд (минимум 15):")
    await call.answer()

@dp1.message(F.text.regexp(r'^\d+$'))
async def process_payment(msg: types.Message):
    quantity = int(msg.text)
    if quantity < 15:
        return await msg.answer("❌ Минимальная покупка — 15 ⭐")
    
    price_rub = int(quantity * 1.2 * 100)
    await msg.answer_invoice(
        title="Пополнение баланса",
        description=f"Покупка {quantity} ⭐",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Звезды", amount=price_rub)],
        payload=str(quantity),
        start_parameter="top-up"
    )

@dp1.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp1.message(F.successful_payment)
async def success(message: types.Message):
    quantity = message.successful_payment.invoice_payload
    await message.answer(f"✅ Оплачено! Вам начислено {quantity} ⭐")
    
    # Уведомление админу
    await bot1.send_message(
        ADMIN_ID, 
        f"💰 <b>Новая оплата!</b>\nОт: @{message.from_user.username}\nКоличество: {quantity} ⭐"
    )

# --- ХЕНДЛЕРЫ БОТА №2 ---

@dp2.message(Command("start"))
async def start_2(message: types.Message):
    await message.answer("Привет! Это твой <b>второй бот</b>.")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---

async def handle(request):
    return web.Response(text="Bot is alive!")

# --- ЗАПУСК ---

async def main():
    # Запуск мини-сервера для Render (порт 10000)
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    
    print("Боты и веб-сервер запущены...")
    
    await bot1.delete_webhook(drop_pending_updates=True)
    await bot2.delete_webhook(drop_pending_updates=True)
    
    await asyncio.gather(
        dp1.start_polling(bot1),
        dp2.start_polling(bot2)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выключено")
