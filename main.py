import logging
import time
import telebot
from bot import bot
import flask
from config import *


def flask_init(bot_object):
    webhook_app = flask.Flask(__name__)
    webhook_logger = webhook_app.logger
    # webhook_logger.setLevel(log.levels.get('DEBUG'))
    # webhook_logger.addHandler(log.__file_handler('logs.log', log.__get_formater()))

    @webhook_app.route('/', methods=['GET', 'HEAD'])
    def index():
        return ''

    @webhook_app.route('token', methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot_object.process_new_updates([update])
            # webhook_logger.debug('updates from webhook: ' + str(update))
            return ''
        else:
            flask.abort(403)

    return webhook_app


def start(use_webhook=False, **webhook_data):
    # logger = log.logger('main', 'logs.log')
    try:

        bot_object = bot.bot_start(use_webhook=use_webhook, webhook_data=webhook_data)

        if use_webhook:
            server_app = flask_init(bot_object)
            return server_app

    except Exception as err:
        pass
        # logger.exception('bot crashed')
        #logger.exception(err)


if __name__ == '__main__':
    app = start(
        use_webhook=True,
        webhook_ip='194.32.77.67',
        webhook_port='webhook_port',
        token='token',
        ssl_cert='ssl_cert'
    )


"""
def create_server():
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)
    app = flask.Flask(__name__)

    @app.route('/', methods=['GET', 'HEAD'])
    def index():
        return ''

    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)
    return app


def start_server():
    app = create_server()
    bot.remove_webhook()
    time.sleep(0.1)
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)


if __name__ == '__main__':
    start_server()
"""
