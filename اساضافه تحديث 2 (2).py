import os
import re
import sys
import subprocess
import telebot
from telebot import types
import psutil
import io
import tokenize
from threading import Thread
TOKEN = '7358167328:AAFAqHkoHBhGyrWmQUyvXdD9UNbVQKaXgDc'
ADMIN_ID = '5340258438'

bot = telebot.TeleBot(TOKEN)

bot_scripts = {}
uploaded_files_dir = "uploaded_files"
banned_users = set()

# إنشاء مجلد uploaded_files إذا لم يكن موجوداً
if not os.path.exists(uploaded_files_dir):
    os.makedirs(uploaded_files_dir)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username in banned_users:
        bot.send_message(message.chat.id, "تم حظرك من البوت تواصل مع المطور @Z_7X_1")
        return

    markup = types.InlineKeyboardMarkup()
    upload_button = types.InlineKeyboardButton("رفع ملف 📤", callback_data='upload')
    markup.row(upload_button)
    bot.send_message(
        message.chat.id,
        "مرحبًا بك في بوت رفع وتشغيل ملفات بايثون.\n"
        "استخدم الزر بالأسفل لرفع الملفات.\n"
        "للحصول على جميع الأوامر والتعليمات، يمنع تماماً رفع ملفات غير بايثون حتى لا يتم حظرك /help.",
        reply_markup=markup
    )

@bot.message_handler(commands=['developer'])
def developer(message):
    if message.from_user.username in banned_users:
        bot.send_message(message.chat.id, "تم حظرك من البوت تواصل مع المطور @Z_7X_1")
        return

    markup = types.InlineKeyboardMarkup()
    wevy = types.InlineKeyboardButton("مطور البوت 👨‍🔧", url='https://t.me/Z_7X_1')
    markup.add(wevy)
    bot.send_message(message.chat.id, "للتواصل مع مطور البوت، اضغط على الزر أدناه:", reply_markup=markup)

@bot.message_handler(commands=['help'])
def instructions(message):
    if message.from_user.username in banned_users:
        bot.send_message(message.chat.id, "تم حظرك من البوت تواصل مع المطور @Z_7X_1")
        return

    bot.send_message(
        message.chat.id,
        "الأوامر المتاحة:\n"
        "/start - بدء البوت والحصول على الأزرار.\n"
        "/developer - التواصل مع المطور.\n"
        "/help - عرض هذه التعليمات.\n"
        "/rck [رسالة] - إرسال رسالة إلى جميع المستخدمين.\n"
        "/ban [معرف] - حظر مستخدم.\n"
        "/uban [معرف] - فك حظر مستخدم.\n"
        "/del [اسم الملف] - حذف ملف.\n"
        "/stp [اسم الملف] - إيقاف ملف.\n"
        "/str [اسم الملف] - تشغيل ملف.\n"
        "/rr [معرف] [رسالة] - إرسال رسالة لمستخدم معين.\n"
        "قم برفع ملف البايثون الخاص بك عبر الزر المخصص.\n"
        "بعد الرفع، يمكنك التحكم في التشغيل، الإيقاف، أو الحذف باستخدام الأزرار الظاهرة."
    )

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if str(message.from_user.id) != ADMIN_ID: 5340258438
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        username = message.text.split(' ', 1)[1].strip('@')
        if username in banned_users:
            bot.reply_to(message, f"المستخدم @{username} محظور بالفعل.")
        else:
            banned_users.add(username)
            bot.reply_to(message, f"تم حظر المستخدم @{username}.")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة معرف المستخدم بعد الأمر.")

@bot.message_handler(commands=['uban'])
def unban_user(message):
    if str(message.from_user.id) != ADMIN_ID: 5340258438
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        username = message.text.split(' ', 1)[1].strip('@')
        if username not in banned_users:
            bot.reply_to(message, f"المستخدم @{username} ليس محظور.")
        else:
            banned_users.remove(username)
            bot.reply_to(message, f"تم فك حظر المستخدم @{username}.")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة معرف المستخدم بعد الأمر.")

