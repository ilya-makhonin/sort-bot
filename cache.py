from sql import sql_method as db


class Cash:
    def __init__(self):
        self.cash = {
            'users': tuple,
            'author': tuple,
            'theme': tuple,
            'level': tuple
        }

    def get_db_information(self):
        self.cash['users'] = db.get_info_by_choice('users')
        self.cash['author'] = db.get_info_by_choice('author')
        self.cash['theme'] = db.get_info_by_choice('theme')
        self.cash['level'] = db.get_info_by_choice('level')


cash = Cash()
