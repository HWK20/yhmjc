import telebot
import json
import os
from flask import Flask, request

# 你的机器人 Token
TOKEN = "9246966528:AAGElMITgNG_zCrQrxQT2_MFdRRa-O9w8_o"
bot = telebot.TeleBot(TOKEN)
app = Flask(name)

# 兼容云端的本地数据路径
DATA_FILE = "user_names.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_db = load_data()

# 接收 Telegram 推送的隐藏接口
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# 访问主页时自动绑定 Webhook (Render 会分配一个专属的 .onrender.com 域名)
@app.route('/')
def webhook():
    bot.remove_webhook()
    # 这里的域名换成你在 Render 上获得的实际服务网址
    # 部署成功后，我们将把下面这行里的 URL 替换成你的 Render 线上网址
    return "Render 部署成功，等待绑定！", 200

# 核心检测逻辑
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'sticker'])
def track_username_changes(message):
    if not message.from_user:
        return

    user_id = str(message.from_user.id)
    current_username = message.from_user.username 
    current_display_username = f"@{current_username}" if current_username else "未设置"

    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    current_name = f"{first_name} {last_name}".strip()

    if user_id in user_db:
        old_username = user_db[user_id].get("username")
        if old_username != current_username and old_username is not None:
            alert_msg = (
                f"⚠️ 检测到群成员修改了 Username！\n\n"
                f"👤 用户昵称: {current_name}\n"
                f"🆔 用户 ID: {user_id}\n"
                f"❌ 旧用户名: @{old_username}\n"
                f"✅ 新用户名: {current_display_username}"
            )
            bot.send_message(message.chat.id, alert_msg, parse_mode="Markdown")

        user_db[user_id] = {"username": current_username, "name": current_name}
        save_data(user_db)
    else:
        user_db[user_id] = {"username": current_username, "name": current_name}
        save_data(user_db)

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))