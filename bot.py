import os
import yt_dlp
from telegram import Update, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

# إعداد
BOT_TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_ID = 123456789  # ← استبدله بمعرفك

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# تخزين المستخدمين
users = set()

# تحميل الصوت من اليوتيوب
def download_youtube_audio(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            filename = ydl.prepare_filename(info['entries'][0])
            mp3_path = filename.rsplit('.', 1)[0] + '.mp3'
            title = info['entries'][0]['title']
            return mp3_path, title
        except Exception as e:
            print(f"Error: {e}")
            return None, None

# التعامل مع الرسائل
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    users.add(user_id)

    if text.lower().startswith("يوت "):
        query = text[4:]
        update.message.reply_chat_action(ChatAction.UPLOAD_AUDIO)
        update.message.reply_text("🔎 جاري البحث وتحميل الصوت، انتظر...")

        mp3_path, title = download_youtube_audio(query)
        if mp3_path:
            update.message.reply_audio(audio=open(mp3_path, 'rb'), title=title, caption=f"🎵 {title}")
        else:
            update.message.reply_text("❌ حدث خطأ أثناء التحميل.")

# لوحة المطور
def dev_panel(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("🚫 غير مسموح.")

    count = len(users)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 عدد المستخدمين", callback_data="count")],
        [InlineKeyboardButton("🗑️ حذف الملفات", callback_data="clean")],
    ])
    update.message.reply_text(f"🔧 لوحة المطور\nعدد المستخدمين: {count}", reply_markup=keyboard)

# أزرار لوحة المطور
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "count":
        query.edit_message_text(f"👤 عدد المستخدمين الفريدين: {len(users)}")

    elif query.data == "clean":
        for file in os.listdir(DOWNLOAD_FOLDER):
            os.remove(os.path.join(DOWNLOAD_FOLDER, file))
        query.edit_message_text("🗑️ تم حذف جميع الملفات المؤقتة.")

# تشغيل البوت
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CommandHandler("لوحة", dev_panel))
    dp.add_handler(telegram.ext.CallbackQueryHandler(button_callback))

    updater.start_polling()
    print("✅ البوت شغال...")
    updater.idle()

if __name__ == '__main__':
    main()
