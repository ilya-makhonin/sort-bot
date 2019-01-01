import pymysql
from config import *


class SqlMethods:
    def __init__(self):
        self.host = db_host
        self.user = db_user
        self.password = db_pass
        self.db = dn_name

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
                    cursor.execute('INSERT INTO `users` (user_id, username, name) VALUES (%s, %s, %s);',
                                   (user_id, username, name))
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
                sql = "SELECT * FROM {};".format(type_table)
                cursor.execute(sql)
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

    def add_article(self, name, link):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO articles (`name`, `url`) VALUES (%s, %s);', (name, link))
                connection.commit()
                cursor.execute('SELECT `id` FROM articles ORDER BY `id` DESC LIMIT 1;')
                return cursor.fetchone()[0]
        finally:
            connection.close()

    def check_author(self, author_arr):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                author_id = []
                for author in author_arr:
                    cursor.execute('SELECT `id` FROM author WHERE `name` = %s;', (author.capitalize(),))
                    result = cursor.fetchone()
                    if result is None:
                        continue
                    else:
                        author_id.append(result[0])
                if len(author_id) != len(author_arr):
                    return False
                else:
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
                for j in theme_arr:
                    for i in result:
                        if j.lower() == i[1].lower():
                            theme_id.append(i[0])
                if len(theme_id) != len(theme_arr):
                    return False
                else:
                    return theme_id
        finally:
            connection.close()

    def add_relation_to_article(self, author_id, theme_id, article_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
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


sql_method = SqlMethods()
