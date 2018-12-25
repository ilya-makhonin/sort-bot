from sql import sql_method as db


# Cash for speed (don't realize)
cash = {
    'author': None,
    'theme': None,
    'level': None
}


def get_db_information():
    cash['author'] = db.get_info_by_choice('author')
    cash['theme'] = db.get_info_by_choice('theme')
    cash['level'] = db.get_info_by_choice('level')
# ******************************
