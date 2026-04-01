import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton

# --- ЛОГГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO)

# --- КОНФИГУРАЦИЯ БОТА №1 (Оплата) ---
TOKEN_1 = "8734424678:AAH7K4Ubg61Jd5umYnSPsbmI9wA4jMKyGKc"
PAYMENT_TOKEN = "1744374395:TEST:fe69aeca23963436d65b"
bot1 = Bot(TOKEN_1, parse_mode="HTML")
dp1 = Dispatcher()

# --- КОНФИГУРАЦИЯ БОТА №2 (Твой второй бот) ---
TOKEN_2 = "ВСТАВЬ_ТОКЕН_ВТОРОГО_БОТА"
bot2 = Bot(TOKEN_2, parse_mode="HTML")
dp2 = Dispatcher()

# =====================================================
# ХЕНДЛЕРЫ ДЛЯ БОТА №1 (ОПЛАТА)
# =====================================================

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Купить Звёзды", callback_data="buy_stars")]
    ])

@dp1.message(Command("start"))
async def start_1(message: types.Message):
    await message.answer("<b>Бот №1 (Оплата):</b> Нажмите кнопку для покупки:", reply_markup=main_kb())

@dp1.callback_query(F.data == "buy_stars")
async def ask_quantity(call: types.CallbackQuery):
    await call.message.answer(f"Введите число звезд (минимум 15):")
    await call.answer()

@dp1.message(F.text.regexp(r'^\d+$'))
async def process_payment(msg: types.Message):
    # Твоя логика формирования инвойса (из предыдущего кода)
    quantity = int(msg.text)
    if quantity < 15:
        return await msg.answer("Минимум 15 звезд.")
    
    price_rub = int(quantity * 1.2 * 100)
    await msg.answer_invoice(
        title="Пополнение",
        description=f"Покупка {quantity} ⭐",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="⭐", amount=price_rub)],
        payload=str(quantity),
        start_parameter="top-up"
    )

@dp1.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp1.message(F.successful_payment)
async def success(message: types.Message):
    await message.answer(f"✅ Оплачено! Начислено {message.successful_payment.invoice_payload} ⭐")

# =====================================================
# ХЕНДЛЕРЫ ДЛЯ БОТА №2 (ТВОЯ ЛОГИКА)
# =====================================================

@dp2.message(Command("start"))
async def start_2(message: types.Message):
    await message.answer("Привет! Это твой <b>второй бот</b>, запущенный в том же процессе.")

# Сюда можно копировать остальные хендлеры второго бота, 
# используя @dp2 вместо @dp

# =====================================================
# ЗАПУСК ОБОИХ БОТОВ
# =====================================================

async def main():
    print("Запуск обоих ботов...")
    
    # Удаляем вебхуки для обоих ботов
    await bot1.delete_webhook(drop_pending_updates=True)
    await bot2.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling параллельно
    await asyncio.gather(
        dp1.start_polling(bot1),
        dp2.start_polling(bot2)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
