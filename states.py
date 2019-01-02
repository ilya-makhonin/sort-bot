from sql import sql_method as db


def check_section(user_id, state):
    section = db.get_state(user_id)
    return (section.split('-')[0]).strip() == state


def get_full_state(user_id):
    state = db.get_state(user_id).split('-')
    if len(state) == 1:
        return state[0].strip()
    if len(state) == 2:
        pages = state[1].split(':')
        return [state[0], int(pages[0].strip()), int(pages[1].strip())]
    pages = state[1].split(':')
    return [state[0], int(pages[0].strip()), int(pages[1].strip()), state[2]]


def change_state(user_id, section, pages=None, category=None):
    if pages is None:
        print(section)
        db.change_state(section, user_id)
    elif category is None:
        db.change_state('{}-{}'.format(section, pages), user_id)
    else:
        db.change_state('{}-{}-{}'.format(section, pages, category), user_id)
