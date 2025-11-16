import os
import time
import mysql.connector
from mysql.connector import errorcode

DB_HOST = os.getenv('MYSQL_HOST', 'mysql_db')
DB_USER = os.getenv('MYSQL_USER', 'django_user')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'django_pass')
DB_NAME = os.getenv('MYSQL_DATABASE', 'timetable')

print(f"Ожидание MySQL: {DB_HOST}:3306...")

for i in range(60):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=3
        )
        conn.close()
        print("MySQL готова!")
        break
    except Exception as e:
        print(f"Попытка {i+1}/60: {e}")
        time.sleep(2)
else:
    print("ОШИБКА: MySQL не доступна")
    exit(1)