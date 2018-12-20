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
                sql = "INSERT INTO `users` (user_id, username, name) VALUES (%s, %s, %s);"
                cursor.execute(sql, (user_id, username, name))
                connection.commit()
        finally:
            connection.close()

    def change_state(self, new_state, user_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET state = %s WHERE user_id = %s;"
                cursor.execute(sql, (new_state, user_id))
                connection.commit()
        finally:
            connection.close()

    def get_user_state(self, user_id):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT state FROM users WHERE user_id = %s;"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
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

    def get_articles(self, condition):
        pass


sql_method = SqlMethods()


# *****************************************************************************************************

def inserting(table, data_array):
    '''
    :param table: type <str> table name in data base
    :param data_array: type <arr> like [{...}, {...}, {...}]
    :keyword table='users' => data_array like [{id: <int>, username: <str>, name: <str>}]
    :keyword table='theme' => data_array like [{theme: <str>}]
    :keyword table='author' => data_array like [{id: <int>, name: <str>}]
    :keyword table='level' => data_array like [{level_type: <str>}]
    :keyword table='articles' => data_array like [{name: <str>, url: <str>, theme: <int>, level: <int>, author: <int>}]
    '''

    connection = pymysql.connections.Connection(
        host='localhost', user='root', password='123456', db='it_root_articles', charset='utf8mb4'
    )

    try:
        with connection.cursor() as cur:
            if table == 'users':
                for data_obj in data_array:
                    sql = "INSERT INTO `users` (user_id, username, name) VALUES (%s, %s, %s);"
                    cur.execute(sql, (data_obj['id'], data_obj['username'], data_obj['name']))
                connection.commit()

            elif table == 'theme':
                for data_obj in data_array:
                    sql = "INSERT INTO `theme` (theme_name) VALUES (%s);"
                    cur.execute(sql, (data_obj['theme'],))
                connection.commit()

            elif table == 'author':
                for data_obj in data_array:
                    sql = "INSERT INTO `author` (author_id, name) VALUES (%s, %s);"
                    cur.execute(sql, (data_obj['id'], data_obj['name']))
                connection.commit()

            elif table == 'level':
                for data_obj in data_array:
                    sql = "INSERT INTO `level` (level_type) VALUES (%s);"
                    cur.execute(sql, (data_obj['level_type'],))
                connection.commit()

            elif table == 'articles':
                for data_obj in data_array:
                    sql = "INSERT INTO `articles` (name, url, theme, level, author) VALUES (%s, %s, %s, %s, %s);"
                    cur.execute(
                        sql, 
                        (data_obj['name'], data_obj['url'], data_obj['theme'], data_obj['level'], data_obj['author'])
                    )
                connection.commit()
    finally:
        connection.close()