@bot.message_handler(commands=['rck'])
def broadcast_message(message):
    if str(message.from_user.id) != ADMIN_ID: 5340258438
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        msg = message.text.split(' ', 1)[1]
        for chat_id in bot_scripts.keys():
            bot.send_message(chat_id, msg)
        bot.reply_to(message, "تم إرسال الرسالة بنجاح.")
    except IndexError:
        if message.reply_to_message:
            msg = message.reply_to_message.text
            for chat_id in bot_scripts.keys():
                bot.send_message(chat_id, msg)
            bot.reply_to(message, "تم إرسال الرسالة بنجاح.")
        else:
            bot.reply_to(message, "يرجى كتابة الرسالة بعد الأمر أو الرد على رسالة.")

@bot.message_handler(commands=['rr'])
def send_private_message(message):
    if str(message.from_user.id) != ADMIN_ID: 5340258438
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        parts = message.text.split(' ', 2)
        username = parts[1].strip('@')
        msg = parts[2]
        for chat_id, script_info in bot_scripts.items():
            if script_info['uploader'] == username:
                bot.send_message(chat_id, msg)
                bot.reply_to(message, "تم إرسال الرسالة بنجاح.")
                return
        bot.reply_to(message, f"تعذر العثور على المستخدم @{username}.")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة معرف المستخدم والرسالة بعد الأمر.")

def file_contains_input_or_eval(content):
    for token_type, token_string, _, _, _ in tokenize.generate_tokens(io.StringIO(content).readline):
        if token_string in {"input", "eval"}:
            return True
    return False

