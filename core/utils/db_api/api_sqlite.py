import sqlite3

# Путь к БД
path_to_db = 'core/data/database.db'


# Преобразование полученного списка в словарь
def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict


# Форматирование запроса с аргументами
def update_format_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())


# Форматирование запроса без аргументов
def update_format(sql, parameters: dict):
    if "XXX" not in sql:
        sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


# Добавление пользователя
def add_user(user_id, user_login, user_name, registration_date, name_city, translate_user_city, geo_id_city, lat_city,
             lng_city):
    with sqlite3.connect(path_to_db) as db:
        db.execute("INSERT INTO users_info"
                   "(user_id, user_login, user_name, registration_date,"
                   " number_selected_products)"
                   "VALUES (?, ?, ?, ?, ?)",
                   [user_id, user_login, user_name, registration_date, 0])
        db.execute("INSERT INTO users_favorites"
                   "(user_id, favourites_products)"
                   "VALUES (?, ?)",
                   [user_id, None])
        db.execute("INSERT INTO users_cities"
                   "(user_id, name_city, translate_user_city, geo_id_city, lat_city, lng_city)"
                   "VALUES (?, ?, ?, ?, ?, ?)",
                   [user_id, name_city, translate_user_city, geo_id_city, lat_city, lng_city])
        db.commit()


# Получение пользователя
def get_information(name_db, **kwargs):
    with sqlite3.connect(path_to_db) as db:
        db.row_factory = dict_factory
        sql = f"SELECT * FROM {name_db}"
        sql, parameters = update_format_args(sql, kwargs)
        return db.execute(sql, parameters).fetchone()


# Удаление пользователя
def delete_user(**kwargs):
    with sqlite3.connect(path_to_db) as db:
        db.row_factory = dict_factory
        sql = "DELETE FROM users_info"
        sql, parameters = update_format_args(sql, kwargs)
        db.execute(sql, parameters)
        db.commit()


# Редактирование пользователя
def update_information(name_db, user_id, **kwargs):
    with sqlite3.connect(path_to_db) as db:
        db.row_factory = dict_factory
        sql = f"UPDATE {name_db} SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        db.execute(sql + "WHERE user_id = ?", parameters)
        db.commit()


# Получение пользователей
def get_all_information(name_db, **kwargs):
    with sqlite3.connect(path_to_db) as db:
        db.row_factory = dict_factory
        sql = f"SELECT * FROM {name_db}"
        if kwargs:
            sql, parameters = update_format_args(sql, kwargs)
            return db.execute(sql, parameters).fetchall()
        else:
            return db.execute(sql).fetchall()


# Создание всех таблиц для БД
def create_bdx():
    with sqlite3.connect(path_to_db) as db:
        # Создание таблицы users_info
        db.execute("CREATE TABLE IF NOT EXISTS users_info ("
                   "increment INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "user_id INTEGER, user_login TEXT, user_name TEXT, "
                   "registration_date TEXT, number_selected_products INTEGER)")

        # Создание таблицы users_favorites
        db.execute("CREATE TABLE IF NOT EXISTS users_favorites ("
                   "increment INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "user_id INTEGER, favourites_products TEXT)")

        # Создание таблицы users_city
        db.execute("CREATE TABLE IF NOT EXISTS users_cities ("
                   "increment INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "user_id INTEGER, name_city TEXT, translate_user_city TEXT,"
                   "geo_id_city INTEGER, lat_city REAL, lng_city REAL)")

        print("Базы данных успешно обновлены!")
        db.commit()
