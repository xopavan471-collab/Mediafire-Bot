import os, json, time, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 8562470788

def save_user(uid):
    f="users.json"
    if not os.path.exists(f):
        with open(f,"w") as x: json.dump([],x)
    with open(f,"r") as x: users=json.load(x)
    if uid not in users:
        users.append(uid)
        with open(f,"w") as x: json.dump(users,x)

def humanbytes(s):
    if not s: return "0 B"
    p=2**10; n=0; d={0:' ',1:'K',2:'M',3:'G',4:'T'}
    while s>p: s/=p; n+=1
    return f"{round(s,2)} {d[n]}B"

def make_progress_bar(per): return "▣"*int(per/6.25) + "▢"*(16-int(per/6.25))

async def start(update, context):
    save_user(update.effective_user.id)
    await update.message.reply_text(f"Hello {update.effective_user.first_name} - Send YouTube/Insta/FB Link")

async def total_users(update, context):
    if update.effective_user.id!=ADMIN_ID: return
    try:
        with open("users.json") as f: users=json.load(f)
        await update.message.reply_text(f"Total: {len(users)}")
    except: await update.message.reply_text("No users")

async def download_video(update, context):
    url=update.message.text.strip()
    if not url.startswith("http"): return
    msg=await update.message.reply_text("Processing...⚡️")
    last=[0]; loop=asyncio.get_running_loop()
    def hook(d):
        if d['status']=='downloading' and time.time()-last[0]>2:
            last[0]=time.time()
            tot=d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            per=d.get('downloaded_bytes',0)/tot*100
            asyncio.run_coroutine_threadsafe(msg.edit_text(f"Downloading {round(per,2)}%\n{make_progress_bar(per)}"), loop)
    fmt="bestvideo[height<=360]+bestaudio/best[height<=360]/best" if "youtu" in url else "bestvideo+bestaudio/best"
    opts={'format':fmt,'outtmpl':'downloads/%(title)s.%(ext)s','merge_output_format':'mp4','quiet':True,'progress_hooks':[hook]}
    try:
        def dl():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(url,download=True)
                return ydl.prepare_filename(info)
        fn=await loop.run_in_executor(None,dl)
        with open(fn,'rb') as v: await update.message.reply_video(video=v,caption="Successful ✨")
        await msg.delete(); os.remove(fn)
    except Exception as e: await msg.edit_text(f"Error: {e}")

def main():
    os.makedirs("downloads", exist_ok=True)
    app=ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", total_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("Bothost Bot Running...")
    app.run_polling()
if __name__=='__main__': main()
