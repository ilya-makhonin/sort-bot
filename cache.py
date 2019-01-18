from sql import db


class Cache:
    """
    Cache for bot. It is need for optimization. Cache don't use now
    """
    def __init__(self):
        self.cache = {
            'users': tuple,
            'author': tuple,
            'theme': tuple,
            'level': tuple
        }

    def get_db_information(self):
        self.cache['users'] = db.get_info_by_choice('users')
        self.cache['author'] = db.get_info_by_choice('author')
        self.cache['theme'] = db.get_info_by_choice('theme')
        self.cache['level'] = db.get_info_by_choice('level')
