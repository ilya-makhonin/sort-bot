from flask import Flask, request
import telebot
from bot import bot
import os


def start_server():
    server = Flask(__name__)

    @server.route("/bot", methods=['POST'])
    def get_message():
        bot.process_new_updates(
            [telebot.types.Update.de_json(
                request.stream.read().decode("utf-8")
            )]
        )
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://fake-gena-bot.herokuapp.com/bot")
        return "?", 200

    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))


if __name__ == '__main__':
    start_server()
