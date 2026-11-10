import psycopg2
from config import DB_CONFIG

def get_connection():
    """Эта функция создает подключение и отдает его другим файлам"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print("Ошибка при подключении:", error)
        return None


if __name__ == '__main__':
    test_conn = get_connection()
    if test_conn:
        print("Ура! Успешное подключение!")
        test_conn.close()