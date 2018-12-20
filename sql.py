import pymysql


def get_connection():
    connection = pymysql.connections.Connection(
        host='localhost', user='root', password='123456',
        db='it_root_articles', charset='utf8mb4'
    )
    return connection


def get_author():
    connection = get_connection()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `users`;"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
    connection.close()


def get_articles(condition):
    pass


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

    connection = get_connection()
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
