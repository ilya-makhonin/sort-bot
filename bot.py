import telebot
from sql import sql_method as db
from constants import *
import config
import time
import log
import logging
from states import get_full_state, check_section, change_state


bot = telebot.TeleBot(config.token)


def get_markup(buttons, rows=1):
    """
    :param buttons: buttons list type <list> like [button name, button name, ...]
    :param rows: rows width count
    :return: bot markup type '<telebot.types.ReplyKeyboardMarkup object at 0x000001819664CCF8>'
    """
    markup = telebot.types.ReplyKeyboardMarkup(True, False, row_width=rows)
    markup.add(*buttons)
    return markup


def pre_modified_button(buttons,  level=False, start=0, finish=20):
    """
    :param buttons: buttons list type <tuple> like ((..., name)(..., name), ...)
    :param level: to back level markup
    :param start: start split diapason type <int>
    :param finish: finish split diapason type <int>
    :return: bot markup type '<telebot.types.ReplyKeyboardMarkup object at 0x000001819664CCF8>'
    """
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
    """
    :param message: Message object with data about user, chat, etc type <class>
    :param back_to: Back to location (main menu, author/theme list) type <str>
    :return: return nothing
    """
    state_user = get_full_state(message.from_user.id)
    # If state equally starting or author - don't action
    if state_user[0] == state['st'] or state_user[0] == state['at']:
        return
    if state_user[0] == state['th']:   # If state equally theme - getting theme list
        buttons = db.get_info_by_choice(state_user[0])
    else:   # If state equally all or author_choice or theme_choice - getting buttons by condition
        table = state_user[0].split('_')[0]   # [all, theme, author]
        condition = state_user[3] if len(state_user) == 4 else ''  # [author name, theme name, empty string]
        buttons = db.get_articles(table, condition)

    category = state_user[3] if len(state_user) == 4 else None   # Create category buttons or None
    if message.text == 'Далее':
        bot.send_message(
            message.from_user.id, text='Далее', parse_mode='markdown',
            reply_markup=pre_modified_button(buttons, back_to, state_user[1] + 20, state_user[2] + 20))
        change_state(message.from_user.id, state_user[0],
                     '{}:{}'.format(state_user[1] + 20, state_user[2] + 20), category)
    if message.text == 'Назад':
        start = state_user[1] - 20 if state_user[1] - 20 >= 0 else 0
        finish = state_user[2] - 20 if state_user[2] - 20 >= 20 else 20
        bot.send_message(message.from_user.id, text='Назад', parse_mode='markdown',
                         reply_markup=pre_modified_button(buttons, back_to, start, finish))
        change_state(message.from_user.id, state_user[0], '{}:{}'.format(start, finish), category)


def article_by(message, state_type, table, back_to, mess):
    """
    :param message: Message object with data about user, chat, etc type <class>
    :param state_type: New user state type <str>
    :param table: The Table from which data will be received type <str>
    :param back_to: Section where the user will be returned type <str>
    :param mess: Message to show to user type <str>
    """
    bot.send_message(message.from_user.id, mess.format(message.text), parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_articles(table, message.text), back_to))
    change_state(message.from_user.id, state_type, '0:20', message.text)


def article_choice(message, back_to, handler):
    """
    :param message: Message object with data about user, chat, etc type <class>
    :param back_to: Section where the user will be returned type <str>
    :param handler: Handler for return back type <func>
    :return:
    """
    if message.text == back_to:
        handler(message)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


# *************************************** Start handler ***************************************
# *********************************************************************************************
@bot.message_handler(commands=['start'])
def start_handler(message: telebot.types.Message):
    name = message.from_user.first_name
    if name is None:
        name = message.from_user.last_name
    db.add_user(message.from_user.id, message.from_user.username, name)
    bot.send_message(
        message.from_user.id, start_message, parse_mode='markdown', reply_markup=get_markup(main_menu))


@bot.message_handler(commands=['help'])
def help_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, help_mes, parse_mode='markdown', reply_markup=get_markup(main_menu))
# *********************************************************************************************
# *********************************************************************************************


