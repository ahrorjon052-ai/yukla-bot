import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from yt_dlp import YoutubeDL

# Bot tokenini shu yerga yozing yoki Environment Variable sifatida kiriting
TOKEN = os.getenv("8530462813:AAFxPrAjZyDG6Fgv_JMqy0XwMgnCKQp1Zv4")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Yuklab olish sozlamalari
ydl_opts_video = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'max_filesize': 50 * 1024 * 1024, # 50MB gacha
}

ydl_opts_audio = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Menga video havolasini yuboring yoki qo'shiq nomini yozing.")

@dp.message()
async def handle_message(message: types.Message):
    url = message.text
    msg = await message.answer("Xo'sh, qidiryapman...")

    try:
        if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url:
            # Video yuklash
            with YoutubeDL(ydl_opts_video) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                video = types.FSInputFile(filename)
                await bot.send_video(message.chat.id, video)
        else:
            # Qo'shiq nomi orqali qidirish (YouTube Music)
            search_query = f"ytsearch:{url}"
            with YoutubeDL(ydl_opts_audio) as ydl:
                info = ydl.extract_info(search_query, download=True)['entries'][0]
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                audio = types.FSInputFile(filename)
                await bot.send_audio(message.chat.id, audio, caption=info['title'])
        
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Xatolik yuz berdi: {str(e)}")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
