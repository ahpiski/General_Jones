import telebot 
from telebot import types
import re
import clock
import json
import schedule
import time
import pytz
from datetime import datetime





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

def save_to_file(dict, filename):
    with open(filename, 'w') as file:
        json.dump((dict), file)

def load_from_file_dict(filename):
    try:
        with open(filename, 'r') as file:
            dict = json.load(file , object_pairs_hook=json_int_keys_pairs_hook)
    except FileNotFoundError:
            dict= {}
    return dict

def load_from_file_list(filename):
    try:
        with open(filename, 'r') as file:
            the_list = json.load(file)
    except FileNotFoundError:
            the_list= list()
    return the_list

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
        bot.send_message(chat_id, f"These designated times are established as periods during which communication is restricted:\n<b>{clocks_strings}</b>" , "HTML")
    else : bot.send_message(chat_id,"There are presently <b>no established time periods</b> for group silence." , "HTML")


chat_mute_clocks_dict = load_from_file_dict("mute_clocks_dict.jason")
chat_ids_to_delete    = load_from_file_list("delete_list.jason")

def mute_group(chat_id):
    permissions = bot.get_chat(chat_id).permissions
    mute_permissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_invite_users=permissions.can_invite_users,
        can_pin_messages=permissions.can_pin_messages,
        can_change_info=permissions.can_change_info,
        can_manage_topics=permissions.can_manage_topics
    )
    bot.set_chat_permissions(chat_id, mute_permissions)
    bot.send_message(chat_id , "The designated time for silence has now commenced.<b>All communication is hereby prohibited</b>. I respectfully request that the admins refrain from engaging in chat." , "HTML")
    
def unmute_group(chat_id):
    permissions = bot.get_chat(chat_id).permissions
    unmute_permissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=permissions.can_invite_users,
        can_pin_messages=permissions.can_pin_messages,
        can_change_info=permissions.can_change_info,
        can_manage_topics=permissions.can_manage_topics
    )
    bot.set_chat_permissions(chat_id, unmute_permissions)
    bot.send_message(chat_id , "<b>The designated time for silence has concluded!</b> Communication may now resume without restriction." , "HTML")

def send_warn(chat_id , min):
    bot.send_message(chat_id, f"<b>Attention!</b> The group is scheduled for closure in precisely <b>{min}</b> minutes. <b>Prepare yourselves accordingly!</b>" , "HTML")

def say_hello(chat_id):
    bot.send_message(chat_id, "General Jones here, ready to enforce order. Tell me the time and I'll lock down the chat for maximum focus. Remember, discipline is key!")
    bot.send_message(chat_id, "To obtain a list of available commands, simply use /help.")
    bot.send_message(chat_id, "I should be granted admin status and have the required permissions.")
def do_delete(status ,chat_id):
    global chat_ids_to_delete
    if not (can_mute_all(chat_id)):
        bot.send_message(chat_id , "it appears an issue has arisen. It's plausible that <b>I lack the necessary administrative privileges or permissions</b> to enact the mute function." , "HTML")
        return
    if(status):
        bot.send_message(chat_id , "<b>Now is the time for silence.</b> I will proceed to clear messages, except for those from admins. Moreover, I request that admins abstain from initiating any chat during this period." , "HTML")
        chat_ids_to_delete.append(chat_id)
        chat_ids_to_delete = list(set(chat_ids_to_delete))
        save_to_file(chat_ids_to_delete , 'delete_list.jason' )
    else:
        bot.send_message(chat_id , "<b>The period of silence has ended.</b> All members are now free to engage in chat." , "HTML")
        if (chat_id in chat_ids_to_delete): chat_ids_to_delete.remove(chat_id) 
        save_to_file(chat_ids_to_delete , 'delete_list.jason' )

def schedule_mute(chat_mute_clocks_dict):
    schedule.clear()
    for key in chat_mute_clocks_dict.keys():
        chat_id = key
        mute_time , unmute_time = clock.split_clocks(chat_mute_clocks_dict[key])
        current_time = datetime.now(pytz.timezone(clock.tzone))
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

