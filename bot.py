import telebot
from sql import sql_method as db
from configuration import *
import token_for_bot as tfb


bot = telebot.TeleBot(tfb.token)
cash = {
    'author': list(),
    'theme': list(),
    'level': list()
}


def get_db_information():
    cash['author'] = db.get_info_by_choice('author')
    cash['theme'] = db.get_info_by_choice('theme')
    cash['level'] = db.get_info_by_choice('level')


def get_markup(buttons, rows=1):
    markup = telebot.types.ReplyKeyboardMarkup(True, True, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons, level=False):
    result = []
    for button in buttons:
        result.append(button[-1])
    if level is not False:
        result.append(level)
    return get_markup(result)


def back_to_main_menu(message: telebot.types.Message):
    bot.send_message(message.from_user.id, 'Go back, bro!', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.send_message(message.from_user.id, start_message, reply_markup=get_markup(main_menu))


# def actions_handler(message):
#     second_level = second_level_back.format('авторов')
#     if message.text == first_level_back:
#         back_to_main_menu(message)
#     elif message.text == second_level:
#         author_handler(message)
#     else:
#         bot.send_message(message.from_user.id, second_level, reply_markup=pre_modified_button([], second_level))
#         bot.register_next_step_handler_by_chat_id(message.from_user.id, author_list_articles)


def get_articles():
    pass


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
    bot.register_next_step_handler_by_chat_id(message.from_user.id, author_list_articles)


def author_list_articles(message: telebot.types.Message):
    second_level = second_level_back.format('авторов')
    if message.text == first_level_back:
        back_to_main_menu(message)
    elif message.text == second_level:
        author_handler(message)
    else:
        bot.send_message(
            message.from_user.id, second_level,
            reply_markup=pre_modified_button([], second_level))
        bot.register_next_step_handler_by_chat_id(message.from_user.id, author_list_articles)


@bot.message_handler(regexp='По темам')
def theme_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id, theme_mes,
        reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back)
    )
    bot.register_next_step_handler_by_chat_id(message.from_user.id, theme_list_articles)


def theme_list_articles(message: telebot.types.Message):
    second_level = second_level_back.format('тем')
    if message.text == first_level_back:
        back_to_main_menu(message)
    elif message.text == second_level:
        theme_handler(message)
    else:
        bot.send_message(
            message.from_user.id, second_level,
            reply_markup=pre_modified_button([], second_level))
        bot.register_next_step_handler_by_chat_id(message.from_user.id, theme_list_articles)


@bot.message_handler(regexp='По уровню')
def level_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id, level_mes,
        reply_markup=get_markup(main_menu))
    bot.register_next_step_handler_by_chat_id(message.from_user.id, level_list_articles)


def level_list_articles(message: telebot.types.Message):
    second_level = second_level_back.format('уровней')
    if message.text == first_level_back:
        back_to_main_menu(message)
    elif message.text == second_level:
        level_handler(message)
    else:
        bot.send_message(message.from_user.id, second_level, reply_markup=pre_modified_button([], second_level))
        bot.register_next_step_handler_by_chat_id(message.from_user.id, level_list_articles)


@bot.message_handler(regexp='Я сам выберу')
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, all_mes, reply_markup=get_markup(main_menu))
    bot.register_next_step_handler_by_chat_id(message.from_user.id, all_list_articles)


def all_list_articles(message: telebot.types.Message):
    if message.text == first_level_back:
        back_to_main_menu(message)
    else:
        bot.send_message(
            message.from_user.id, first_level_back,
            reply_markup=pre_modified_button([], first_level_back))
        bot.register_next_step_handler_by_chat_id(message.from_user.id, all_list_articles)


if __name__ == '__main__':
    bot.polling(none_stop=True)
