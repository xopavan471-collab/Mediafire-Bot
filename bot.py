import telebot, os, re, requests, time
import cloudscraper

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)
scraper = cloudscraper.create_scraper()

def get_direct(u):
    try:
        t = scraper.get(u, timeout=30).text
        m = re.search(r'href="(https://download\d+[^"]+)"', t)
        if m: return m.group(1).replace('&amp;','&')
        m = re.search(r'aria-label="Download file" href="([^"]+)"', t)
        if m: return m.group(1)
    except: pass
    return None

def bar(p):
    f = int(p//10)
    return "■"*f + "□"*(10-f)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Hello !! {name} Welcome to URL Uploader Bot.

Features:  
🤟 Just Send me media fire Link
🌐 Direct URL uploader  
⚡ Fast & smooth processing 
🔗 Unlimited Upload Link 
🚀 Enjoy a premium, Hassle-free Enjoy")

@bot.message_handler(func=lambda x: True)
def handle(m):
    if not m.text or "http" not in m.text: return
    url = re.search(r'https?://[^\s]+', m.text).group(0)
    try:
        s = bot.send_message(m.chat.id, "🔍 Searching...")
        dl = get_direct(url)
        if not dl:
            bot.edit_message_text("❌ Link nahi mila", m.chat.id, s.message_id)
            return
        r = requests.get(dl, stream=True, timeout=90)
        total = int(r.headers.get('content-length', 0))
        name = url.split('/')[-1].split('?')[0] or "file.apk"
        down = 0
        last = 0
        with open(name, 'wb') as f:
            for c in r.iter_content(1024*1024):
                if c:
                    f.write(c)
                    down+=len(c)
                    if time.time()-last > 1:
                        p = down/total*100 if total else 0
                        try:
                            bot.edit_message_text(f"⬇️ [{bar(p)}] {p:.1f}%\n📦 {down//1048576}MB / {total//1048576}MB\n📄 {name}", m.chat.id, s.message_id)
                        except: pass
                        last=time.time()
        bot.edit_message_text("⬆️ Uploading...", m.chat.id, s.message_id)
        with open(name, 'rb') as f:
            bot.send_document(m.chat.id, f, caption="✅ Done ")
        os.remove(name)
        bot.delete_message(m.chat.id, s.message_id)
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

print("Bot Started")
bot.infinity_polling()