def schedule_delete(chat_mute_clocks_dict):
    schedule.clear()
    for key in chat_mute_clocks_dict.keys():
        chat_id = key
        mute_time , unmute_time = clock.split_clocks(chat_mute_clocks_dict[key])
        current_time = datetime.now(pytz.timezone(clock.tzone))
        for times in mute_time:
            hour, minute = map(int, times.split(':'))
            schedule_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(do_delete,True, key)
        for times in mute_time:
            mins = {5 , 15 , 30 , 60}
            for min in mins:
                hour , minute = clock.reduce_rime(times , min)
                schedule_time = current_time.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                schedule.every().day.at(schedule_time.strftime("%H:%M")).do(send_warn, key , min)
        for times in unmute_time:
            hour, minute = map(int, times.split(':'))
            schedule_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(do_delete,False,key)

schedule_mute(chat_mute_clocks_dict)

time_range_pattern = re.compile(r'^(?:[01]\d|2[0-4]):(?:[0-5]\d)-(?:[01]\d|2[0-4]):(?:[0-5]\d)$')


@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_message(message):
    bot.send_message(message.chat.id, "Permission to join your group requested")


@bot.message_handler(commands=['clocks'])
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
                    save_to_file(chat_mute_clocks_dict, "mute_clocks_dict.jason")
                    send_status(chat.id)
                else: bot.reply_to(message, "it appears an issue has arisen. It's plausible that I lack the necessary administrative privileges or permissions to enact the mute function.")
            else:
                bot.reply_to(message, "The time range format provided is invalid. Kindly adhere to the standard HH:MM-HH:MM format, as exemplified: 12:30-16:20.")
        else:
            bot.reply_to(message, "After executing the /clocks command, kindly furnish a time range following the format HH:MM-HH:MM, as exemplified: 12:30-16:20.")

    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")
    return

@bot.message_handler(commands=['clear'])
def handle_mute_command(message):
    if is_admin(message):
        del chat_mute_clocks_dict[message.chat.id]
        if (message.chat.id in chat_ids_to_delete): chat_ids_to_delete.remove(message.chat.id) 
        save_to_file(chat_ids_to_delete , 'delete_list.jason' )
        save_to_file(chat_mute_clocks_dict , "mute_clocks_dict.jason")
        schedule_mute(chat_mute_clocks_dict)
        schedule_delete(chat_mute_clocks_dict)
        bot.send_message(message.chat.id , "The time periods for silence have been successfully lifted.")
    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")

@bot.message_handler(commands=['get_status'])
def handle_get_status(message):
    send_status(message.chat.id)

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message , "To establish mute time periods, issue the command /mute.\nTo clear the mute periods table, use /clear.\nFor a status update on mute time periods, use /get_status.\nTo mute the group, utilize /set mute. Conversely, for unmuting, issue /set unmute.")

@bot.message_handler(commands=['set'])
def handle_set(message):
    global chat_mute_clocks_dict
    set = ' '.join(message.text.split()[1:])
    if (is_admin(message)): 
        if(set == 'mute'): mute_group(message.chat.id)
        if(set == 'unmute'): unmute_group(message.chat.id)
        if(set == 'delete_on'): do_delete(True ,message.chat.id)
        if(set == 'delete_off'): do_delete(False , message.chat.id)
        if(set == 'delete_mode'):
            bot.reply_to(message , "Delete mode enabled! I will proceed to clear messages during the selected periods outlined in the clocks table.")
            schedule_delete(chat_mute_clocks_dict)
        if(set == 'mute_mode'):
            bot.reply_to(message ,"Mute mode enabled. I will proceed to mute the group during the selected periods outlined in the clocks table.")
            schedule_mute(chat_mute_clocks_dict)


@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def greet_new_members(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            say_hello(message.chat.id)
            break

@bot.message_handler(func=lambda message: True)
def delete_messages(message):
    chat_id = message.chat.id
    if is_admin(message):
        return
    if chat_id in chat_ids_to_delete:
        bot.delete_message(chat_id, message.message_id)


def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
import threading
scheduler_thread = threading.Thread(target=scheduler)
scheduler_thread.start()

bot.infinity_polling()