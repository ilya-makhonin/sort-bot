import telebot
from bot import bot
import flask
from config import *
import log


def flask_init(bot_object):
    webhook_app = flask.Flask(__name__)
    webhook_logger = webhook_app.logger
    webhook_logger.setLevel(log.LEVELS.get('DEBUG'))
    webhook_logger.addHandler(log.__file_handler('flask.log', log.__get_formatter()))

    @webhook_app.route('/', methods=['GET', 'HEAD'])
    def index():
        return ''

    @webhook_app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot_object.process_new_updates([update])
            webhook_logger.debug('updates from webhook: ' + str(update))
            return ''
        else:
            flask.abort(403)

    return webhook_app


def start(use_webhook=False, **webhook_data):
    logger = log.logger('main', 'main.log')
    try:
        bot_object = bot.bot_start(use_webhook=use_webhook, webhook_data=webhook_data)
        if use_webhook:
            server_app = flask_init(bot_object)
            return server_app
    except Exception as err:
        logger.exception('bot crashed')
        logger.exception(err)


if __name__ == '__main__':
    app = start(
        use_webhook=True,
        webhook_ip=WEBHOOK_HOST,
        webhook_port=WEBHOOK_PORT,
        token=token,
        ssl_cert='ssl_cert'
    )
