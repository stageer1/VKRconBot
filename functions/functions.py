import re
import sqlite3 as sql
import json
import sys
import vk_api

config = json.load(open('config.json'))
token = config['token']
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

def remove_minecraft_color_codes(text):
    return re.sub(r"§[0-9a-fk-or]", "", text)

def check_empty_users(filename="data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    try:
        # Создание таблицы пользователей, если ее нет
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        level TEXT NOT NULL)
        ''')

        conn.commit()

        # Проверяем наличие super-пользователей
        cursor.execute("SELECT * FROM Users WHERE level = ?", ("super",))
        users = cursor.fetchall()

        if not users:
            print("В базе данных не зарегистрировано ни одного super-пользователя.")
            username = input("Введите VK-username для выдачи прав super-админа: ")

            try:
                id = vk.users.get(user_ids=username)[0]['id']
            except vk_api.exceptions.ApiError:
                print("Пользователь с таким username не найден. Перезапустите бота и введите другой VK-username.")
                sys.exit()

            # Проверяем, зарегистрирован ли этот пользователь
            cursor.execute("SELECT id FROM Users")
            all_users = cursor.fetchall()

            for user in all_users:
                if int(id) == user[0]:  # user[0] содержит tgid
                    print("Этот пользователь уже зарегистрирован. Перезапустите бота и введите другой VK-username")
                    sys.exit()

            # Добавляем нового пользователя с правами super-админа
            cursor.execute("INSERT INTO Users (id, level) VALUES (?, ?)", (int(id), "super"))
            conn.commit()

    finally:
        # Закрытие подключения в любом случае
        conn.close()

def check_user_in_db(id: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE id = ?", (id, ))
    data = cursor.fetchone()
    conn.close()

    return data if data else 0

def is_command_allowed(cmd: str, id: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = ?", (id,))
    data = cursor.fetchone()

    if data[1] == "super":
        return 1

    groups = json.load(open("groups.json", 'r'))
    try:
        group = groups[data[1]]
        cmd_list = cmd.split()
        allowed_commands = group["allowed_commands"]
        if '*' in allowed_commands:
            return 1
        if cmd_list[0] not in allowed_commands:
            return 0

        ban_words_for_command = group.get("ban_words_for_commands", {}).get(cmd_list[0], [])

        # Если в команде есть запрещённые слова — команда запрещена
        for word in cmd_list:
            if word in ban_words_for_command:
                return 0  # Команда содержит запрещённое слово

        # Если команда прошла все проверки, она разрешена
        return 1
    except IndexError:
        print(f"{id} в базе данных имеет группу {data[1]}, но в groups.json она не зарегистрирована!")
        return Exception
    finally:
        conn.close()

def register(id: int, level: str, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Users (id, level) VALUES (?, ?)", (id, level))
    conn.commit()
    conn.close()

def unregister(id: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def set_group(id: int, level: str, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("UPDATE Users SET level = ? WHERE id = ?", (level, id))
    conn.commit()
    conn.close()