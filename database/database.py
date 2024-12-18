import os
import sqlite3

# Настройка базы данных SQLite для хранения пользователей
if not os.path.exists("currency.db"):
    conn = sqlite3.connect("currency.db")
    cursor = conn.cursor()
    # Создаём таблицу, если её ещё нет
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
    conn.commit()
    conn.close()


