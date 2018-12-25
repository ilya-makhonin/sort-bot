import pymysql


class SqlMethods:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '123456'
        self.db = 'it_root_articles'

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
                return cursor.fetchone()
        finally:
            connection.close()


sql_method = SqlMethods()
