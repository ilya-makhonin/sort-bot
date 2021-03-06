import telebot
from sql import db
from constants import *
import config
from time import sleep
import log
import logging
from states import states as s
from utils import get_markup, pre_modified_button


bot = telebot.TeleBot(config.token)
logger_bot = log.logger('bot', 'bot.log', 'WARNING')


def next_back(message, back_to):
    """
    :param message: Message object with data about user, chat, etc type <class>
    :param back_to: Back to location (main menu, author/theme list) type <str>
    :return: return nothing
    """
    state_user = s.get_full_state(message.from_user.id)
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
        s.change_state(message.from_user.id, state_user[0],
                       '{}:{}'.format(state_user[1] + 20, state_user[2] + 20), category)
    if message.text == 'Назад':
        start = state_user[1] - 20 if state_user[1] - 20 >= 0 else 0
        finish = state_user[2] - 20 if state_user[2] - 20 >= 20 else 20
        bot.send_message(message.from_user.id, text='Назад', parse_mode='markdown',
                         reply_markup=pre_modified_button(buttons, back_to, start, finish))
        s.change_state(message.from_user.id, state_user[0], '{}:{}'.format(start, finish), category)


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
    s.change_state(message.from_user.id, state_type, '0:20', message.text)


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


# **************************************** Admin panel ****************************************
def check_admin(message):
    admins_list = [admin[1] for admin in db.get_info_by_choice('author')]
    return message.from_user.id in admins_list


@bot.message_handler(commands=['helping'])
def helping_handler(message: telebot.types.Message):
    if check_admin(message):
        bot.send_message(message.from_user.id, helping_text, parse_mode='markdown')


@bot.message_handler(commands=['global'])
def global_mailing(message: telebot.types.Message):
    if check_admin(message):
        text = message.text[8:].strip()
        if text == '':
            bot.send_message(message.from_user.id, 'Вы не ввели текст рассылки!')
        else:
            counter_deleted_users = 0
            users_id = [user[1] for user in db.get_info_by_choice('users')]
            for user_id in users_id:
                try:
                    bot.send_message(user_id, text, parse_mode='HTML')
                except Exception as error:
                    counter_deleted_users += 1
                    logger_bot.warning(error.with_traceback(None))
                    continue
            bot.send_message(message.from_user.id, 'Удалённых пользователей {}'.format(counter_deleted_users))


@bot.message_handler(commands=['downloadarticle'])
def download_articles(message: telebot.types.Message):
    if check_admin(message):
        article = message.text[17:].split('|')   # like ['authors', 'themes', 'name', 'link']
        if len(article) < 4:
            bot.send_message(message.from_user.id, download_incorrect, parse_mode='HTML')
        elif article[0].strip() == 'other':              # like ['other', 'section', 'themes', 'name', 'link']
            section = article[1].strip()
            themes = [(theme.replace('#', '')).strip() for theme in article[2].split(', ')]
            section_correct = db.check_author_or_section(section, other=True)
            theme_correct = db.check_theme(themes)
            if not section_correct or not theme_correct:
                bot.send_message(message.from_user.id, other_incorrect.format(section_correct, theme_correct))
                return
            article_id = db.add_article(article[3].strip(), article[4].strip(), other=section_correct)
            if not article_id:
                bot.send_message(message.from_user.id, article_duplicate)
                return
            db.add_relation_to_article(None, theme_correct, article_id, other=True)
            bot.send_message(message.from_user.id, download_success)
        else:
            authors = [(author.replace('#', '')).strip() for author in article[0].split(' ')]
            themes = [(theme.replace('#', '')).strip() for theme in article[1].split(', ')]
            author_correct = db.check_author_or_section(authors)       # return type <list> like [1, 2, 3]
            theme_correct = db.check_theme(themes)          # return type <list> like [<int>,...]
            if not author_correct or not theme_correct:
                bot.send_message(message.from_user.id, stand_incorrect.format(author_correct, theme_correct))
                return
            article_id = db.add_article(article[2].strip(), article[3].strip())   # get id of a article type <int>
            if not article_id:
                bot.send_message(message.from_user.id, article_duplicate)
                return
            db.add_relation_to_article(author_correct, theme_correct, article_id)   # set many to many relationship
            bot.send_message(message.from_user.id, download_success)


@bot.message_handler(commands=['downloadtheme'])
def download_theme(message: telebot.types.Message):
    if check_admin(message):
        theme_name = (message.text[15:].replace('#', '')).strip()
        if theme_name == '':
            bot.send_message(message.from_user.id, 'Вы не ввели тему!')
        else:
            result = db.add_theme(theme_name)
            if not result:
                bot.send_message(message.from_user.id, 'Данная тема уже существует!')
                return
            bot.send_message(
                message.from_user.id, 'Тема *{}* успешно добавленна!'.format(theme_name), parse_mode='markdown')


