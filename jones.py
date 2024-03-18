import telebot 
from telebot import types
import re
import clock
import json
import schedule
import time
import pytz
from datetime import datetime



tzone = "Iran"

with open('api_key.txt', 'r') as file : api_key = file.readline().strip()
bot = telebot.TeleBot(api_key)
def json_int_keys_pairs_hook(pairs):
    result = {}
    for key, value in pairs:
        try:
            # Try to convert the key to an integer
            key = int(key)
        except ValueError:
            # If conversion fails, keep it as it is
            pass
        result[key] = value
    return result

def save_dicts_to_file(chat_mute_clocks_dict, filename):
    with open(filename, 'w') as file:
        json.dump((chat_mute_clocks_dict), file)

def load_dicts_from_file(filename):
    try:
        with open(filename, 'r') as file:
            chat_mute_clocks_dict = json.load(file , object_pairs_hook=json_int_keys_pairs_hook)
    except FileNotFoundError:
        chat_mute_clocks_dict= {}
    return chat_mute_clocks_dict


chat_mute_clocks_dict = load_dicts_from_file("dicts.jason")


def mute_group(chat_id):
    mute_permissions = bot.get_chat(chat_id).permissions
    mute_permissions.can_send_messages = False
    bot.set_chat_permissions(chat_id, mute_permissions)
    bot.send_message(chat_id , "The designated time for silenceunmute_permissions = types.ChatPermissions(can_send_messages=True) has now commenced. All communication is hereby prohibited. I respectfully request that the admins refrain from engaging in chat.")
    
def unmute_group(chat_id):
    unmute_permissions = bot.get_chat(chat_id).permissions
    unmute_permissions.can_send_messages = True
    bot.set_chat_permissions(chat_id, unmute_permissions)
    bot.send_message(chat_id , "The designated time for silence has concluded! Communication may now resume without restriction.")

def send_warn(chat_id , min):
    bot.send_message(chat_id, f"Attention! The group is scheduled for closure in precisely {min} minutes. Prepare yourselves accordingly!")



def schedule_mute(chat_mute_clocks_dict):
    schedule.clear()
    for key in chat_mute_clocks_dict.keys():
        chat_id = key
        mute_time , unmute_time = clock.split_clocks(chat_mute_clocks_dict[key])
        current_time = datetime.now(pytz.timezone(tzone))
        for times in mute_time:
            hour, minute = map(int, times.split(':'))
            schedule_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(mute_group, key)
        for times in mute_time:
            mins = {5 , 15 , 30 , 60}
            for min in mins:
                hour , minute = clock.reduce_rime(times , min)
                schedule_time = current_time.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                schedule.every().day.at(schedule_time.strftime("%H:%M")).do(send_warn, key , min)
        for times in unmute_time:
            hour, minute = map(int, times.split(':'))
            schedule_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(unmute_group, key)

schedule_mute(chat_mute_clocks_dict)

time_range_pattern = re.compile(r'^\d{2}:\d{2}-\d{2}:\d{2}$')


def is_admin(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    admins = bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False
def can_mute_all(chat_id):
    bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
    if bot_member.status in ['administrator', 'creator'] and bot_member.can_restrict_members:
        return True
    else:
        return False
def send_status(chat_id):
    if (chat_id in chat_mute_clocks_dict):
        clocks_strings = '\n'.join(chat_mute_clocks_dict[chat_id])
        bot.send_message(chat_id, f"These designated times are established as periods during which communication is restricted:\n{clocks_strings}")
    else : bot.send_message(chat_id,"There are presently no established time periods for group silence.")



@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_message(message):
    bot.send_message(message.chat.id, "Permission to join your group requested")


@bot.message_handler(commands=['mute'])
def handle_mute_command(message):

    chat = message.chat
    user = message.from_user


    if  is_admin(message):
        if len(message.text.split()) > 1:
            time_range = ' '.join(message.text.split()[1:])
            if time_range_pattern.match(time_range):
                if can_mute_all(chat.id):
                    chat_mute_clocks_dict.setdefault(chat.id, []).append(time_range)
                    chat_mute_clocks_dict[chat.id] = list(set(chat_mute_clocks_dict[chat.id]))#remove dupplications
                    chat_mute_clocks_dict[chat.id] = clock.No_clock_interference(chat_mute_clocks_dict[chat.id])#manage interferences
                    save_dicts_to_file(chat_mute_clocks_dict, "dicts.jason")
                    print(chat_mute_clocks_dict)
                    send_status(chat.id)
                    schedule_mute(chat_mute_clocks_dict)
                else: bot.reply_to(message, "it appears an issue has arisen. It's plausible that I lack the necessary administrative privileges or permissions to enact the mute function.")
            else:
                bot.reply_to(message, "The time range format provided is invalid. Kindly adhere to the standard HH:MM-HH:MM format, as exemplified: 12:30-16:20.")
        else:
            bot.reply_to(message, "After executing the /mute command, kindly furnish a time range following the format HH:MM-HH:MM, as exemplified: 12:30-16:20.")
    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")
    return

@bot.message_handler(commands=['clear'])
def handle_mute_command(message):
    if is_admin(message):
        del chat_mute_clocks_dict[message.chat.id]
        save_dicts_to_file(chat_mute_clocks_dict , "dicts.jason")
        bot.send_message(message.chat.id , "The time periods for silence have been successfully lifted.")
    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")

@bot.message_handler(commands=['get_status'])
def handle_get_status(message):
    send_status(message.chat.id)

def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
import threading
scheduler_thread = threading.Thread(target=scheduler)
scheduler_thread.start()

bot.infinity_polling()