from sql import db
import threading
import multiprocessing


class Cache:
    """
    Cache for bot. It is need for optimization. Cache don't use now
    I will need to add functions for work with users state
    users: [ id: { name: <str>, state: <str>, ... }, ...] or users: { id: state }
    Will add multiprocessing or threading for download cache data to DB (three times a day)
    """
    def __init__(self):
        self.cache = {
            'users': tuple,
            'author': tuple,
            'theme': tuple,
            'level': tuple
        }
        # Temporary storage for states of users
        self.cache_state = dict

    def get_db_information(self):
        self.cache['users'] = db.get_info_by_choice('users')
        self.cache['author'] = db.get_info_by_choice('author')
        self.cache['theme'] = db.get_info_by_choice('theme')
        self.cache['level'] = db.get_info_by_choice('level')

    def get_state_from_db(self):
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT user_id, state FROM users;')
                states = cursor.fetchall()
                cache_state = {state[0]: state[1] for state in states}
                self.cache_state = cache_state
                del cache_state
        finally:
            connection.close()

    def set_state_to_db(self):
        pass

    def get_state(self, user_id):
        pass

    def set_state(self, user_id):
        pass
