from sql import db


def check_section(user_id, state):
    """
    :param user_id: user id type <int>
    :param state: checking state type <str>
    :return: type <bull> like True or False
    """
    section = db.get_state(user_id)
    return section.split('-')[0] == state


def get_full_state(user_id):
    """
    :param user_id: user id type <int>
    :return: user state type <list> like [section, start page, finish page, category]
    """
    state = db.get_state(user_id).split('-')
    if len(state) == 1:
        return state
    if len(state) == 2:
        pages = state[1].split(':')
        return [state[0], int(pages[0]), int(pages[1])]
    pages = state[1].split(':')
    return [state[0], int(pages[0]), int(pages[1]), state[2]]


def change_state(user_id, section, pages=None, category=None):
    """
    :param user_id: user id type <int>
    :param section: section name type <str>
    :param pages: pages diapason type <str> like '0:20', step - 20
    :param category: category name type <str> like author name or theme
    """
    if pages is None:
        db.change_state(section, user_id)
    elif category is None:
        db.change_state('{}-{}'.format(section, pages), user_id)
    else:
        db.change_state('{}-{}-{}'.format(section, pages, category), user_id)
