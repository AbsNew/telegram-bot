import asyncio
import re
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from flask import Flask
from threading import Thread

# بيانات الحساب
api_id = 5363697
api_hash = '2280ee24606143529bf8b97dbe306c38'
phone = '+9647806125801'

# بيانات الكروب
group_link = 'https://t.me/+FYoUuq5a2RJkN2Qy'

# 1. إنشاء اتصال بـ Telegram
client = TelegramClient('session', api_id, api_hash)

# 2. إعداد Flask للسيرفر
app = Flask(__name__)

@app.route('/')
def home():
    return "💡 البوت يعمل بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 3. تنظيف النص من الرموز غير المرغوبة
def clean_message(text):
    # حذف الرموز غير الرقمية والفواصل
    cleaned = re.sub(r'[^\d,]', '', text)
    return cleaned

# 4. تشغيل البوت الأساسي
async def bot_loop():
    await client.start(phone=phone)
    group = await client.get_entity(group_link)

    while True:
        try:
            await client.send_message(group, 'بقشيش')
            await asyncio.sleep(5)

            await client.send_message(group, 'راتب')
            await asyncio.sleep(5)

            await client.send_message(group, 'فلوسي')
            await asyncio.sleep(5)

            history = await client(GetHistoryRequest(
                peer=group,
                limit=10,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            latest_balance = None
            for message in history.messages:
                if message.message and 'فلوسك' in message.message:
                    print(f"📩 الرسالة التي تم العثور عليها: {message.message}")

                    cleaned_number = clean_message(message.message)

                    if cleaned_number:
                        latest_balance = cleaned_number.replace(',', '')
                        break

            if latest_balance:
                await client.send_message(group, f'استثمار {latest_balance}')
                print(f"✅ تم إرسال: استثمار {latest_balance}")
            else:
                print("❌ لم يتم العثور على رصيد!")

        except Exception as e:
            print(f"⚠️ خطأ: {e}")

        print("⏳ ننتظر 21 دقيقة...")
        await asyncio.sleep(1260)  # 21 دقيقة

# 5. تشغيل السيرفر
keep_alive()

# 6. تشغيل البوت
with client:
    client.loop.run_until_complete(bot_loop())
