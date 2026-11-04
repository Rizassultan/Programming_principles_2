import psycopg2
import csv


# Настройки подключения к базе данных
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Qwpp1283*", 
    "host": "localhost"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# 1. Design table(s) for the PhoneBook
def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) UNIQUE NOT NULL
                );
            """)
            print("Таблица phonebook готова.")

# 2. Implement inserting data from a CSV file
def import_from_csv(filepath):
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    cur.execute("""
                        INSERT INTO phonebook (username, phone) 
                        VALUES (%s, %s) 
                        ON CONFLICT (phone) DO NOTHING;
                    """, (row[0], row[1]))
            print(f"Данные из {filepath} успешно импортированы.")

# 3. Implement inserting data entered from the console
def add_contact(username, phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO phonebook (username, phone) VALUES (%s, %s)",
                    (username, phone)
                )
                print(f"Контакт {username} добавлен.")
            except psycopg2.IntegrityError:
                print("Ошибка: Контакт с таким номером уже существует.")

# 4. Implement updating a contact's first name or phone number
def update_contact(contact_id, new_name=None, new_phone=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if new_name:
                cur.execute("UPDATE phonebook SET username = %s WHERE id = %s", (new_name, contact_id))
            if new_phone:
                cur.execute("UPDATE phonebook SET phone = %s WHERE id = %s", (new_phone, contact_id))
            print(f"Контакт ID {contact_id} обновлен.")

# 5. Implement querying contacts with different filters
def query_contacts(name_filter=None, phone_prefix=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT id, username, phone FROM phonebook WHERE 1=1"
            params = []
            
            if name_filter:
                query += " AND username ILIKE %s"
                params.append(f"%{name_filter}%")
                
            if phone_prefix:
                query += " AND phone LIKE %s"
                params.append(f"{phone_prefix}%")
                
            cur.execute(query, tuple(params))
            results = cur.fetchall()
            
            print(f"\n--- Результаты поиска (Найдено: {len(results)}) ---")
            for r in results:
                print(f"ID: {r[0]} | Имя: {r[1]} | Телефон: {r[2]}")
            return results

# 6. Implement deleting a contact by username or phone number
def delete_contact(username=None, phone=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if username:
                cur.execute("DELETE FROM phonebook WHERE username = %s", (username,))
                print(f"Контакты с именем '{username}' удалены.")
            elif phone:
                cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
                print(f"Контакт с телефоном '{phone}' удален.")
            else:
                print("Укажите имя или телефон для удаления.")

# Демонстрация работы приложения
if __name__ == "__main__":
    create_table()
    
    # 2. Импорт из CSV (убедитесь, что contacts.csv существует)
    try:
        import_from_csv('contacts.csv')
    except FileNotFoundError:
        print("Файл contacts.csv не найден, пропускаем импорт.")
        
    # 3. Ввод через консоль
    print("\nДобавление нового контакта:")
    new_user = input("Введите имя: ")
    new_phone = input("Введите телефон: ")
    add_contact(new_user, new_phone)
    
    # 5. Поиск контакта
    print("\nПоиск контактов, начинающихся на '+1555':")
    query_contacts(phone_prefix='+1555')
    
    # 4. Обновление (для примера обновим контакт с ID 1, если он существует)
    print("\nОбновление контакта с ID 1:")
    update_contact(1, new_name="Alice Updated")
    query_contacts(name_filter="Alice Updated")
    
    # 6. Удаление
    print("\nУдаление контакта:")
    delete_contact(phone=new_phone)