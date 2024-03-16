import telebot 
import re

with open('api_key.txt', 'r') as file : api_key = file.readline().strip()

time_range_pattern = re.compile(r'^\d{2}:\d{2}-\d{2}:\d{2}$')
def is_admin(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    admins = bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False

bot = telebot.TeleBot(api_key)

@bot.message_handler(func=lambda message: message.chat.type == 'private')
def private_message(message):
    bot.send_message(message.chat.id, "Permission to join your group requested")


@bot.message_handler(commands=['mute'])
def handle_mute_command(message):

    chat_id = message.chat.id
    user = message.from_user

    if  is_admin(message):
        if len(message.text.split()) > 1:
            time_range = ' '.join(message.text.split()[1:])
            if time_range_pattern.match(time_range):
                print(time_range)
                bot.reply_to(message, f"Time range copied: {time_range}")
            else:
                bot.reply_to(message, "The time range format provided is invalid. Kindly adhere to the standard HH:MM-HH:MM format, as exemplified: 12:30-16:20.")
        else:
            bot.reply_to(message, "After executing the /mute command, kindly furnish a time range following the format HH:MM-HH:MM, as exemplified: 12:30-16:20.")
    else: bot.reply_to(message, "Respectfully, it appears you lack the necessary administrative privileges. Orders can only be accepted from those holding the esteemed position of admin, as per protocol.")
    return

bot.infinity_polling()