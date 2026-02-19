import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from yt_dlp import YoutubeDL

# 1. SOZLAMALAR
# Tokenni to'g'ridan-to'g'ri yozamiz yoki o'zgaruvchiga olamiz
TOKEN = "8530462813:AAFxPrAjZyDG6Fgv_JMqy0XwMgnCKQp1Zv4"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Yuklash papkasini yaratish
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Video yuklash sozlamalari
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
}

# Audio yuklash sozalamalari
AUDIO_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
}

# 2. RENDER UCHUN PORTNI BAND QILISH (DUMMY SERVER)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    # Loglarni konsolda ko'rsatmaslik uchun
    def log_message(self, format, *args):
        return

def run_port_listener():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Render port {port} eshitilmoqda...")
    server.serve_forever()

# 3. BOT FUNKSIYALARI
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "<b>Salom!</b> 👋\n\n"
        "Men orqali:\n"
        "1. 🔗 Video havola yuborib yuklab olishingiz\n"
        "2. 🎵 Qo'shiq nomi yoki ijrochini yozib topishingiz mumkin.", 
        parse_mode="HTML"
    )

@dp.message()
async def handle_request(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ Biroz kutib turing...")
    file_path = None

    try:
        if "http" in url:
            # VIDEO YUKLASH
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                video_input = types.FSInputFile(file_path)
                await bot.send_video(message.chat.id, video_input, caption=info.get('title', ''))
        else:
            # QO'SHIQ QIDIRISH (Nomidan)
            with YoutubeDL(AUDIO_OPTIONS) as ydl:
                search_query = f"ytsearch1:{url}"
                info = ydl.extract_info(search_query, download=True)['entries'][0]
                
                # Audio fayl nomini to'g'ri olish (.mp3 formatini hisobga olgan holda)
                temp_name = ydl.prepare_filename(info)
                file_path = os.path.splitext(temp_name)[0] + ".mp3"
                
                audio_input = types.FSInputFile(file_path)
                await bot.send_audio(message.chat.id, audio_input, title=info.get('title'))

        # Faylni o'chirish (xotirani tejash)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik yuz berdi. Havola noto'g'ri yoki serverda yuklama ko'p.")
        print(f"Xato: {e}")

# 4. ASOSIY ISHGA TUSHIRISH
async def main():
    # Render portini alohida oqimda ishga tushiramiz
    threading.Thread(target=run_port_listener, daemon=True).start()
    
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
