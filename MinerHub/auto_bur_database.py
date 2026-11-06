import sqlite3

conn = sqlite3.connect('auto_bur.db')
print('База данных создана и подключена')

cursor = conn.cursor()

if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="auto_bur"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto_bur (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            status_pokupki INTEGER DEFAULT 0,
            status_bura INTEGER DEFAULT 0,
            bagaj_uluch INTEGER DEFAULT 1,
            kol_vo_ruda_bur INTEGER DEFAULT 1,
            oil_uluch INTEGER DEFAULT 1,
            oil INTEGER DEFAULT 0,
            inv INTEGER DEFAULT 0,
            case_inv INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "auto_bur" создана')
else:
    print('Выполнено подключение к таблице "auto_bur".')

conn.commit()
conn.close()
print('База данных успешно инициализирована.')


def add_bur(user_id, username):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO auto_bur (id, username, status_pokupki, status_bura, inv, bagaj_uluch, kol_vo_ruda_bur, oil_uluch, oil) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (user_id, username, 0, 0, 0, 1, 1, 1, 0))
    conn.commit()
    conn.close()


# Чинила

def clear_status_bur(user_id, stars):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET status_bura = ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()

# Статусы и функции бура

def get_status_bur(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def add_status_pokupki(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET status_pokupki = status_pokupki + ? WHERE id = ?',
                   (1, user_id))
    conn.commit()
    conn.close()

def start_bur(user_id, stars):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET status_bura = status_bura + ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()

def stop_bur(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET status_bura = status_bura - ? WHERE id = ?',
                   (1, user_id))
    conn.commit()
    conn.close()

def get_status_pokupki_bur(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

# Топливо

def get_bur_oil(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def add_oil(user_id, stars):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET oil = oil + ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()

def minus_oil(user_id, stars):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET oil = oil - ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()
# Руда в буре

def add_ruda_bur(user_id, stars):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET inv = inv + ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()

# Кейсы в инвентаре бура


# Улучшения бура
#Улучшение багажа:

def get_bagaj_uluch(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

#Улучшение кол-во руды:
def get_kol_vo_ruda_uluch_bur(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result
#Улучшение топлива:

def get_oil_uluch(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def set_oil_uluch(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE auto_bur SET oil_uluch = oil_uluch + ? WHERE id = ?',
                   (stars, user_id))
    conn.commit()
    conn.close()
# Инвентарь бура

def get_inv(user_id):
    conn = sqlite3.connect('auto_bur.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM auto_bur WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result










