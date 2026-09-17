import os
import json
import time
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
print("Bot is starting... Loading config...")

# Token ab GitHub se nahi, JustRunMy se lega - SAFE!
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8283637087:AAGIJJMw3R4JshOsLRBWMZBlkReIeDmDEbc")

def save_user(user_id):
    file = "users.json"
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
    with open(file, "r") as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(file, "w") as f:
            json.dump(users, f)
        return True
    return False

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    dic_power_ten = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + dic_power_ten[n] + 'B'

def time_formatter(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + ((str(hours) + "ʜ, ") if hours else "") + ((str(minutes) + "ᴍ, ") if minutes else "") + ((str(seconds) + "ꜱ") if seconds else "")
    return tmp if tmp else "0 ꜱ"

def make_progress_bar(percentage):
    completed = int(percentage / 6.25)
    return "▣" * completed + "▢" * (16 - completed)

async def total_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 8562470788
    user_id = update.effective_user.id
    if user_id!= ADMIN_ID:
        await update.message.reply_text(f"Aap admin nahi ho! Aapki ID hai: {user_id}")
        return
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        await update.message.reply_text(f"📊 Total Users: {len(users)}")
    except:
        await update.message.reply_text("Abhi tak koi user nahi hai!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name.upper() if update.effective_user else "USER"
    save_user(update.effective_user.id)
    caption_text = f"𝐇ᴇʟʟᴏ {user_name} 𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐔𝐑𝐋 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐁ᴏᴛ.\n\n𝐈 𝐀ᴍ 𝐔𝐑𝐋 𝐔ᴘʟᴏᴀᴅᴇʀ 𝐀ᴅᴠᴀɴᴄᴇ 𝐁ᴏᴛ."
    keyboard = [[InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/zexon_Bot_updates")],[InlineKeyboardButton("𝐒ʜᴀʀᴇ", url="https://t.me/URL_Save_Bot"), InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://whatsapp.com/channel/0029VbClgKEEVccGKahXmw3X")],[InlineKeyboardButton("𝐇ᴇʟᴘ", url="https://t.me/zexon_x")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=caption_text, reply_markup=reply_markup)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return
    status_msg = await update.message.reply_text("𝐏ʀᴏsᴇssɪɴɢ...⚡️")
    last_update = [0]
    loop = asyncio.get_running_loop()
    def yt_dlp_hook(d):
        if d['status'] == 'downloading':
            now = time.time()
            if now - last_update[0] < 2:
                return
            last_update[0] = now
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0) or 0
            eta = d.get('eta', 0) or 0
            if total > 0:
                percentage = (downloaded / total) * 100
                bar = make_progress_bar(percentage)
                text = f"𝐒ᴛᴀᴛᴜs 𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ:\n\n{bar}\n\n 𝐒ɪᴢᴇ : {humanbytes(downloaded)} | {humanbytes(total)}\n 𝐃ᴏɴᴇ : {round(percentage, 2)}%\n 𝐒ᴘᴇᴇᴅ : {humanbytes(speed)}/s\n 𝐄ᴛᴀ : {time_formatter(eta)}"
                asyncio.run_coroutine_threadsafe(status_msg.edit_text(text), loop)
    if "youtube.com" in url or "youtu.be" in url:
        format_opt = "bestvideo[height<=360]+bestaudio/best[height<=360]/best" if "shorts" not in url else "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    else:
        format_opt = "bestvideo+bestaudio/best"
    ydl_opts = {'format': format_opt, 'outtmpl': 'downloads/%(title)s.%(ext)s', 'merge_output_format': 'mp4', 'quiet': True, 'progress_hooks': [yt_dlp_hook]}
    try:
        def download_file():
            os.makedirs("downloads", exist_ok=True)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                return filename
        filename = await loop.run_in_executor(None, download_file)
        file_size = os.path.getsize(filename)
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴜᴄᴄᴇꜱꜰᴜʟ ✨", write_timeout=600, read_timeout=600)
        await status_msg.delete()
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        await status_msg.edit_text(f"Failed: {str(e)}")

def main():
    print("Bot Started Successfully! Ready to work.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", total_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bot is running perfectly...")
    app.run_polling()

if __name__ == '__main__':
    main()
