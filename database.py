import sqlite3

def recording(id):
    db = sqlite3.connect('data.db')
    sql = db.cursor()
    sql.execute("""CREATE TABLE IF NOT EXISTS users (
                                                id TEXT,
                                                step TEXT
                                                )""")

    sql.execute(f"SELECT id FROM users WHERE id = '{id}'")
    if sql.fetchone() is None:
        # Запись в базу данных
        sql.execute("INSERT INTO users VALUES (?, ?)", (id, "start"))
        db.commit()

def update(id, object, value):
    db = sqlite3.connect('data.db')
    sql = db.cursor()
    sql.execute(f"UPDATE users SET {object} = ? WHERE id = ?", (value, id))
    db.commit()

def read(id, object):
    db = sqlite3.connect('data.db')
    sql = db.cursor()
    for i in sql.execute(f"SELECT {object} FROM users WHERE id = ?", (id,)):
        return i[0]
    db.commit()
