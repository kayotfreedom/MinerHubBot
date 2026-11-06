import sqlite3

conn = sqlite3.connect('casedatabase.db')
print('База данных создана и подключена')

cursor = conn.cursor()

if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="obich"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obich (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            obich_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "obich" создана')
else:
    print('Выполнено подключение к таблице "obich".')
if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="redkiy"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redkiy (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            redkiy_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "redkiy" создана')
else:
    print('Выполнено подключение к таблице "redkiy".')
if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="mif"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mif (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            mif_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "mif" создана')
else:
    print('Выполнено подключение к таблице "mif".')
if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="predmetniy"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predmetniy (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            predmetniy_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "predmetniy" создана')
else:
    print('Выполнено подключение к таблице "predmetniy".')
if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="ekip"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ekip (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            ekip_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "ekip" создана')
else:
    print('Выполнено подключение к таблице "ekip".')
if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="uluch"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uluch (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            uluch_case INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "uluch" создана')
else:
    print('Выполнено подключение к таблице "uluch".')

conn.commit()
conn.close()
print('База данных успешно инициализирована.')

def add_case_user(user_id, username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO obich (id, username, obich_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    cursor.execute('INSERT INTO redkiy (id, username, redkiy_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    cursor.execute('INSERT INTO mif (id, username, mif_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    cursor.execute('INSERT INTO predmetniy (id, username, predmetniy_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    cursor.execute('INSERT INTO ekip (id, username, ekip_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    cursor.execute('INSERT INTO uluch (id, username, update_case) VALUES (?, ?, ?)',
                   (user_id, username, 0))
    conn.commit()
    conn.close()

def get_obich(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM obich WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_redkiy(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM redkiy WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_mif(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM mif WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_predmetniy(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM predmetniy WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_ekip(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ekip WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_uluch(user_id):
    conn = sqlite3.connect('casedatabase.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM uluch WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result