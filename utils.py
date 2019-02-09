from telebot import types


def get_markup(buttons, rows=1):
    """
    :param buttons: buttons list type <list> like [button name, button name, ...]
    :param rows: rows width count
    :return: bot markup type '<telebot.types.ReplyKeyboardMarkup object at 0x000001819664CCF8>'
    """
    markup = types.ReplyKeyboardMarkup(True, False, row_width=rows)
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
