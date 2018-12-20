import telebot
from sql import sql_method as db
from configuration import *
import pprint


bot = telebot.TeleBot('token')


def get_markup(buttons, rows=1):
    markup = telebot.types.ReplyKeyboardMarkup(True, True, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons):
    result = []
    for button in buttons:
        result.append([button[-1].capitalize(), button[0]])


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    name = message.from_user.first_name
    if name is None:
        name = message.from_user.last_name
    db.add_user(message.from_user.id, message.from_user.username, name)
    bot.send_message(message.from_user.id, start_message, parse_mode='markdown')


if __name__ == '__main__':
    bot.polling(none_stop=True)
