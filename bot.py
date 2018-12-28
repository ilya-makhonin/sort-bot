import telebot
from sql import sql_method as db
from constants import *
import config
import multiprocessing
import time


bot = telebot.TeleBot(config.token)


def get_markup(buttons, rows=1):
    markup = telebot.types.ReplyKeyboardMarkup(True, True, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons, level=False, page=1):
    result = []
    if level is not False:
        result.append(level)
    for button in buttons:
        result.append(button[-1])
    if len(result) > 20:
        pass
        # if page > 1:
        #     result = result[page * 10: (page * 10) + 20]
        #     result.append('Вернуться назад')
        # else:
        #     result = result[0:20]
        # result.append('Смотреть дальше')
    return get_markup(result)


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    name = message.from_user.first_name
    if name is None:
        name = message.from_user.last_name
    db.add_user(message.from_user.id, message.from_user.username, name)
    db.change_state('starting', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=start_message,
        parse_mode='markdown',
        reply_markup=get_markup(main_menu))


@bot.message_handler(commands=['downloadarticles'])
def download_articles(message: telebot.types.Message):
    admins_list = [i[1] for i in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        pass
        # авторы|темы|название|ссылка|


@bot.message_handler(regexp=first_level_back)
def back_to_main_menu(message: telebot.types.Message):
    db.change_state('starting', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        'Go back, bro!',
        reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.send_message(
        message.from_user.id,
        text=start_message,
        parse_mode='markdown',
        reply_markup=get_markup(main_menu))


@bot.message_handler(regexp='По авторам')
def author_handler(message: telebot.types.Message):
    db.change_state('author', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=hello_author_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_info_by_choice('author'), first_level_back)
    )


@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == 'author')
def author_list_articles(message: telebot.types.Message):
    db.change_state('author_choice', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=author_mes.format(message.text),
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_articles('author', message.text), back_to_author))


@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == 'author_choice')
def get_article_author(message: telebot.types.Message):
    if message.text == back_to_author:
        db.change_state('author', message.from_user.id)
        author_handler(message)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


@bot.message_handler(regexp='По темам')
def theme_handler(message: telebot.types.Message):
    db.change_state('theme', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=hello_theme_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back)
    )


@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == 'theme')
def theme_list_articles(message: telebot.types.Message):
    db.change_state('theme_choice', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=theme_mes.format(message.text),
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_articles('theme', message.text), back_to_theme))


@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == 'theme_choice')
def get_article_theme(message: telebot.types.Message):
    if message.text == back_to_theme:
        db.change_state('theme', message.from_user.id)
        theme_handler(message)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


@bot.message_handler(regexp='Я сам выберу')
def all_articles_handler(message: telebot.types.Message):
    db.change_state('all_articles', message.from_user.id)
    bot.send_message(
        message.from_user.id,
        text=hello_all_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_articles('all'), first_level_back))


@bot.message_handler(func=lambda message: db.get_state(message.from_user.id) == 'all_articles')
def all_list_articles(message: telebot.types.Message):
    article = db.get_article(message.text)
    bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


def args_check(args_names, checking_kwargs):
    """
    :param args_names: <list> names of variables
    :param checking_kwargs: <map/kwargs> map with variables names and variables by itself
    :return: True if all vars in kwargs, False else
    """
    for arg in args_names:
        if checking_kwargs.get(arg) is None:
            return False
    return True


def bot_start(use_webhook=False, webhook_data=dict):
    def set_webhook(url, cert):
        try:
            telebot.apihelper.set_webhook(config.token, url=url, certificate=cert)
        except Exception as err:
            print(err.with_traceback(None))

    def webhook_isolated_run(url, cert):
        multiprocessing.Process(target=set_webhook, args=(url, cert), daemon=True).start()

    global bot, states

    # telebot.logger.setLevel(logging.DEBUG)
    # telebot.logger.addHandler(log.__file_handler('logs.log', log.__get_formater()))

    if not use_webhook:
        bot.remove_webhook()
        bot.polling(none_stop=True)

    elif args_check(['webhook_ip', 'webhook_port', 'token', 'ssl_cert'], webhook_data):
        bot.remove_webhook()
        time.sleep(1)

        webhook_isolated_run(url='https://%s:%s/%s/' % (webhook_data.get('webhook_ip'),
                                                        webhook_data.get('webhook_port'),
                                                        webhook_data.get('token')),
                             cert=open(webhook_data.get('ssl_cert'), 'r'))
        return bot
    else:
        raise Exception('Params for start with webhook is not specified')

    return bot


if __name__ == '__main__':
    bot.polling(none_stop=True)