@bot.message_handler(commands=['addcourse'])
def add_course(message: telebot.types.Message):
    if check_admin(message):
        text = (message.text[10:]).split('|')
        result = db.add_course(text[0].strip(), text[1].strip())
        if result:
            bot.send_message(message.from_user.id, 'Курс успешно добавлен!')
            return
        bot.send_message(message.from_user.id, 'Во время добавления курса возникла ошибка!')


@bot.message_handler(commands=['userscount'])
def count_handler(message: telebot.types.Message):
    if check_admin(message):
        count = db.get_user_count()
        text = 'На данный момент ботом пользуются {} человек'.format(count)
        bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['lastarticle'])
def get_last_article(message: telebot.types.Message):
    if check_admin(message):
        article = db.get_last_article()
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))
# *********************************************************************************************


# *********** Back to main menu (Article by author, Article by theme, All articles, etc) ***********
@bot.message_handler(func=lambda message: message.text == first_level_back)
def back_to_main_menu(message: telebot.types.Message):
    s.change_state(message.from_user.id, state['st'])
    bot.send_message(message.from_user.id, main_message, parse_mode='markdown', reply_markup=get_markup(main_menu))
# *********************************************************************************************


# *************************************** Get by state ***************************************
@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['at']))
def author_list_articles(message: telebot.types.Message):
    article_by(message, state['ac'], 'author', back_to_author, author_mes)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['ac']))
def get_article_author(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_author)
    else:
        article_choice(message, back_to_author, author_handler)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['th']))
def theme_list_articles(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        article_by(message, state['tc'], 'theme', back_to_theme, theme_mes)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['tc']))
def get_article_theme(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_theme)
    else:
        article_choice(message, back_to_theme, theme_handler)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['al']))
def all_list_articles(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        article = db.get_article(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(article[0], article[1]))


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['ot']))
def get_other_article(message: telebot.types.Message):
    article_by(message, state['oc'], 'other', back_to_other, other_mes)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['oc']))
def get_other_choice(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, back_to_other)
    else:
        article_choice(message, back_to_other, other_articles_handler)


@bot.message_handler(func=lambda message: s.check_section(message.from_user.id, state['cr']))
def get_choice_course(message: telebot.types.Message):
    if message.text == 'Далее' or message.text == 'Назад':
        next_back(message, first_level_back)
    else:
        course = db.get_course(message.text)
        bot.send_message(message.from_user.id, '{} - {}'.format(course[0], course[1]))
# ********************************************************************************************


# ************************************* Section handlers *************************************
@bot.message_handler(func=lambda x: x.text == 'По авторам')
def author_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_author_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('author'), first_level_back))
    s.change_state(message.from_user.id, state['at'])


@bot.message_handler(func=lambda x: x.text == 'По темам')
def theme_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_theme_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('theme'), first_level_back))
    s.change_state(message.from_user.id, state['th'], '0:20')


@bot.message_handler(func=lambda x: x.text == 'Я сам выберу! Покажите все статьи')
def all_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_all_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_articles('all'), first_level_back))
    s.change_state(message.from_user.id, state['al'], '0:20')


@bot.message_handler(func=lambda x: x.text == 'Other. Гости, интервью, и многое другое')
def other_articles_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_other_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('other_content'), first_level_back))
    s.change_state(message.from_user.id, state['ot'])


@bot.message_handler(func=lambda x: x.text == 'Курсы по разработке')
def courses_handler(message: telebot.types.Message):
    bot.send_message(message.from_user.id, hello_courses_mes, parse_mode='markdown',
                     reply_markup=pre_modified_button(db.get_info_by_choice('courses'), first_level_back))
    s.change_state(message.from_user.id, state['cr'])
# ********************************************************************************************


# ************************************ Bot start function *************************************
def bot_start(webhook_data: dict, use_webhook: bool, logging_enable: bool):
    """
    :param webhook_data: data for deploy type <dict>
    :param use_webhook: type <bool>
    :param logging_enable: type <bool>
    :return: bot object
    """
    global bot

    def set_webhook(url, cert):
        try:
            bot.set_webhook(url=url, certificate=cert)
        except Exception as err:
            logger_bot.warning(err.with_traceback(None))
            raise Exception('Error for setting bot web hooks')

    def args_check(args_names, checking_kwargs):
        for arg in args_names:
            if checking_kwargs.get(arg) is None:
                return False
        return True

    if logging_enable:
        telebot.logger.setLevel(logging.WARNING)
        telebot.logger.addHandler(log.__file_handler('./logs/bot.log', log.__get_formatter()))

    if not use_webhook:
        return bot
    elif args_check(['webhook_ip', 'webhook_port', 'token', 'ssl_cert'], webhook_data):
        bot.remove_webhook()
        sleep(1)
        set_webhook(
            f"https://{webhook_data.get('webhook_ip')}:{webhook_data.get('webhook_port')}/{webhook_data.get('token')}/",
            open(webhook_data.get('ssl_cert'), 'r'))
        return bot
    else:
        logger_bot.warning('Params for start with webhook is not specified')
        raise Exception('Params for start with webhook is not specified')