@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        if message.from_user.username in banned_users:
            bot.send_message(message.chat.id, "تم حظرك من البوت تواصل مع المطور @Z_7X_1")
            return

        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot_script_name = message.document.file_name
        if not bot_script_name.endswith('.py'):
            bot.reply_to(message, "هذا بوت خاص برفع ملفات بايثون فقط.")
            return

        if any(ext in bot_script_name for ext in ['.php', '.zip']):
            bot.reply_to(message, "هذا بوت خاص برفع ملفات بايثون فقط.")
            return

        script_path = os.path.join(uploaded_files_dir, bot_script_name)
        file_content = downloaded_file.decode('utf-8')

        if file_contains_input_or_eval(file_content):
            bot.reply_to(message, "الملف يحتوي على دوال غير مسموح بها (مثل input أو eval).")
            return

        bot_scripts[message.chat.id] = {
            'name': bot_script_name,
            'uploader': message.from_user.username,
            'path': script_path,
            'process': None
        }

        with open(script_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot_token = get_bot_token(script_path)
        markup = types.InlineKeyboardMarkup()
        delete_button = types.InlineKeyboardButton(f"حذف {bot_script_name} 🗑", callback_data=f'delete_{message.chat.id}_{bot_script_name}')
        stop_button = types.InlineKeyboardButton(f"إيقاف {bot_script_name} 🔴", callback_data=f'stop_{message.chat.id}_{bot_script_name}')
        start_button = types.InlineKeyboardButton(f"تشغيل {bot_script_name} 🟢", callback_data=f'start_{message.chat.id}_{bot_script_name}')
        markup.row(delete_button, stop_button, start_button)

        bot.reply_to(
            message,
            f"تم رفع ملف بوتك بنجاح ✅\n\nاسم الملف المرفوع: {bot_script_name}\nتوكن البوت المرفوع: {bot_token}\nرفعه المستخدم: @{message.from_user.username}\n\nيمكنك التحكم في الملف باستخدام الأزرار الموجودة.",
            reply_markup=markup
        )
        send_to_admin(script_path, message.from_user.username)
        install_and_run_uploaded_file(script_path, message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

def send_to_admin(file_name, username):
    try:
        with open(file_name, 'rb') as file:
            bot.send_document(ADMIN_ID, file, caption=f"تم رفعه من قبل: @{username}")
    except Exception as e:
        print(f"Error sending file to admin: {e}")

def install_and_run_uploaded_file(script_path, chat_id):
    try:
        if os.path.exists('requirements.txt'):
            subprocess.Popen([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        p = subprocess.Popen([sys.executable, script_path])
        bot_scripts[chat_id]['process'] = p
        bot.send_message(chat_id, f"تم تشغيل {os.path.basename(script_path)} بنجاح.")
    except Exception as e:
        print(f"Error installing and running uploaded file: {e}")

def get_bot_token(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
            match = re.search(r'TOKEN\s*=\s*[\'"]([^\'"]*)[\'"]', content)
            if match:
                return match.group(1)
            else:
                return "تعذر العثور على التوكن"
    except Exception as e:
        print(f"Error getting bot token: {e}")
        return "تعذر العثور على التوكن"

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'upload':
        bot.send_message(call.message.chat.id, "يرجى إرسال الملف لرفعه.")
    elif 'delete_' in call.data or 'stop_' in call.data or 'start_' in call.data:
        try:
            user_id, script_name = call.data.split('_')[1], call.data.split('_')[2]
            script_path = bot_scripts[int(user_id)]['path']
            if 'delete' in call.data:
                try:
                    stop_bot(script_path, call.message.chat.id, delete=True)
                    bot.send_message(call.message.chat.id, f"تم حذف ملف {script_name} بنجاح.")
                    bot.send_message(ADMIN_ID, f"قام المستخدم @{bot_scripts[int(user_id)]['uploader']} بحذف ملفه {script_name}.")
                    with open(script_path, 'rb') as file:
                        bot.send_document(ADMIN_ID, file, caption=f"ملف محذوف: {script_name}")
                    bot_scripts.pop(int(user_id))
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"حدث خطأ: {e}")
            elif 'stop' in call.data:
                try:
                    stop_bot(script_path, call.message.chat.id)
                    bot.send_message(ADMIN_ID, f"قام المستخدم @{bot_scripts[int(user_id)]['uploader']} بإيقاف ملفه {script_name}.")
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"حدث خطأ: {e}")
            elif 'start' in call.data:
                try:
                    start_file(script_path, call.message.chat.id)
                    bot.send_message(ADMIN_ID, f"قام المستخدم @{bot_scripts[int(user_id)]['uploader']} بتشغيل ملفه {script_name}.")
                except Exception as e:
                    bot.send_message(call.message.chat.id, f"حدث خطأ: {e}")
        except IndexError:
            bot.send_message(call.message.chat.id, "حدث خطأ في معالجة الطلب. يرجى المحاولة مرة أخرى.")
    elif call.data == 'stop_all':
        stop_all_files(call.message.chat.id)
    elif call.data == 'start_all':
        start_all_files(call.message.chat.id)
    elif call.data == 'rck_all':
        bot.send_message(call.message.chat.id, "يرجى كتابة الرسالة لإرسالها للجميع.")
        bot.register_next_step_handler(call.message, handle_broadcast_message)
    elif call.data == 'ban_user':
        bot.send_message(call.message.chat.id, "يرجى كتابة معرف المستخدم لحظره.")
        bot.register_next_step_handler(call.message, handle_ban_user)
    elif call.data == 'uban_user':
        bot.send_message(call.message.chat.id, "يرجى كتابة معرف المستخدم لفك حظره.")
        bot.register_next_step_handler(call.message, handle_unban_user)

def stop_all_files(chat_id):
    stopped_files = []
    for chat_id, script_info in list(bot_scripts.items()):
        if stop_bot(script_info['path'], chat_id):
            stopped_files.append(script_info['name'])
    if stopped_files:
        bot.send_message(chat_id, f"تم إيقاف الملفات التالية بنجاح: {', '.join(stopped_files)}")
    else:
        bot.send_message(chat_id, "لا توجد ملفات قيد التشغيل لإيقافها.")

def start_all_files(chat_id):
    started_files = []
    for chat_id, script_info in list(bot_scripts.items()):
        if start_file(script_info['path'], chat_id):
            started_files.append(script_info['name'])
    if started_files:
        bot.send_message(chat_id, f"تم تشغيل الملفات التالية بنجاح: {', '.join(started_files)}")
    else:
        bot.send_message(chat_id, "لا توجد ملفات متوقفة لتشغيلها.")

def stop_bot(script_path, chat_id, delete=False):
    try:
        script_name = os.path.basename(script_path)
        process = bot_scripts.get(chat_id, {}).get('process')
        if process and psutil.pid_exists(process.pid):
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):  # Terminate all child processes
                child.terminate()
            parent.terminate()
            parent.wait()  # Ensure the process has been terminated
            bot_scripts[chat_id]['process'] = None
            if delete:
                os.remove(script_path)  # Remove the script if delete flag is set
                bot.send_message(chat_id, f"تم حذف {script_name} من الاستضافة.")
            else:
                bot.send_message(chat_id, f"تم إيقاف {script_name} بنجاح.")
            return True
        else:
            bot.send_message(chat_id, f"عملية {script_name} غير موجودة أو أنها قد توقفت بالفعل.")
            return False
    except psutil.NoSuchProcess:
        bot.send_message(chat_id, f"عملية {script_name} غير موجودة.")
        return False
    except Exception as e:
        print(f"Error stopping bot: {e}")
        bot.send_message(chat_id, f"حدث خطأ أثناء إيقاف {script_name}: {e}")
        return False

def start_file(script_path, chat_id):
    try:
        script_name = os.path.basename(script_path)
        if bot_scripts.get(chat_id, {}).get('process') and psutil.pid_exists(bot_scripts[chat_id]['process'].pid):
            bot.send_message(chat_id, f"الملف {script_name} يعمل بالفعل.")
            return False
        else:
            p = subprocess.Popen([sys.executable, script_path])
            bot_scripts[chat_id]['process'] = p
            bot.send_message(chat_id, f"تم تشغيل {script_name} بنجاح.")
            return True
    except Exception as e:
        print(f"Error starting bot: {e}")
        bot.send_message(chat_id, f"حدث خطأ أثناء تشغيل {script_name}: {e}")
        return False

@bot.message_handler(commands=['del'])
def delete_file(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        if message.reply_to_message:
            script_name = message.reply_to_message.text.strip()
        else:
            script_name = message.text.split(' ', 1)[1].strip()

        script_path = os.path.join(uploaded_files_dir, script_name)
        stop_bot(script_path, message.chat.id, delete=True)
        bot.reply_to(message, f"تم حذف ملف {script_name} بنجاح.")
        with open(script_path, 'rb') as file:
            bot.send_document(ADMIN_ID, file, caption=f"ملف محذوف: {script_name}")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة اسم الملف بعد الأمر أو الرد على رسالة.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

@bot.message_handler(commands=['stp'])
def stop_file_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        if message.reply_to_message:
            script_name = message.reply_to_message.text.strip()
        else:
            script_name = message.text.split(' ', 1)[1].strip()

        script_path = os.path.join(uploaded_files_dir, script_name)
        stop_bot(script_path, message.chat.id)
        bot.reply_to(message, f"تم إيقاف ملف {script_name} بنجاح.")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة اسم الملف بعد الأمر أو الرد على رسالة.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

@bot.message_handler(commands=['str'])
def start_file_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    try:
        if message.reply_to_message:
            script_name = message.reply_to_message.text.strip()
        else:
            script_name = message.text.split(' ', 1)[1].strip()

        script_path = os.path.join(uploaded_files_dir, script_name)
        start_file(script_path, message.chat.id)
        bot.reply_to(message, f"تم تشغيل ملف {script_name} بنجاح.")
    except IndexError:
        bot.reply_to(message, "يرجى كتابة اسم الملف بعد الأمر أو الرد على رسالة.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

@bot.message_handler(commands=['adm'])
def admin_panel(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    markup = types.InlineKeyboardMarkup()
    stop_all_button = types.InlineKeyboardButton("إيقاف جميع الملفات 🔴", callback_data='stop_all')
    start_all_button = types.InlineKeyboardButton("تشغيل جميع الملفات 🟢", callback_data='start_all')
    stop_bot_button = types.InlineKeyboardButton("إيقاف البوت بالكامل", callback_data='stop_bot')
    start_bot_button = types.InlineKeyboardButton("تشغيل البوت بالكامل", callback_data='start_bot')
    rck_button = types.InlineKeyboardButton("إرسال رسالة للجميع", callback_data='rck_all')
    ban_button = types.InlineKeyboardButton("حظر مستخدم", callback_data='ban_user')
    uban_button = types.InlineKeyboardButton("فك حظر مستخدم", callback_data='uban_user')
    
    markup.row(stop_all_button, start_all_button)
    markup.row(stop_bot_button, start_bot_button)
    markup.row(rck_button)
    markup.row(ban_button, uban_button)
    
    bot.send_message(message.chat.id, "5340258438", reply_markup=markup)

def stop_bot_server():
    bot.stop_polling()
    for chat_id, script_info in list(bot_scripts.items()):
        stop_bot(script_info['path'], chat_id)

def start_bot_server():
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def admin_callback_handler(call):
    if call.data == 'stop_bot':
        stop_bot_server()
        bot.send_message(call.message.chat.id, "تم إيقاف البوت بالكامل.")
    elif call.data == 'start_bot':
        start_bot_server()
        bot.send_message(call.message.chat.id, "تم تشغيل البوت بالكامل.")
    elif call.data == 'rck_all':
        bot.send_message(call.message.chat.id, "يرجى كتابة الرسالة لإرسالها للجميع.")
        bot.register_next_step_handler(call.message, handle_broadcast_message)
    elif call.data == 'ban_user':
        bot.send_message(call.message.chat.id, "يرجى كتابة معرف المستخدم لحظره.")
        bot.register_next_step_handler(call.message, handle_ban_user)
    elif call.data == 'uban_user':
        bot.send_message(call.message.chat.id, "يرجى كتابة معرف المستخدم لفك حظره.")
        bot.register_next_step_handler(call.message, handle_unban_user)
    elif call.data == 'stop_all':
        stop_all_files(call.message.chat.id)
    elif call.data == 'start_all':
        start_all_files(call.message.chat.id)

def handle_broadcast_message(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    msg = message.text
    for chat_id in bot_scripts.keys():
        bot.send_message(chat_id, msg)
    bot.reply_to(message, "تم إرسال الرسالة بنجاح.")

def handle_ban_user(message):
    if str(message.from_user.id) != ADMIN_ID: 5340258438
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    username = message.text.strip('@')
    if username in banned_users:
        bot.reply_to(message, f"المستخدم @{username} محظور بالفعل.")
    else:
        banned_users.add(username)
        bot.reply_to(message, f"تم حظر المستخدم @{username}.")

def handle_unban_user(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "ليس لديك صلاحية استخدام هذا الأمر.")
        return

    username = message.text.strip('@')
    if username not in banned_users:
        bot.reply_to(message, f"المستخدم @{username} ليس محظور.")
    else:
        banned_users.remove(username)
        bot.reply_to(message, f"تم فك حظر المستخدم @{username}.")

def stop_all_files(chat_id):
    stopped_files = []
    for chat_id, script_info in list(bot_scripts.items()):
        if stop_bot(script_info['path'], chat_id):
            stopped_files.append(script_info['name'])
    if stopped_files:
        bot.send_message(chat_id, f"تم إيقاف الملفات التالية بنجاح: {', '.join(stopped_files)}")
    else:
        bot.send_message(chat_id, "لا توجد ملفات قيد التشغيل لإيقافها.")

def start_all_files(chat_id):
    started_files = []
    for chat_id, script_info in list(bot_scripts.items()):
        if start_file(script_info['path'], chat_id):
            started_files.append(script_info['name'])
    if started_files:
        bot.send_message(chat_id, f"تم تشغيل الملفات التالية بنجاح: {', '.join(started_files)}")
    else:
        bot.send_message(chat_id, "لا توجد ملفات متوقفة لتشغيلها.")

# ضمان تشغيل نسخة واحدة فقط من البوت
if __name__ == "__main__":
    try:
        bot.polling()
    except Exception as e:
        print(f"Error: {e}")
