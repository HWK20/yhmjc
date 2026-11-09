import os
import telebot
from flask import Flask, request

TOKEN = '9246966528:AAGElMITgNG_zCrQrxQT2_MFdRRa-O9w8_o'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_db = {}

@app.route('/')
def index():
    return "Bot is running online!", 200

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            # 打印收到的原始 JSON 数据到 Render 日志中！
            print("RECV JSON:", json_string)
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
        else:
            return 'Forbidden', 403
    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        return '', 200

@bot.message_handler(func=lambda message: True)
def track_username_change(message):
    try:
        user_id = message.from_user.id
        current_username = message.from_user.username
        
        # 强制在群里回显
        bot.reply_to(message, f"【收到】ID: {user_id}, Name: @{str(current_username)}")
        
        if user_id in user_db:
            old_username = user_db[user_id]
            if old_username != current_username:
                old_str = f"@{old_username}" if old_username else "无用户名"
                new_str = f"@{current_username}" if current_username else "无用户名"
                bot.reply_to(message, f"⚠️ 检测到用户名修改！旧: {old_str} -> 新: {new_str}")
        
        user_db[user_id] = current_username
    except Exception as e:
        print("HANDLER ERROR:", str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
