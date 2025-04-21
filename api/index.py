import json, requests, io
from PIL import Image
from flask import Flask, request, Response
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "7606678509:AAEpJmTxn-SHvgeNY2VZH5RN0j7Tr_i_MgQ"
AUTHORIZED_GROUP_IDS = [-1002453016338, -1002699301861]
AUTHORIZED_USER_IDS = [1745313119]
ITEM_DATA_URL = "https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/refs/heads/main/data/itemData.json"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/MACBRUH-OFC/FreeFire-Resources/main/live/IconCDN/android/"

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
item_data = json.loads(requests.get(ITEM_DATA_URL).text)

def process_image(url):
    try:
        img = Image.open(io.BytesIO(requests.get(url, timeout=10).content))
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

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="""
🎮 Free Fire Item Bot 🎮

Send item IDs in this format:
id (item id)

🔍 Get complete item details with images""")

def is_auth(update: Update):
    cid, uid = update.effective_chat.id, update.effective_user.id
    return (cid in AUTHORIZED_GROUP_IDS or (cid == uid and uid in AUTHORIZED_USER_IDS))

def restrict(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 ACCESS RESTRICTED\n\nThis bot only works in official group\nJoin @FreeFire_MacbruhUpdates", reply_to_message_id=update.message.message_id)

def handle(update: Update, context: CallbackContext):
    if not is_auth(update): return restrict(update, context)
    msg = update.message.text.strip()
    if msg.lower().startswith("id ") and len(msg) > 3:
        item_id = msg[3:].strip()
        if item_id.isdigit():
            item = next((i for i in item_data if i["itemID"] == int(item_id)), None)
            if item:
                return send_info(update, context, item)
            else:
                return context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Wrong ID/Data Not Found", reply_to_message_id=update.message.message_id)

def send_info(update: Update, context: CallbackContext, item):
    try:
        url = f"{IMAGE_BASE_URL}{item['itemID']}.png"
        img = process_image(url)
        cap = f"""▫️ ITEM DETAILS ▫️
➖➖➖➖➖➖➖
ID: {item['itemID']}
Name: {item['description']}
Desc: {item.get('description2', item['description'])}
Icon: {item['icon']}
➖➖➖➖➖➖➖"""
        if img:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=cap, reply_to_message_id=update.message.message_id)
        else:
            raise Exception("No image")
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text=cap + "\n⚠️ Image not available", reply_to_message_id=update.message.message_id)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

@app.route("/api/index", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return Response("ok", status=200)