# **************************************** Admin panel ****************************************
# *********************************************************************************************
@bot.message_handler(commands=['helping'])
def helping_handler(message: telebot.types.Message):
    admins_list = [admin[1] for admin in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        bot.send_message(message.from_user.id, helping_text, parse_mode='markdown')


@bot.message_handler(commands=['global'])
def global_mailing(message: telebot.types.Message):
    admins_list = [admin[1] for admin in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        text = message.text[8:].strip()
        if text == '':
            bot.send_message(message.from_user.id, 'Вы не ввели текст рассылки!')
        else:
            users_id = [user[1] for user in db.get_info_by_choice('users')]
            for user_id in users_id:
                try:
                    bot.send_message(user_id, text, parse_mode='HTML')
                except Exception:
                    continue


@bot.message_handler(commands=['downloadarticle'])
def download_articles(message: telebot.types.Message):
    admins_list = [admin[1] for admin in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        article = message.text[17:].split('|')   # like ['authors', 'themes', 'name', 'link']
        if len(article) < 4:
            bot.send_message(message.from_user.id, download_incorrect, parse_mode='HTML')
        else:
            # format authors string type <list> like ['Naize', ...]
            authors = [(author.replace('#', '')) for author in article[0].split(' ')]
            # format themes string type <list> like ['Frontend', ...]
            themes = [(theme.replace('#', '')) for theme in article[1].split(' ')]

            # Validation of input data (authors and themes)
            author_correct = db.check_author(authors)       # return type <list> like [1, 2, 3]
            theme_correct = db.check_theme(themes)          # return type <list> like [<int>,...]
            if not author_correct or not theme_correct:
                download_error = 'Отчёт:\n\n'
                if not author_correct:
                    download_error += author_error + '\n'
                if not theme_correct:
                    download_error += theme_error
                bot.send_message(message.from_user.id, download_error)
            else:
                article_id = db.add_article(article[2].strip(), article[3].strip())   # get id of a article type <int>
                if not article_id:
                    bot.send_message(message.from_user.id,
                                     'Статья с таким названием уже существует! Используйте другое название')
                    return
                db.add_relation_to_article(author_correct, theme_correct, article_id)   # set many to many relationship
                bot.send_message(message.from_user.id, download_success)


@bot.message_handler(commands=['downloadtheme'])
def download_theme(message: telebot.types.Message):
    admins_list = [admin[1] for admin in db.get_info_by_choice('author')]
    if message.from_user.id in admins_list:
        theme_name = (message.text[15:].replace('#', '')).strip()
        if theme_name == '':
            bot.send_message(message.from_user.id, 'Вы не ввели тему!')
        else:
            result = db.add_theme(theme_name)
            if not result:
                bot.send_message(message.from_user.id, 'Данная тема уже существует!')
            else:
                bot.send_message(message.from_user.id, 'Тема *{}* успешно добавленна!'.format(theme_name),
                                 parse_mode='markdown')
# *********************************************************************************************
# *********************************************************************************************


# *********** Back to main menu (Article by author, Article by theme, All articles) ***********
# *********************************************************************************************
@bot.message_handler(func=lambda message: message.text == first_level_back)
def back_to_main_menu(message: telebot.types.Message):
    change_state(message.from_user.id, state['st'])
    bot.send_message(message.from_user.id, 'Come back, bro!', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.send_message(message.from_user.id, start_message, parse_mode='markdown', reply_markup=get_markup(main_menu))
# *********************************************************************************************
# *********************************************************************************************


# *************************************** Get by state ***************************************
# ********************************************************************************************
@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['at']))
def author_list_articles(message: telebot.types.Message):
    article_by(message, state['ac'], 'author', back_to_author, author_mes)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['ac']))
def get_article_author(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_author)
    else:
        article_choice(message, back_to_author, author_handler)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['th']))
def theme_list_articles(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        article_by(message, state['tc'], 'theme', back_to_theme, theme_mes)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['tc']))
def get_article_theme(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_theme)
    else:
        article_choice(message, back_to_theme, theme_handler)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['al']))
def all_list_articles(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['ot']))
def get_other_article(message: telebot.types.Message):
    article_by(message, state['oc'], 'other', back_to_other, other_mes)


@bot.message_handler(func=lambda message: check_section(message.from_user.id, state['oc']))
def get_other_choice(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_other)
    else:
        article_choice(message, back_to_other, other_articles_handler)
# ********************************************************************************************
# ********************************************************************************************


# ************************************* Section handlers *************************************
# ********************************************************************************************
@bot.message_handler(func=lambda x: x.text == 'По авторам')
def author_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_author_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('author'), first_level_back))
    change_state(message.from_user.id, state['at'])


@bot.message_handler(func=lambda x: x.text == 'По темам')
def theme_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_theme_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back))
    change_state(message.from_user.id, state['th'], '0:20')


@bot.message_handler(func=lambda x: x.text == 'Я сам выберу! Покажите все статьи')
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_all_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_articles('all'), first_level_back))
    change_state(message.from_user.id, state['al'], '0:20')


@bot.message_handler(func=lambda x: x.text == 'Other. Гости, интервью, и многое другое')
def other_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_other_mes, parse_mode='markdown',
                     reply_markup=get_markup(other_section))
    change_state(message.from_user.id, state['ot'])
# ********************************************************************************************
# ********************************************************************************************


# ************************************ Bot start function *************************************
# *********************************************************************************************
def bot_start(webhook_data, use_webhook=False, logging_enable=False):
    """
    :param webhook_data: data for deploy type <dict>
    :param use_webhook: type <bul>
    :param logging_enable: type <bul>
    :return: bot object
    """
    global bot

    def set_webhook(url, cert):
        try:
            # telebot.apihelper.set_webhook(config.token, url=url, certificate=cert)
            bot.set_webhook(url=url, certificate=cert)
        except Exception as err:
            print(err.with_traceback(None))

    def args_check(args_names, checking_kwargs):
        for arg in args_names:
            if checking_kwargs.get(arg) is None:
                return False
        return True

    if logging_enable:
        telebot.logger.setLevel(logging.WARNING)
        telebot.logger.addHandler(log.__file_handler('./logs/bot.log', log.__get_formatter()))

    if not use_webhook:
        bot.remove_webhook()
        time.sleep(1)
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
