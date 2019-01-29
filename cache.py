from sql import db


class Cache:
    def __init__(self, lazy_loading):
        self.cache_state = dict()
        self.lazy_loading = lazy_loading
        if len(self.cache_state.values()) == 0:
            self.get_state_from_db()

    def get_state_from_db(self):
        """
        This function loads states of users from db. It"s triggered when the class is initialized.
        :return: nothing
        """
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT user_id, state FROM users;')
                states = cursor.fetchall()
                self.cache_state = {state[0]: state[1] for state in states}
        finally:
            connection.close()

    def set_state_to_db(self):
        """
        This function updates the states of users in the database
        :return: nothing
        """
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
        """
        This function gets a user state by user id. If a user state isn't in the cache that's checking in db
        :param user_id: unique id of a users
        :return: a state of user
        """
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
        """
        This function is setting a new user state by user id. If lazy loading is disabled it updates a user state in db
        :param user_id: unique id of a users
        :param new_state: a new user state
        :return: nothing
        """
        self.cache_state.update({user_id: new_state})
        if not self.lazy_loading:
            db.change_state(new_state, user_id)

    def clear_cache(self):
        """
        This function clears the cache
        :return: nothing
        """
        self.cache_state.clear()

    def update_cache(self):
        """
        This function updates the cache.
        :return: nothing
        """
        self.set_state_to_db()
        self.clear_cache()
        self.get_state_from_db()


# Initial class instance with disabling lazy loading
cache = Cache(lazy_loading=False)
