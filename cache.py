from sql import db
import threading
import multiprocessing


class Cache:
    def __init__(self, lazy_loading):
        self.cache_state = dict()
        self.lazy_loading = lazy_loading
        if len(self.cache_state.values()) == 0:
            self.get_state_from_db()

    def get_state_from_db(self):
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT user_id, state FROM users;')
                states = cursor.fetchall()
                self.cache_state = {state[0]: state[1] for state in states}
        finally:
            connection.close()

    def set_state_to_db(self):
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                for user, state in self.cache_state.items():
                    cursor.execute('UPDATE users SET state = %s WHERE user_id = %s;', (state, user))
                connection.commit()
        except Exception as error:
            db.logger.error(error)
        finally:
            connection.close()

    def get_state(self, user_id):
        try:
            return self.cache_state[user_id]
        except KeyError:
            connection = db.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT state FROM users WHERE user_id = %s;', (user_id,))
                    new_state = cursor.fetchone()[0]
                    self.cache_state.update({user_id: new_state})
                    return new_state
            except TypeError as type_error:
                db.logger.error(type_error)
                return False
            finally:
                connection.close()

    def set_state(self, user_id, new_state):
        self.cache_state.update({user_id: new_state})
        if not self.lazy_loading:
            db.change_state(new_state, user_id)

    def clear_cache(self):
        self.cache_state.clear()

    def update_cache(self):
        if self.lazy_loading:
            self.set_state_to_db()
            self.clear_cache()
            self.get_state_from_db()
