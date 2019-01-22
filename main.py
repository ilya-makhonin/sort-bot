import telebot
import bot
import flask
from config import *
import log


def flask_init(bot_object):
    webhook_app = flask.Flask(__name__)
    webhook_logger = webhook_app.logger
    # webhook_logger.setLevel(log.LEVELS.get('WARNING'))
    webhook_logger.addHandler(log.__file_handler('./logs/flask.log', log.__get_formatter()))

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
            webhook_logger.warning('Abort 403')
            flask.abort(403)
    return webhook_app


def start(use_webhook=False, **webhook_data):
    logger = log.logger('main', './logs/main.log', 'WARNING')
    try:
        bot_object = bot.bot_start(webhook_data=webhook_data, use_webhook=use_webhook, logging_enable=True)
        if use_webhook:
            server = flask_init(bot_object)
            return server
        return None
    except Exception as err:
        logger.exception('bot crashed')
        logger.exception(err)


app = start(use_webhook=True, webhook_ip=WEBHOOK_HOST, webhook_port=WEBHOOK_PORT, token=token, ssl_cert=SSL_SERT)

if __name__ == '__main__':
    app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, ssl_context=(SSL_SERT, SSL_POM))
