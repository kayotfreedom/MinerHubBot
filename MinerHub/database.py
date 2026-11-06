import sqlite3

conn = sqlite3.connect('database.db')
print('База данных создана и подключена')

cursor = conn.cursor()



if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            donate REAL DEFAULT 0.0,
            count_refs INTEGER DEFAULT 0,
            referral_id INTEGER DEFAULT NULL,
            withdrawn REAL DEFAULT 0.0,
            level INTEGER DEFAULT 1
        )
    ''')
    print('Таблица "users" создана')
else:
    print('Выполнено подключение к таблице "users".')

if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="ruda"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ruda (
            user_id INTEGER PRIMARY KEY,
            ruda_zemlya INTEGER DEFAULT 0,
            cash REAL DEFAULT 0.0,
            kirka TEXT NOT NULL,
            ruda_stone INTEGER DEFAULT 0,
            ruda_iran INTEGER DEFAULT 0,
            vibor_ruda INTEGER DEFAULT 1,
            vsego_ruda INTEGER DEFAULT 0,
            vsego_dobito INTEGER DEFAULT 0
        )
    ''')
    print('Таблица "ruda" создана')
else:
    print('Выполнено подключение к таблице "ruda".')

if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="promocodes"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY,
            code TEXT NOT NULL UNIQUE,
            stars REAL NOT NULL,
            max_uses INTEGER NOT NULL,
            current_uses INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    print('Таблица "promocodes" создана')
else:
    print('Выполнено подключение к таблице "promocodes".')

if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="promocode_uses"').fetchone() is None:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocode_uses (
            id INTEGER PRIMARY KEY,
            promocode_id INTEGER,
            user_id INTEGER,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (promocode_id) REFERENCES promocodes(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(promocode_id, user_id)
        )
    ''')
    print('Таблица "promocode_uses" создана')
else:
    print('Выполнено подключение к таблице "promocode_uses".')
conn.commit()
conn.close()
print('База данных успешно инициализирована.')

def check_blocked_user(user_id, chat_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*) FROM blocked_users WHERE user_id=? AND chat_id=?;
            """,
            (user_id, chat_id),
        )

        result = cursor.fetchone()[0]
        return bool(result > 0)
    finally:
        conn.close()


def add_promocode(code, stars, max_uses):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO promocodes (code, stars, max_uses) VALUES (?, ?, ?)',
                       (code, stars, max_uses))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def use_promocode(code, user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        promo = cursor.execute('''
            SELECT * FROM promocodes 
            WHERE code = ? AND is_active = TRUE 
            AND current_uses < max_uses
        ''', (code,)).fetchone()

        if not promo:
            return False, "Промокод недействителен или закончились использования"

        used = cursor.execute('''
            SELECT 1 FROM promocode_uses 
            WHERE promocode_id = ? AND user_id = ?
        ''', (promo[0], user_id)).fetchone()

        if used:
            return False, "Вы уже использовали этот промокод"

        # Увеличиваем количество использований промокода
        cursor.execute('''
            UPDATE promocodes 
            SET current_uses = current_uses + 1 
            WHERE code = ?
        ''', (code,))

        # Записываем использование промокода
        cursor.execute('''
            INSERT INTO promocode_uses (promocode_id, user_id) 
            VALUES (?, ?)
        ''', (promo[0], user_id))

        # Начисляем звезды пользователю
        cursor.execute('''
            UPDATE users 
            SET stars = stars + ? 
            WHERE id = ?
        ''', (promo[2], user_id))

        conn.commit()
        return True, promo[2]  # Возвращаем True и количество начисленных звезд
    except Exception as e:
        conn.rollback()
        return False, f"❌ {str(e)}"
    finally:
        conn.close()


def deactivate_promocode(code):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE promocodes SET is_active = FALSE WHERE code = ?', (code,))
    conn.commit()
    conn.close()


def add_user(user_id, username, referral_id=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id, username, donate, count_refs, level, referral_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, username, 0.0, 0, 1, referral_id))
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return bool(result)


def increment_donate(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET donate = donate + ? WHERE id = ?', (stars, user_id))
    conn.commit()
    conn.close()


def deincrement_donate(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET donate = donate - ? WHERE id = ?', (stars, user_id))
    conn.commit()
    conn.close()


def get_user_zero_referrals():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users WHERE count_refs = 0').fetchall()
    conn.close()
    return result


def withdraw_stars(user_id, stars_to_withdraw):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET donate = donate - ?, withdrawn = withdrawn + ? WHERE id = ?',
                   (stars_to_withdraw, stars_to_withdraw, user_id))
    conn.commit()
    conn.close()


def increment_referrals(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET count_refs = count_refs + 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def get_user_count():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT COUNT(*) FROM users').fetchone()
    conn.close()
    return result[0] if result else 0


def get_total_withdrawn():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT SUM(withdrawn) FROM users').fetchone()
    conn.close()
    return result[0] if result else 0.0


def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result


def get_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users').fetchall()
    conn.close()
    return result

# Функции руды

def add_user2(user_id, kirka_nachal):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ruda (user_id, cash, kirka, vibor_ruda, vsego_ruda, vsego_dobito) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, 0.0, kirka_nachal, 1, 0, 0))
    conn.commit()
    conn.close()

def get_ruda(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def prod_ruda_zemlya(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_zemlya = ruda_zemlya - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def prod_ruda_stone(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_stone = ruda_stone - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def prod_ruda_iran(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_iran = ruda_iran - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def vsego_ruda(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vsego_ruda = vsego_ruda + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def set_vsego_dobito(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vsego_dobito = vsego_dobito + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def minus_vsego_dobito(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vsego_dobito = vsego_dobito - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def get_vsego_dobito(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def pop_cash(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET cash = cash + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def minus_cash(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET cash = cash - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def get_cash(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_vibor_ruda(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def set_vibor_ruda(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vibor_ruda = vibor_ruda + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def clear_vibor_ruda(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vibor_ruda = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_ruda_zemlya(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_ruda_stone(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_ruda_iran(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def get_vsego_ruda(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result

def minus_vsego(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET vsego_ruda = vsego_ruda - ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

#Добавление по рудам

def increment_ruda_zemlya(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_zemlya = ruda_zemlya + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def increment_ruda_stone(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_stone = ruda_stone + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

def increment_ruda_iran(user_id, stars):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET ruda_iran = ruda_iran + ? WHERE user_id = ?', (stars, user_id))
    conn.commit()
    conn.close()

#Руды выбор



#Уровень пользователя

def add_level(user_id, level):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET level = level + ? WHERE id = ?', (level, user_id))
    conn.commit()
    conn.close()

def get_level(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return result

#Кирка

def delete_kirka(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET kirka = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def set_kirka(user_id, kirka):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ruda SET kirka = kirka + ? WHERE user_id = ?', (kirka, user_id))
    conn.commit()
    conn.close()

def get_kirka(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT * FROM ruda WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return result