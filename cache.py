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
        # Temporary storage for states of users
        self.cache_state = dict()

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
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                for user, state in self.cache_state.items():
                    cursor.execute('UPDATE users SET state = %s WHERE user_id = %s', (state, user))
                connection.commit()
        except Exception as error:
            db.logger.error(error)
        finally:
            connection.close()

    def get_state(self, user_id):
        pass

    def set_state(self, user_id):
        pass
