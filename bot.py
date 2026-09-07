import os, re, requests
import cloudscraper
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", 2040))
API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
TOKEN = os.environ.get("TOKEN") # Koyeb me TOKEN add karna

scraper = cloudscraper.create_scraper()

def get_mf_direct(url):
    try:
        html = scraper.get(url, timeout=30).text
        # New Mediafire pattern
        match = re.search(r'href="(https://download\d+\.mediafire\.com[^"]+)"', html)
        if match:
            return match.group(1).replace('&amp;', '&')
        match2 = re.search(r'aria-label="Download file" href="([^"]+)"', html)
        if match2:
            return match2.group(1)
    except Exception as e:
        print(f"Error: {e}")
    return None

app = Client("MediaFireBot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

# === TERA WALA START MESSAGE ===
@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        f"Hello!! {m.from_user.first_name} Welcome to URL Uploader Bot.\n\n"
        f"Features: \n"
        f"🤟 Just Send me media fire Link\n"
        f"🌐 Direct URL uploader \n"
        f"⚡ Fast & smooth processing \n"
        f"🔗 Unlimited Upload Link \n"
        f"🚀 Enjoy a premium, Hassle-free experience!"
    )

@app.on_message(filters.command("about"))
async def about(c, m):
    text = "**Bot Information:**\n\n🤖 Bot Name: Uploader X Pro\n🧩 Version: v3.0.1\n🌐 DC: DC-4(Amsterdam)\n🙆 Developer: ZEXON PAVAN"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Channel", url="https://t.me/NS_BOTS")]])
    await m.reply_text(text, reply_markup=btn)

@app.on_message(filters.text & ~filters.command(["start","about"]))
async def mf_handler(c, m):
    if "mediafire.com" not in m.text.lower():
        return
    try:
        url = re.search(r'https?://[^\s]+', m.text).group(0)
    except:
        return

    box = await m.reply_text(f"🔍 **Link Checking...**\n\n`{url}`\n\n▰▱▱▱▱▱▱▱ 10%")

    dl_url = get_mf_direct(url)
    if not dl_url:
        await box.edit("❌ **Direct Link nahi mila!**\nLink sahi hai kya check karo.")
        return

    await box.edit(f"📥 **Downloading Started...**\n\n▰▰▰▱▱▱▱▱▱ 30%\n`{url}`")

    try:
        file_name = url.split("/")[-1].split("?")[0] or "mediafire_file.mkv"
        r = requests.get(dl_url, stream=True, timeout=120)
        total_size = int(r.headers.get('content-length', 0))

        with open(file_name, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        await box.edit(f"⬆️ **Uploading to Telegram...**\n\n▰▰▰▰▰▰▰▱▱ 70%\n📄 `{file_name}`")

        await c.send_document(
            m.chat.id,
            file_name,
            caption=f"✅ **Uploaded!**\n\n📄 `{file_name}`\n🚀 **By URL Uploader Bot**"
        )
        os.remove(file_name)
        await box.delete()

    except Exception as e:
        await box.edit(f"❌ **Error:** `{e}`")

app.run()
