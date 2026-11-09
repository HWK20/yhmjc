import os
import telebot
from flask import Flask, request

TOKEN = '9246966528:AAGElMITgNG_zCrQrxQT2_MFdRRa-O9w8_o'
bot = telebot.TeleBot(TOKEN)
app = Flask(name)

# 用于记录用户 ID 与 Username 的对应关系
user_db = {}

@app.route('/')
def index():
    return "Bot is running online!", 200

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@bot.message_handler(func=lambda message: True)
def track_username_change(message):
    user_id = message.from_user.id
    current_username = message.from_user.username
    
    # 检查是否记录过该用户
    if user_id in user_db:
        old_username = user_db[user_id]
        if old_username != current_username:
            old_str = f"@{old_username}" if old_username else "无用户名"
            new_str = f"@{current_username}" if current_username else "无用户名"
            
            alert_text = (
                f"⚠️ 检测到群成员修改 Username！\n\n"
                f"👤 用户: {message.from_user.first_name}\n"
                f"🆔 ID: {user_id}\n"
                f"🔴 旧用户名: {old_str}\n"
                f"🟢 新用户名: {new_str}"
            )
            bot.reply_to(message, alert_text, parse_mode="Markdown")
    
    # 每次发言均更新最新的用户名记录
    user_db[user_id] = current_username

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
