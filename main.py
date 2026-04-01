import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
ADMIN_ID = 7323296973
TOKEN_1 = "8734424678:AAH7K4Ubg61Jd5umYnSPsbmI9wA4jMKyGKc"
# Вставь сюда токен второго бота или такой же как первый для теста
TOKEN_2 = "ВСТАВЬ_ТОКЕН_ВТОРОГО_БОТА" 

logging.basicConfig(level=logging.INFO)

# Инициализация ботов (версия aiogram 3.7+)
bot1 = Bot(token=TOKEN_1, default=DefaultBotProperties(parse_mode="HTML"))
dp1 = Dispatcher()

bot2 = Bot(token=TOKEN_2, default=DefaultBotProperties(parse_mode="HTML"))
dp2 = Dispatcher()

# --- ХЕНДЛЕРЫ БОТА №1 ---
@dp1.message(Command("start"))
async def start_1(message: types.Message):
    await message.answer("<b>Привет!</b> Это Бот №1.\nФункционал оплаты временно отключен.")

# --- ХЕНДЛЕРЫ БОТА №2 ---
@dp2.message(Command("start"))
async def start_2(message: types.Message):
    await message.answer("<b>Привет!</b> Это Бот №2.")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не засыпал и не выдавал ошибку) ---
async def handle(request):
    return web.Response(text="Bot Status: Online")

async def main():
    # Настройка порта для Render
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    print(f"Сервер запущен на порту {port}. Боты выходят в онлайн...")

    # Очистка очереди сообщений и запуск
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
        print("Боты выключены")
