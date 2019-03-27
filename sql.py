import pymysql
from config import *
import log


class SqlMethods:
    def __init__(self):
        self.host = HOST
        self.user = USER
        self.password = PASS
        self.db = DB
        self.logger = log.logger('sql', 'sql.log', 'WARNING')

    def get_connection(self):
        connection = pymysql.connections.Connection(
            host=self.host, user=self.user, password=self.password, db=self.db, charset='utf8mb4')
        return connection

    def add_user(self, user_id, username, name):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
                if cursor.fetchone() is None:
                    if username is not None and len(username) > 35:
                        username = username[0:35]
                    if name is not None and len(name) > 100:
                        name = name[0:100]
                    cursor.execute('INSERT INTO `users` (user_id, username, name) VALUES (%s, %s, %s);',
                                   (user_id, username, name))
                else:
                    self.change_state('starting', user_id)
                connection.commit()
        finally:
            connection.close()

    def change_state(self, new_state, user_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('UPDATE users SET state = %s WHERE user_id = %s;', (new_state, user_id))
                connection.commit()
        finally:
            connection.close()

    def get_state(self, user_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT `state` FROM users WHERE user_id = %s;', (user_id,))
                return (cursor.fetchone())[0]
        finally:
            connection.close()

    def get_info_by_choice(self, type_table):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM {};".format(type_table))
                return cursor.fetchall()
        finally:
            connection.close()

    def get_articles(self, condition, flag=''):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                result = None
                if condition == 'author':
                    cursor.execute('SELECT articles.`name` FROM author_article '
                                   'JOIN author ON author_article.author_id = author.`id` '
                                   'JOIN articles ON author_article.article_id = articles.`id` '
                                   'WHERE author.`id` = (SELECT `id` FROM author WHERE `name` = %s);', (flag,))
                    result = cursor.fetchall()
                elif condition == 'theme':
                    cursor.execute('SELECT articles.`name` FROM theme_article '
                                   'JOIN theme ON theme_article.theme_id = theme.`id` '
                                   'JOIN articles ON theme_article.article_id = articles.`id` '
                                   'WHERE theme.`id` = (SELECT `id` FROM theme WHERE theme_name = %s);', (flag,))
                    result = cursor.fetchall()
                elif condition == 'all':
                    cursor.execute('SELECT `name` FROM articles;')
                    result = cursor.fetchall()
                elif condition == 'other':
                    cursor.execute('SELECT `name` FROM articles JOIN other_content ON '
                                   'other_content.`id` = articles.is_other WHERE other_content.`id` = ('
                                   'SELECT `id` FROM other_content WHERE content_type = %s);', flag)
                    result = cursor.fetchall()
                return result
        finally:
            connection.close()

    def get_article(self, name):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT `name`, `url` FROM articles WHERE `name` = %s;', (name,))
                return cursor.fetchone() or ['Упс!', 'Такой статьи не существует!']
        finally:
            connection.close()

    def get_last_article(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT `name`, `url` FROM articles ORDER BY id DESC LIMIT 1;')
                return cursor.fetchone() or ['Упс!', 'Такой статьи не существует!']
        finally:
            connection.close()

    def add_course(self, name, url):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO courses (`name`, `url`) VALUES (%s, %s);', (name, url))
                return True
        except Exception as error:
            self.logger.warning(error.with_traceback(None))
            return False
        finally:
            connection.close()

    def get_course(self, name):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT `name`, `url` FROM courses WHERE `name` = %s;', (name,))
                return cursor.fetchone() or ['Упс!', 'Такого курса не существует!']
        finally:
            connection.close()

    def add_article(self, name, link, other=''):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if other != '':
                    cursor.execute(
                        'INSERT INTO articles (`name`, `url`, `is_other`) VALUES (%s, %s, %s);', (name, link, other))
                else:
                    cursor.execute('INSERT INTO articles (`name`, `url`) VALUES (%s, %s);', (name, link))
                connection.commit()
                cursor.execute('SELECT `id` FROM articles ORDER BY `id` DESC LIMIT 1;')
                return cursor.fetchone()[0]
        except Exception as error:
            self.logger.warning(error)
            return False
        finally:
            connection.close()

    def check_author_or_section(self, data, other=False):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if other:
                    cursor.execute('SELECT `id`, content_type FROM other_content;')
                    sections = cursor.fetchall()
                    for section in sections:
                        if section[1].lower() == data.lower():
                            return section[0]
                    return False
                author_id = []
                for author in data:
                    cursor.execute('SELECT `id` FROM author WHERE `name` = %s;', (author.capitalize(),))
                    result = cursor.fetchone()
                    if result is None:
                        continue
                    author_id.append(result[0])
                if len(author_id) != len(data):
                    return False
                return author_id
        finally:
            connection.close()

    def check_theme(self, theme_arr):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                theme_id = []
                cursor.execute('SELECT `id`, theme_name FROM theme;')
                result = cursor.fetchall()
                for theme in theme_arr:
                    for theme_from_db in result:
                        if theme.lower() == theme_from_db[1].lower():
                            theme_id.append(theme_from_db[0])
                if len(theme_id) != len(theme_arr):
                    return False
                return theme_id
        finally:
            connection.close()

    def add_relation_to_article(self, author_id, theme_id, article_id, other=False):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                if not other:
                    for author in author_id:
                        cursor.execute(
                            'INSERT INTO author_article (author_id, article_id) VALUES (%s, %s)', (author, article_id))
                connection.commit()
                for theme in theme_id:
                    cursor.execute(
                        'INSERT INTO theme_article (theme_id, article_id) VALUES (%s, %s)', (theme, article_id))
                connection.commit()
        finally:
            connection.close()

    def add_theme(self, theme_name):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT theme_name FROM theme;')
                theme_list = cursor.fetchall()
                for theme in theme_list:
                    if theme[0].lower() == theme_name.lower():
                        return False
                cursor.execute('INSERT INTO theme (theme_name) VALUES (%s)', (theme_name,))
                connection.commit()
                cursor.execute('SELECT theme_name FROM theme ORDER BY `id` DESC LIMIT 1;')
                return cursor.fetchone()[0]
        finally:
            connection.close()

    def get_user_count(self):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(0) FROM users;')
                return cursor.fetchone()[0]
        finally:
            connection.close()


db = SqlMethods()
