from connect import get_connection
import csv

def create_table():
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50),
        phone VARCHAR(20) NOT NULL UNIQUE
    );
    """
    
    conn = get_connection() 
    if conn is not None:
        try:
            cursor = conn.cursor()       
            cursor.execute(sql_create_table) 
            conn.commit()               
            cursor.close()               
            print("Таблица 'contacts' успешно создана или уже существует!")
        except Exception as error:
            print("Ошибка при создании таблицы:", error)
        finally:
            conn.close()                 

def create_db_functions():
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Читаем и выполняем functions.sql
            with open('functions.sql', 'r', encoding='utf-8') as f:
                cursor.execute(f.read())
                
            # Читаем и выполняем procedures.sql
            with open('procedures.sql', 'r', encoding='utf-8') as f:
                cursor.execute(f.read())
                
            conn.commit()
            cursor.close()
            print("SQL-скрипты из файлов успешно загружены в базу!")
        except Exception as error:
            print("Ошибка при загрузке SQL-файлов:", error)
        finally:
            conn.close()



def insert_contact(first_name, last_name, phone):
    sql_call = "CALL upsert_contact(%s, %s, %s);"
    
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (first_name, last_name, phone))
            conn.commit()
            cursor.close()
            print(f"Контакт {first_name} успешно добавлен или обновлен!")
        except Exception as error:
            print("Ошибка при добавлении/обновлении контакта:", error)
        finally:
            conn.close()

def insert_from_csv(filename):
    sql_call = "SELECT * FROM insert_many_contacts(%s::VARCHAR[], %s::VARCHAR[], %s::VARCHAR[]);"
    
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_names, last_names, phones = [], [], []
            
            import csv
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовки
                for row in reader:
                    first_names.append(row[0].strip())
                    last_names.append(row[1].strip())
                    phones.append(row[2].strip())
            
            cursor.execute(sql_call, (first_names, last_names, phones))
            
            bad_data = cursor.fetchall()
            conn.commit()
            
            print(f"\n--- Отчет по файлу {filename} ---")
            if bad_data:
                print("ВНИМАНИЕ! Эти контакты НЕ добавлены (ошибка валидации):")
                for bad in bad_data:
                    print(f"Имя: {bad[0]} | Тел: {bad[1]} | Ошибка: {bad[2]}")
                print("Остальные контакты успешно загружены.")
            else:
                print("Все контакты успешно добавлены без ошибок!")
            print("----------------------------------\n")
                
            cursor.close()
        except Exception as error:
            print("Ошибка при массовой загрузке:", error)
        finally:
            conn.close()


def query_contacts(search_term=""):
    sql_query = "SELECT * FROM search_contacts(%s);"
    
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (search_term,))
            
            rows = cursor.fetchall() 
            
            print(f"\n--- Результаты поиска по '{search_term}' ---")
            if not rows:
                print("Ничего не найдено.")
            else:
                print(f"{'ID':<5} | {'Имя и Фамилия':<25} | {'Телефон':<17}")
                print("-" * 53)
                for row in rows:
                    full_name = f"{row[1]} {row[2] or ''}".strip()
                    print(f"{row[0]:<5} | {full_name:<25} | {row[3]:<17}")
            print("-" * 53 + "\n")
            
            cursor.close()
        except Exception as error:
            print("Ошибка при поиске:", error)
        finally:
            conn.close()


def update_contact(old_phone, new_first_name, new_phone):
    sql_update = """
    UPDATE contacts
    SET first_name = %s, phone = %s
    WHERE phone = %s;
    """
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_update, (new_first_name, new_phone, old_phone))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Контакт с номером {old_phone} успешно обновлен!")
            else:
                print(f"Контакт с номером {old_phone} не найден.")
                
            cursor.close()
        except Exception as error:
            print("Ошибка при обновлении:", error)
        finally:
            conn.close()

def delete_contact(identifier):
    sql_call = "CALL delete_contact_proc(%s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (identifier,))
            conn.commit()
            print(f"Команда на удаление '{identifier}' отправлена в базу.")
            cursor.close()
        except Exception as error:
            print("Ошибка при удалении:", error)
        finally:
            conn.close()

def query_contacts_paginated(limit, offset):
    sql_call = "SELECT * FROM get_contacts_paginated(%s, %s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (limit, offset))
            rows = cursor.fetchall()
            
            print(f"\n--- Страница контактов (Лимит: {limit}, Пропущено: {offset}) ---")
            if not rows:
                print("На этой странице пусто.")
            else:
                print(f"{'ID':<5} | {'Имя и Фамилия':<25} | {'Телефон':<17}")
                print("-" * 53)
                for row in rows:
                    full_name = f"{row[1]} {row[2] or ''}".strip()
                    print(f"{row[0]:<5} | {full_name:<25} | {row[3]:<17}")
            print("-" * 53 + "\n")
            cursor.close()
        except Exception as error:
            print("Ошибка при получении страницы:", error)
        finally:
            conn.close()


def main_menu():
    """Главное интерактивное меню приложения"""
    while True:
        print("\n=== ТЕЛЕФОННАЯ КНИГА ===")
        print("1. Добавить контакт вручную")
        print("2. Загрузить контакты из CSV")
        print("3. Найти/Показать контакты")
        print("4. Обновить контакт")
        print("5. Удалить контакт")
        print("6. Показать контакты по страницам (Пагинация)")
        print("0. Выйти")
        print("========================")
        
        choice = input("Выберите действие (0-5): ")
        
        if choice == '1':
            print("\n-- Добавление нового контакта --")
            first_name = input("Введите имя (обязательно): ").strip()
            if not first_name:
                print("Имя не может быть пустым!")
                continue
                
            last_name = input("Введите фамилию (можно пропустить): ").strip()
            phone = input("Введите номер телефона (обязательно): ").strip()
            if not phone:
                print("Номер телефона не может быть пустым!")
                continue
                
            insert_contact(first_name, last_name, phone)
            
        elif choice == '2':
            print("\n-- Загрузка из CSV --")
            filename = input("Введите имя файла (по умолчанию contacts.csv): ").strip()
            if not filename:
                filename = 'contacts.csv'
            insert_from_csv(filename)
            
        elif choice == '3':
            print("\n-- Поиск контактов --")
            search_term = input("Введите имя или телефон для поиска (или нажмите Enter, чтобы показать всех): ").strip()
            query_contacts(search_term)
            
        elif choice == '4':
            print("\n-- Обновление контакта --")
            old_phone = input("Введите ТЕКУЩИЙ номер телефона контакта: ").strip()
            new_name = input("Введите НОВОЕ имя: ").strip()
            new_phone = input("Введите НОВЫЙ номер телефона: ").strip()
            
            if old_phone and new_name and new_phone:
                update_contact(old_phone, new_name, new_phone)
            else:
                print("Ошибка: Все поля должны быть заполнены!")
                
        elif choice == '5':
            print("\n-- Удаление контакта --")
            identifier = input("Введите Имя или Номер телефона для удаления: ").strip()
            if identifier:
                delete_contact(identifier)
            else:
                print("Ошибка: Вы ничего не ввели!")

        elif choice == '6':
            print("\n-- Пагинация --")
            try:
                limit = int(input("Сколько контактов показать на одной странице? "))
                offset = int(input("Сколько контактов пропустить с начала? (offset) "))
                query_contacts_paginated(limit, offset)
            except ValueError:
                print("Ошибка: нужно вводить числа!")
                
        elif choice == '0':
            print("\nВыход из программы. До свидания!")
            break  
            
        else:
            print("\nНеверный ввод. Пожалуйста, выберите цифру от 0 до 5.")


if __name__ == '__main__':
    create_table()
    create_db_functions()
    main_menu()
