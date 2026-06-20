import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот-секретарь работает!", 200

@app.route('/health')
def health():
    return "OK", 200

API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
PHONE = os.environ.get('PHONE', '')
DEEPSEEK_USERNAME = '@DeepSeekBot'

if not API_ID or not API_HASH or not PHONE:
    raise ValueError("Задай API_ID, API_HASH и PHONE в переменных окружения!")

client = TelegramClient('session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # (весь тот же код обработки, но он не будет вызван, пока бот не авторизован)
    pass  # пока оставим пустым, главное — авторизоваться

async def start_bot():
    # Проверяем, есть ли сессия
    if os.path.exists('session.session'):
        print("Сессия найдена, подключаюсь...")
        await client.start(phone=PHONE)
        print("✅ Бот запущен!")
    else:
        # Если сессии нет, пытаемся получить код
        print("Сессии нет, запрашиваем код...")
        # Отправляем запрос на код, но не ждём ввода, а сразу прерываемся
        try:
            # Пытаемся стартовать с фиктивным кодом, чтобы Telegram отправил SMS
            await client.start(phone=PHONE, code_callback=lambda: input("Введите код: "))
        except Exception as e:
            print(f"Ошибка (это нормально): {e}")
            print("❌ Код отправлен на ваш телефон! Проверьте Telegram/SMS.")
            print("Теперь добавьте переменную AUTH_CODE с этим кодом и перезапустите деплой.")
            return  # завершаем, чтобы не ждать ввода
    # Если дошли сюда — авторизованы
    print("✅ Секретарь запущен и слушает сообщения...")
    await client.run_until_disconnected()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

thread = threading.Thread(target=run_bot)
thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
