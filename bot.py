import telebot
from sql import sql_method as db
from constants import *
import config
# import multiprocessing
import time
import log
import logging
from states import get_full_state, check_section, change_state


bot = telebot.TeleBot(config.token)


def get_markup(buttons, rows=1):
    markup = telebot.types.ReplyKeyboardMarkup(True, True, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons,  level=False, start=0, finish=20):
    result = []
    # ***** Create buttons list *****
    if level is not False:
        result.append(level)
    for button in buttons[start:finish]:
        result.append(button[-1])
    if len(buttons) > finish:
        result.append('Далее')
    if start > 0:
        result.append('Назад')
    # *******************************
    return get_markup(result)


def next_back(message, back_to):
    state_user = get_full_state(message.from_user.id)
    button = tuple
    if state_user == 'starting' or state_user == 'author':
        return
    elif state_user[0] == 'all':
        buttons = db.get_articles(state_user[0])
    elif state_user[0] == 'theme':
        buttons = db.get_info_by_choice(state_user[0])
    else:
        buttons = db.get_articles()
    if message.text == 'Далее':
        bot.send_message(message.from_user.id, text='Далее', parse_mode='markdown',
                          reply_markup=pre_modified_button(buttons, back_to, state_user[1] + 20, state_user[2] + 20))
        change_state(message.from_user.id, state_user[0], pages='{}:{}'.format(state_user[1] + 20, state_user[2] + 20))
    if message.text == 'Назад':
        start = state_user[1] - 20 if state_user[1] - 20 >= 0 else 0
        finish = state_user[2] - 20 if state_user[2] - 20 >= 20 else 20
        bot.send_message(message.from_user.id, text='Назад', parse_mode='markdown',
                         reply_markup=pre_modified_button(buttons, back_to, start, finish))
        change_state(message.from_user.id, state_user[0], pages='{}:{}'.format(start, finish))


def article_by(message, state_type, table, back_to, mess):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to)
    else:
        bot.send_message(
            message.from_user.id,
            text=mess.format(message.text),
            parse_mode='markdown',
            reply_markup=pre_modified_button(db.get_articles(table, message.text), back_to))
        change_state(message.from_user.id, state_type, '0:20', message.text)


def article_choice(message, back_to, handler):
    if message.text == back_to:
        handler(message)
    elif message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    name = message.from_user.first_name
    if name is None:
        name = message.from_user.last_name
    db.add_user(message.from_user.id, message.from_user.username, name)
    bot.send_message(
        message.from_user.id,
        text=start_message,
        parse_mode='markdown',
        reply_markup=get_markup(main_menu))


# **************************************** Admin panel ****************************************
# *********************************************************************************************
@bot.message_handler(commands=['downloadarticle'])
def download_articles(message: telebot.types.Message):
    admins_list = [i[1] for i in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        article = message.text[18:].split('|')
        if len(article) < 4:
            bot.send_message(message.from_user.id, download_incorrect, parse_mode='HTML')
        else:
            authors = [(author.replace('#', '')).strip() for author in article[0].split(' ')]
            themes = [(theme.replace('#', '')).strip() for theme in article[1].split(' ')]
            author_correct = db.check_author(authors)
            theme_correct = db.check_theme(themes)
            download_error = 'Отчёт:\n\n'
            if not author_correct or not theme_correct:
                if not author_correct:
                    download_error += author_error + '\n'
                if not theme_correct:
                    download_error += theme_error
                bot.send_message(message.from_user.id, download_error)
            else:
                article_id = db.add_article(article[2].strip(), article[3].strip())
                db.add_relation_to_article(author_correct, theme_correct, article_id)
                bot.send_message(message.from_user.id, download_success)


@bot.message_handler(commands=['downloadtheme'])
def download_theme(message: telebot.types.Message):
    admins_list = [i[1] for i in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        theme_name = (message.text[15:].replace('#', '')).strip()
        if theme_name == '':
            bot.send_message(message.from_user.id, 'Вы не ввели тему!')
        else:
            result = db.add_theme(theme_name)
            if not result:
                bot.send_message(message.from_user.id, 'Данная тема уже существует!')
            else:
                bot.send_message(
                    message.from_user.id,
                    'Тема *{}* успешно добавленна!'.format(theme_name),
                    parse_mode='markdown')
# *********************************************************************************************
# *********************************************************************************************


# Back to main menu (Article by author, Article by theme, All articles)
@bot.message_handler(func=lambda message: message.text == first_level_back)
def back_to_main_menu(message: telebot.types.Message):
    change_state(message.from_user.id, state['st'])
    bot.send_message(
        message.from_user.id,
        'Go back, bro!',
        reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.send_message(
        message.from_user.id,
        text=start_message,
        parse_mode='markdown',
        reply_markup=get_markup(main_menu))


# *************************************** Get by state ***************************************
# ********************************************************************************************
@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['at']))
def author_list_articles(message: telebot.types.Message):
    article_by(message, state['ac'], 'author', back_to_author, author_mes)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['ac']))
def get_article_author(message: telebot.types.Message):
    article_choice(message, back_to_author, author_handler)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['th']))
def theme_list_articles(message: telebot.types.Message):
    article_by(message, state['tc'], 'theme', back_to_theme, theme_mes)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['tc']))
def get_article_theme(message: telebot.types.Message):
    article_choice(message, back_to_theme, theme_handler)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['al']))
def all_list_articles(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))
# ********************************************************************************************
# ********************************************************************************************


@bot.message_handler(regexp='По авторам')
def author_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id,
        text=hello_author_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_info_by_choice('author'), first_level_back))
    change_state(message.from_user.id, state['at'])


@bot.message_handler(regexp='По темам')
def theme_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id,
        text=hello_theme_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back))
    change_state(message.from_user.id, state['th'], '0:20')


@bot.message_handler(regexp='Я сам выберу')
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(
        message.from_user.id,
        text=hello_all_mes,
        parse_mode='markdown',
        reply_markup=pre_modified_button(db.get_articles('all'), first_level_back))
    change_state(message.from_user.id, state['al'], '0:20')


# ************************************ Bot start function *************************************
def bot_start(webhook_data, use_webhook=False):
    def set_webhook(url, cert):
        try:
            telebot.apihelper.set_webhook(config.token, url=url, certificate=cert)
        except Exception as err:
            print(err.with_traceback(None))

    # def webhook_isolated_run(url, cert):
    #     multiprocessing.Process(target=set_webhook, args=(url, cert), daemon=True).start()

    def args_check(args_names, checking_kwargs):
        for arg in args_names:
            if checking_kwargs.get(arg) is None:
                return False
        return True

    # global bot, states

    # telebot.logger.setLevel(logging.DEBUG)
    # telebot.logger.addHandler(log.__file_handler('logs.log', log.__get_formatter()))

    if not use_webhook:
        bot.remove_webhook()
        bot.polling(none_stop=True)
    elif args_check(['webhook_ip', 'webhook_port', 'token', 'ssl_cert'], webhook_data):
        bot.remove_webhook()
        time.sleep(1)
        set_webhook(
            url='https://%s:%s/%s/' % (
                webhook_data.get('webhook_ip'),
                webhook_data.get('webhook_port'),
                webhook_data.get('token')),
            cert=open(webhook_data.get('ssl_cert'), 'r'))
        return bot
    else:
        raise Exception('Params for start with webhook is not specified')
    return bot


if __name__ == '__main__':
    bot_start({})
