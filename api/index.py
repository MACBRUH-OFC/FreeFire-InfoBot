import json, io, requests
from PIL import Image
from flask import Flask, request, Response
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7606678509:AAEpJmTxn-SHvgeNY2VZH5RN0j7Tr_i_MgQ"
AUTHORIZED_GROUP_IDS = [-1002453016338, -1002699301861]
AUTHORIZED_USER_IDS = [1745313119]
ITEM_DATA_URL = "https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/refs/heads/main/data/itemData.json"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/main/live/IconCDN/android/"

app = Flask(__name__)
bot = Bot(BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🎮 Free Fire Item Bot 🎮

Send item IDs in this format:
id (item id)

🔍 Get complete item details with images
""")

def is_authorized(update: Update):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    return (cid in AUTHORIZED_GROUP_IDS or (cid == uid and uid in AUTHORIZED_USER_IDS))

async def unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 ACCESS RESTRICTED\n\nThis bot only works in official group\nJoin @FreeFire_MacbruhUpdates")

def load_item_data():
    try:
        response = requests.get(ITEM_DATA_URL)
        return json.loads(response.text)
    except:
        return []

def process_image(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        img = Image.open(io.BytesIO(response.content))
        if img.mode in ('RGBA', 'LA'):
            bg = Image.new('RGB', img.size, 'black')
            bg.paste(img, mask=img.split()[-1])
            img = bg
        out = io.BytesIO()
        img.save(out, format='PNG')
        out.seek(0)
        return out
    except:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await unauthorized(update, context)

    msg = update.message.text.strip()
    if msg.lower().startswith("id ") and len(msg) > 3:
        item_id = msg[3:].strip()
        if item_id.isdigit():
            item_data = load_item_data()
            item = next((i for i in item_data if i["itemID"] == int(item_id)), None)
            if item:
                await send_item_info(update, context, item)
            else:
                await update.message.reply_text("❌ Wrong ID/Data Not Found")

async def send_item_info(update: Update, context: ContextTypes.DEFAULT_TYPE, item):
    try:
        url = f"{IMAGE_BASE_URL}{item['itemID']}.png"
        img_bytes = process_image(url)
        caption = f"""▫️ ITEM DETAILS ▫️
➖➖➖➖➖➖➖
ID: {item['itemID']}
Name: {item['description']}
Desc: {item.get('description2', item['description'])}
Icon: {item['icon']}
➖➖➖➖➖➖➖"""
        if img_bytes:
            await update.message.reply_photo(photo=img_bytes, caption=caption)
        else:
            await update.message.reply_text(caption + "\n⚠️ Image not available")
    except:
        await update.message.reply_text("❌ Failed to send item info")

@app.route("/api/index", methods=["POST"])
def webhook():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        update = Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put_nowait(update)
        return Response("ok", status=200)
    except Exception as e:
        print("Webhook error:", e)
        return Response("error", status=500)
