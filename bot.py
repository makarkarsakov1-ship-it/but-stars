import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГУРАЦИЯ ---
# Твой токен бота
TOKEN = "8734424678:AAH7K4Ubg61Jd5umYnSPsbmI9wA4jMKyGKc"

# Твой тестовый токен платежного провайдера (Sberbank/ЮKassa и т.д.)
PAYMENT_PROVIDER_TOKEN = "1744374395:TEST:fe69aeca23963436d65b" 

MIN_STARS = 15
PRICE_PER_STAR = 1.2  # ₽ за 1 звезду

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()

# --- КЛАВИАТУРА ---
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Купить Звёзды", callback_data="buy_stars")]
    ])

# --- КОМАНДА /START ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "<b>Добро пожаловать!</b> 💎\n\nВы можете купить звёзды через кнопку ниже:",
        reply_markup=main_kb()
    )

# --- ОБРАБОТКА НАЖАТИЯ КНОПКИ ---
@dp.callback_query(F.data == "buy_stars")
async def ask_quantity(call: types.CallbackQuery):
    await call.message.answer(f"Введите число — сколько ⭐ вы хотите купить?\n(Минимум: <b>{MIN_STARS}</b>)")
    await call.answer()

# --- ОБРАБОТКА ВВОДА ЧИСЛА ---
@dp.message(F.text.regexp(r'^\d+$')) # Проверка, что введено только число
async def process_quantity(msg: types.Message):
    try:
        quantity = int(msg.text)
        if quantity < MIN_STARS:
            return await msg.answer(f"❌ Минимальная покупка: {MIN_STARS} ⭐")
            
        # Сумма в копейках (amount=100 это 1 рубль)
        price_rub = int(quantity * PRICE_PER_STAR * 100) 
        
        await msg.answer_invoice(
            title="Пополнение баланса",
            description=f"Покупка {quantity} ⭐ для вашего профиля",
            provider_token=PAYMENT_PROVIDER_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label=f"{quantity} ⭐", amount=price_rub)],
            payload=str(quantity), # Передаем количество звезд в чек для обработки после оплаты
            start_parameter="top-up-stars"
        )
    except ValueError:
        await msg.answer("Пожалуйста, введите корректное число звезд.")

# --- ПРОВЕРКА ПЛАТЕЖА (ДО ОПЛАТЫ) ---
@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    # Здесь можно добавить проверку наличия товара на складе
    await query.answer(ok=True)

# --- УСПЕШНАЯ ОПЛАТА ---
@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    quantity = int(message.successful_payment.invoice_payload)
    
    # ТУТ ЛОГИКА НАЧИСЛЕНИЯ
    # Например: await db.add_stars(user_id=message.from_user.id, count=quantity)
    
    await message.answer(
        f"✅ <b>Оплата прошла успешно!</b>\n\nВам начислено: <b>{quantity} ⭐</b>\n"
        f"Спасибо за покупку!"
    )

# --- ЗАПУСК ---
async def main():
    print("Бот для оплаты запущен...")
    # Удаляем вебхуки, чтобы бот отвечал только на новые сообщения
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
