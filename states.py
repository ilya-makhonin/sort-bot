from sql import db
from cache import Cache
from log import logger


class States:
    def __init__(self, use_cache):
        self.use_cache = use_cache
        self.logger = logger('state', './logs/state.log', 'INFO')
        if use_cache:
            self.cache = Cache(use_cache)
        self.logger.info(f"Now param use_cache in Cache class instance is {self.use_cache}")

    def check_section(self, user_id, state):
        """
        :param user_id: user id type <int>
        :param state: checking state type <str>
        :return: type <bull> like True or False
        """
        if self.use_cache:
            section = self.cache.get_state(user_id)
        else:
            section = db.get_state(user_id)
        self.logger.info(f"Used check_section: use_cache - {self.use_cache}, section var - {section}")
        return section.split('-')[0] == state

    def get_full_state(self, user_id):
        """
        :param user_id: user id type <int>
        :return: user state type <list> like [section, start page, finish page, category]
        """
        if self.use_cache:
            state = self.cache.get_state(user_id).split('-')
        else:
            state = db.get_state(user_id).split('-')

        if len(state) == 1:
            return state
        if len(state) == 2:
            pages = state[1].split(':')
            return [state[0], int(pages[0]), int(pages[1])]
        pages = state[1].split(':')
        self.logger.info(f"Used get_full_state: use_cache - {self.use_cache}, "
                         f"return data - {[state[0], int(pages[0]), int(pages[1]), state[2]]}")
        return [state[0], int(pages[0]), int(pages[1]), state[2]]

    def change_state(self, user_id, section, pages=None, category=None):
        """
        :param user_id: user id type <int>
        :param section: section name type <str>
        :param pages: pages diapason type <str> like '0:20', step - 20
        :param category: category name type <str> like author name or theme
        """
        self.logger.info(f"Used change_state: use_cache - {self.use_cache}, "
                         f"input data - {user_id, section, pages, category}")
        if pages is None:
            if self.use_cache:
                self.cache.set_state(user_id, section)
                return
            db.change_state(section, user_id)
        elif category is None:
            if self.use_cache:
                self.cache.set_state(user_id, '{}-{}'.format(section, pages))
                return
            db.change_state('{}-{}'.format(section, pages), user_id)
        else:
            if self.use_cache:
                self.cache.set_state(user_id, '{}-{}-{}'.format(section, pages, category))
                return
            db.change_state('{}-{}-{}'.format(section, pages, category), user_id)

    def get_cache_instance(self):
        return self.cache


states = States(False)
