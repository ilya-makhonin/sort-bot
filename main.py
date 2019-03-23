import telebot
import bot
import flask
from config import *
import log
from states import states as s
from time import sleep
import threading


logger_main = log.logger('main', './logs/main.log', 'WARNING')


def update_states(timeout=43200):
    """
    This function is updating states of users
    :param timeout: type <int> - how often update states of users in db
    :return: nothing
    """
    try:
        while True:
            sleep(timeout)
            s.get_cache_instance().update_cache()
    except Exception as err:
        logger_main.warning(err.with_traceback(None))
        print(err)


def flask_init(bot_object):
    webhook_app = flask.Flask(__name__)

    @webhook_app.route('/', methods=['GET', 'HEAD'])
    def index():
        return ''

    @webhook_app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot_object.process_new_updates([update])
            return ''
        else:
            logger_main.warning('Abort 403')
            flask.abort(403)
    return webhook_app


def start_server(use_webhook: bool, logging_enable: bool, **webhook_data):
    try:
        bot_ = bot.bot_start(webhook_data, use_webhook, logging_enable)
        if use_webhook:
            server = flask_init(bot_)
            server.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, ssl_context=(SSL_SERT, SSL_POM))
        else:
            bot_.remove_webhook()
            sleep(1)
            bot_.polling(none_stop=True)
    except Exception as err:
        logger_main.warning('bot crashed')
        logger_main.warning(err.with_traceback(None))


def main(use_webhook=False, with_cache=False, logging_enable=True):
    """
    if with_cache equal True - create and start a new Thread - thread. Then the app will be running
    """
    if with_cache:
        thread = threading.Thread(target=update_states, args=[])
        thread.setDaemon(True)
        thread.start()
    start_server(
        use_webhook,
        logging_enable,
        webhook_ip=WEBHOOK_HOST,
        webhook_port=WEBHOOK_PORT,
        token=token,
        ssl_cert=SSL_SERT)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        logger_main.warning(error.with_traceback(None))
        print(error)
