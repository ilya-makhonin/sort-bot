import telebot
from sql import sql_method as db
from configuration import *


bot = telebot.TeleBot('token')


def get_markup(buttons, rows=1):
    markup = telebot.types.ReplyKeyboardMarkup(True, True, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons, level=False):
    result = []
    for button in buttons:
        result.append(button[-1].capitalize())
    if level is not False:
        result.append(level)
    return get_markup(result)


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    name = message.from_user.first_name
    if name is None:
        name = message.from_user.last_name
    db.add_user(message.from_user.id, message.from_user.username, name)
    bot.send_message(message.from_user.id, start_message,
                     parse_mode='markdown', reply_markup=get_markup(main_menu))


@bot.message_handler(regexp='По авторам')
def author_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id, author_mes,
        reply_markup=pre_modified_button(db.get_info_by_choice('author'), first_level_back)
    )


def author_list_articles(message: telebot.types.Message):
    pass


@bot.message_handler(regexp='По темам')
def theme_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id, theme_mes,
        reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back)
    )


@bot.message_handler(regexp='По уровню')
def level_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, level_mes, reply_markup=get_markup(main_menu))


@bot.message_handler(regexp='Я сам выберу')
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, all_mes, reply_markup=get_markup(main_menu))


@bot.message_handler(regexp=first_level_back)
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, start_message, reply_markup=get_markup(main_menu))


if __name__ == '__main__':
    bot.polling(none_stop=True)
