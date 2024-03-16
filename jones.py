import telebot 
from telebot import types
import re
import clock

with open('api_key.txt', 'r') as file : api_key = file.readline().strip()
chat_permissions_dict = {}
chat_mute_clocks_dict = {}

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

bot = telebot.TeleBot(api_key)

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_message(message):
    bot.send_message(message.chat.id, "Permission to join your group requested")


@bot.message_handler(commands=['mute'])
def handle_mute_command(message):

    chat = message.chat
    user = message.from_user

    mute_permissions = types.ChatPermissions(can_send_messages=False)
    if  is_admin(message):
        if len(message.text.split()) > 1:
            time_range = ' '.join(message.text.split()[1:])
            if time_range_pattern.match(time_range):
                if can_mute_all(chat.id):
                    chat_mute_clocks_dict.setdefault(chat.id, []).append(time_range)
                    chat_mute_clocks_dict[chat.id] = list(set(chat_mute_clocks_dict[chat.id]))#remove dupplications
                    chat_mute_clocks_dict[chat.id] = clock.No_clock_interference(chat_mute_clocks_dict[chat.id])#manage interferences
                    clocks_strings = '\n'.join(chat_mute_clocks_dict[chat.id])
                    bot.reply_to(message, f"These designated times are established as periods during which communication is restricted:\n{clocks_strings}")
                else: bot.reply_to(message, "admin nistam")
            else:
                bot.reply_to(message, "The time range format provided is invalid. Kindly adhere to the standard HH:MM-HH:MM format, as exemplified: 12:30-16:20.")
        else:
            bot.reply_to(message, "After executing the /mute command, kindly furnish a time range following the format HH:MM-HH:MM, as exemplified: 12:30-16:20.")
    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")
    return

bot.infinity_polling()