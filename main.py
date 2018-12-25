import logging
import time
import telebot
from bot import bot
import flask
from config import *


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
